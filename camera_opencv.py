import cv2 as cv
import numpy as np

from camera_base import Camera
from shared import get_image_publisher


class CameraOpenCV(Camera):

    def __init__(self, index: int = 0, half_broadcast: bool = False, cap_fps: int = 59, run=True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.grabber = cv.VideoCapture(index)
        self.grabber.set(cv.CAP_PROP_FPS, cap_fps)
        print("FPS:", self.grabber.get(cv.CAP_PROP_FPS))

        frame = self.grabber.read()[1]
        half = cv.resize(frame, (0, 0), fx=0.5, fy=0.5)
        self.shape = frame.shape
        self.shape_half = half.shape

        self.raw = get_image_publisher("shm://camera", self.shape, np.uint8)
        self.raw_half = get_image_publisher("shm://camera-half", self.shape_half, np.uint8)
        self.half_broadcast = half_broadcast

        if run:
            self.start()

    def step(self):
        self.grabber.read(self.raw)
        if self.half_broadcast:
            self.raw_half[:] = cv.resize(self.raw, (0, 0), fx=0.5, fy=0.5)


if __name__ == '__main__':
    camera_worker = CameraOpenCV()
