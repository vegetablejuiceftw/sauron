from time import time
from typing import List

import cv2 as cv

from face_dnn.dnn_detector import DNNProcessor
from haar_cascades import cascade_detector
from messages import DetectionPosition, DetectionPacket
from pubsub import Topics, Services, TopicNames
from shared import ImageSubscriber


class Detector:
    def __init__(self, zoom: float = 1.00, run=True, **kwargs) -> None:
        self.kwargs = kwargs
        self.zoom = zoom
        self.raw = None
        self.image = None
        self.detection: dict = {}
        self.count = 0
        self.preserve = 0
        self.haar_processor = cascade_detector.CascadeProcessor(cascade_detector.Topics.face)
        self.dnn_processor = DNNProcessor()
        self.detection_pub = Topics.start_service(Services.detector)
        self.worker = ImageSubscriber('shm://camera', self.grab)

        if run:
            print("start detector")
            self.worker.start()

    def grab(self, image, ms):
        self.raw = image
        self.count += 1

        detection = self.detect(self.raw, self.zoom)

        if detection or self.preserve == 3:
            self.detection = detection
            self.preserve = 0
            self.detection_pub[TopicNames.detection](DetectionPacket(points=self.detection))
        else:
            self.preserve += 1

    def detect(self, frame, zoom) -> List[DetectionPosition]:
        # measure processing the lazy way
        start = time()
        # process frame
        original_height, original_width, *_channels = frame.shape
        frame = cv.resize(frame, (0, 0), fx=zoom, fy=zoom)

        dilation = 0.7

        # scan region of interest only, i.e last seen detection square
        if self.detection:
            # last seen object
            p = self.detection[0]

            # enlarge search area to account for moving between frames
            height, width, *_channels = frame.shape
            up = int(max(p.cy * zoom - (p.h * zoom * dilation), 0))
            down = int(min(p.cy * zoom + (p.h * zoom * dilation), height))
            left = int(max(p.cx * zoom - (p.w * zoom * dilation), 0))
            right = int(min(p.cx * zoom + (p.w * zoom * dilation), width))
            # cut the region of interest out
            frame_roi = frame[up:down, left:right]
            roi_height, roi_width, *_channels = frame_roi.shape

            # detect bounding boxes
            results = self.haar_processor.process(frame_roi, 1) or self.dnn_processor.process(frame_roi, 100)
            ms = (time() - start) * 1000

            # we need to transform detected positions to original image coordinates / zoom level
            for x, y, w, h in results:
                center_x, center_y = x + w // 2, y + h // 2

                # center shift in pixels
                delta_x, delta_y = int((roi_width // 2 - center_x) / zoom), int((roi_height // 2 - center_y) / zoom)

                return [
                    DetectionPosition(
                        x=p.x - delta_x,
                        y=p.y - delta_y,
                        w=int(w / zoom),
                        h=int(h / zoom),
                        sx=original_width, sy=original_height,
                        id=self.count,
                        pid=p.pid,
                        age=self.count - p.pid,
                        color=(255, 0, 255),
                        ms=ms,
                    ),
                    # box for detection area
                    DetectionPosition(
                        x=int(left / zoom),
                        y=int(up / zoom),
                        w=int((right - left) / zoom),
                        h=int((down - up) / zoom),
                        sx=original_width, sy=original_height,
                        id=self.count,
                        pid=p.pid,
                        age=self.count - p.pid,
                        color=(0, 255, 0),
                        ms=ms,
                    ),
                ]

        # haar detects candles and books as faces :(
        # points = self.haar_processor.process(frame, 0.5)

        points = self.dnn_processor.process(frame, 200)

        ms = (time() - start) * 1000

        position_results = [
            DetectionPosition(
                x=x, y=y, w=w, h=h,
                sx=original_width, sy=original_height,
                id=self.count, pid=self.count, age=0, color=(255, 0, 255), ms=ms,
            ).zoom(zoom)
            for x, y, w, h in points
        ]

        position_results.sort(key=lambda p: p.key)
        return position_results


if __name__ == '__main__':
    face_detector = Detector()

    # cap = cv.VideoCapture(0)
    # while cap.isOpened:
    #     ret, frame = cap.read()
    #
    #     if frame is None:
    #         continue
    #
    #     faces = face_detector.detect(frame, 1)
    #
    #     for face in faces:
    #         cv.rectangle(frame, (face.x, face.y), (face.x + face.w, face.y + face.h), face.color, 2)
    #         cv.putText(
    #             frame, '%d-%d   %.1f, %.1f' % (face.pid, face.age, face.dx, face.dy), (face.x, face.y - 8),
    #             cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv.LINE_AA,
    #         )
    #         cv.putText(
    #             frame, 'ms %d' % face.ms, (face.x + 4, face.y - 8 + face.h),
    #             cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1, cv.LINE_AA,
    #         )
    #
    #     cv.imshow('Capture - Face detection', frame)
    #
    #     if cv.waitKey(10) == 27:
    #         break
