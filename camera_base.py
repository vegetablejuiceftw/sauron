from threading import Thread
from time import sleep


class Camera(Thread):
    def __init__(self, run=True, mock=False, silent=False, camera_sleep=0.016, **kwargs) -> None:
        Thread.__init__(self, **kwargs)
        self.grabber = None
        self.raw = None
        self.camera_sleep = camera_sleep

    def step(self):
        raise NotImplemented

    def run(self):
        while True:
            self.step()
            sleep(self.camera_sleep)
