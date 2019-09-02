from threading import Thread
from time import time
from typing import List

import settings
from pubsub import CallbackListener, get_listener, Topics, Ports, Detection, DetectionPosition, get_server, Delta


class Autonomous(Thread):

    def __init__(self, autonomous_timeout: float = 1.0, **kwargs) -> None:
        Thread.__init__(self, **kwargs)
        self.autonomous_timeout = autonomous_timeout
        self.last_detect = time()
        self.last_id = None

        self.publisher = get_server(port=Ports.servo[1], topics=[Topics.servo])

    def handler(self, topic, message):
        if topic == Topics.detection:
            detection = Detection.parse_raw(message)
            print("received detection", len(detection.points))
            self.logic(detection.points)
        else:
            print("failed", topic)

    def logic(self, detection: List[DetectionPosition]):
        # we care only about the most most center point
        point_of_interest = detection[0] if detection else None
        time_elapsed = time() - self.last_detect

        if time_elapsed > self.autonomous_timeout and point_of_interest and point_of_interest.age > 5 and self.last_id != point_of_interest.id:
            self.last_id = point_of_interest.id
            dx, dy = point_of_interest.dx, point_of_interest.dy

            # incremental mode
            # smooth = 3
            # speed = 10
            # self.turn += tanh(dx / smooth) * speed
            # self.tilt -= tanh(dy / smooth) * speed

            # absolute mode
            tilt = -25 * dy
            turn = 50 * dx
            print()
            print('do autonomus %.2f %.2f -> [%.2f %.2f]' % (dx, dy, tilt, turn))
            self.last_detect = time()

            packet = Delta(dx=turn, dy=tilt, time=time())
            self.publisher[Topics.servo](packet)


if __name__ == '__main__':
    driver = Autonomous(autonomous_timeout=settings.AUTO_TRACK_INERVAL)
    listener = get_listener(Ports.detection, Topics.detection)
    CallbackListener(listener, driver.handler, daemon=False)
