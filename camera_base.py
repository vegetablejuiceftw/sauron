from threading import Thread
from time import sleep


class Camera(Thread):
    def __init__(self, **kwargs) -> None:
        Thread.__init__(self, **kwargs)
        self.grabber = None
        self.raw = None

    def step(self):
        raise NotImplemented

    def run(self):
        while True:
            self.step()
            sleep(0.016)
