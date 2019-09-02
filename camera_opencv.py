import cv2 as cv
import numpy as np

import settings
from camera_base import Camera
from shared import get_image_publisher


class CameraOpenCV(Camera):

    def __init__(self, index: int = 0, half_broadcast: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grabber = cv.VideoCapture(index)
        print("FPS:", self.grabber.get(cv.CAP_PROP_FPS))
        frame = self.grabber.read()[1]
        half = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)
        self.shape = frame.shape
        self.shape_half = half.shape

        self.raw = get_image_publisher("shm://camera", self.shape, np.uint8)
        self.raw_half = get_image_publisher("shm://camera-half", self.shape_half, np.uint8)
        self.half_broadcast = half_broadcast

    def step(self):
        self.grabber.read(self.raw)
        if self.half_broadcast:
            self.raw_half[:] = cv.resize(self.raw, (0, 0), fx=0.5, fy=0.5)


if __name__ == '__main__':
    camera_worker = CameraOpenCV(half_broadcast=settings.HALF_CAMERA_BROADCAST)
    camera_worker.start()
