from time import time
from typing import List

import cv2 as cv
import numpy as np

from face_dnn.dnn_detector import DNNProcessor
from haar_cascades import cascade_detector
from messages import DetectionPosition, DetectionPacket
from pubsub import Topics, Services, TopicNames
from shared import ImageSubscriber, get_image_publisher


class Detector:
    def __init__(self, zoom: float = 1.00, lower=[110, 50, 50], upper=[130, 255, 255], run=True, **kwargs) -> None:
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

        self.shape = None
        self.masked = None

        self.lower = lower
        self.upper = upper

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

        if image.shape != self.shape:
            self.shape = image.shape
            self.masked = get_image_publisher("shm://camera-masked", self.shape, np.uint8)

    def detect(self, frame, zoom) -> List[DetectionPosition]:
        # measure processing the lazy way
        start = time()
        # process frame
        original_height, original_width, *_channels = frame.shape
        frame = cv.resize(frame, (0, 0), fx=zoom, fy=zoom)

        frame = cv.GaussianBlur(frame, (5, 5), 0)
        hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)

        mask = cv.inRange(hsv, np.array(self.lower), np.array(self.upper))
        mask = cv.erode(mask, None, iterations=4)

        if self.shape:
            self.masked[:] = cv.bitwise_and(frame, frame, mask=mask)

        contours, hierarchy = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        points = [cv.boundingRect(cnt) for cnt in contours]

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
    detector = Detector()
