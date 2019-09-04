from gevent import monkey

from messages import DetectionPacket

monkey.patch_all(thread=False)

from time import sleep, time

import SharedArray as sa
import cv2 as cv
from flask import Flask, render_template, Response, request
import numpy as np

from pubsub import Delta, Topics, CallbackListener, Services, TopicNames

app = Flask(__name__, static_folder='./', static_url_path='', template_folder='./templates')

servo_pub = Topics.start_service(Services.web_server)
detection_queue = Topics.start_listener(TopicNames.detection)

detection_sub = CallbackListener(detection_queue, daemon=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    speed = 2.0
    tilt, turn = 0, 0
    if request.json:
        action = request.json['action']
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
        print(tilt, turn)

    return render_template('index.html')


def generator():
    frame = sa.attach("shm://camera")
    current = frame.copy()

    fails = 0

    while True:
        if not np.array_equal(current, frame):
            fails = 0
            current = frame.copy()
            last_detection: DetectionPacket = detection_sub.messages.get(TopicNames.detection)
            if last_detection:
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
        sleep(0.032 if fails < 5 else 1)


@app.route('/video')
def video_feed():
    if "camera" in [e.name.decode() for e in sa.list()]:
        return Response(generator(), mimetype='multipart/x-mixed-replace; boundary=frame')
    else:
        return Response('camera not online', 404)


if __name__ == '__main__':
    from gevent import pywsgi

    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
