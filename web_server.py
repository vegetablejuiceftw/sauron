import asyncio
import uvicorn
from time import time
import SharedArray as sa
import cv2 as cv
import numpy as np

from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.responses import Response, StreamingResponse, JSONResponse
from starlette.templating import Jinja2Templates

from messages import DetectionPacket
from pubsub import Delta, Topics, CallbackListener, Services, TopicNames

templates = Jinja2Templates(directory='templates')

app = Starlette(debug=True)
app.mount('/static', StaticFiles(directory='static'), name='static')

servo_pub = None
frame_buffer = None


# TODO: replace this with websockets
@app.route('/servo', methods=['POST'])
async def servo(request):
    speed = 2.0
    tilt, turn = 0, 0
    json = await request.json()

    action = json['action']
    if action == 'up':
        tilt -= speed
    if action == 'down':
        tilt += speed
    if action == 'left':
        turn += speed
    if action == 'right':
        turn -= speed

    packet = Delta(dx=turn, dy=tilt, time=time())
    servo_pub[TopicNames.servo](packet)
    print(json, tilt, turn)
    return JSONResponse({})


@app.route('/')
async def homepage(request):
    template = "index.html"
    context = {"request": request}
    return templates.TemplateResponse(template, context)


async def generator(request):
    frame = sa.attach(frame_buffer)
    current = frame.copy()

    detection_queue = Topics.start_listener(TopicNames.detection)
    detection_sub = CallbackListener(detection_queue, daemon=True, run=True)

    fails = 0

    while True:
        # oh boy : D, web dev is so eezy
        # https://github.com/encode/starlette/pull/320
        # https://github.com/encode/starlette/issues/297
        # https://github.com/tiangolo/fastapi/issues/410
        if await request.is_disconnected():
            print("video stream disconnected : D")
            detection_sub.running = False
            break
        if not np.array_equal(current, frame):
            # print("frame")
            fails = 0
            current = frame.copy()
            if TopicNames.detection in detection_sub.messages:
                last_detection: DetectionPacket = detection_sub.messages[TopicNames.detection]

                for face in last_detection.points:
                    cv.rectangle(current, (face.x, face.y), (face.x + face.w, face.y + face.h), face.color, 2)
                    cv.putText(
                        current, '%d-%d   %.1f, %.1f' % (face.pid, face.age, face.dx, face.dy), (face.x, face.y - 8),
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv.LINE_AA,
                    )
                    cv.putText(
                        current, 'ms %d' % face.ms, (face.x + 4, face.y - 8 + face.h),
                        cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv.LINE_AA,
                    )
            ret, jpg = cv.imencode('.jpg', current, (cv.IMWRITE_JPEG_QUALITY, 60))
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpg.tostring() + b'\r\n')
        else:
            fails += 1
        await asyncio.sleep(0.032 if fails < 5 else 1)


@app.route('/video')
async def video_feed(request):
    if "camera" in [e.name.decode() for e in sa.list()]:
        return StreamingResponse(generator(request), media_type='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response('camera not online', 404)


def launch(*args, frame_buffer_name="shm://camera", workers=1, **kwargs):
    global servo_pub, frame_buffer

    frame_buffer = frame_buffer_name
    print("launching web server")
    servo_pub = Topics.start_service(Services.web_server)
    uvicorn.run(app, host='0.0.0.0', port=8000, workers=workers)


@app.on_event('shutdown')
def murder():
    print("Murder! :O")


if __name__ == '__main__':
    launch()
