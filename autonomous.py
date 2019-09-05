from threading import Thread
from time import time
from typing import List

from messages import DetectionPacket, DetectionPosition, Delta
from pubsub import Topics, Services, CallbackListener, TopicNames


class Autonomous(Thread):

    def __init__(self, autonomous_timeout: float = 1.0, run=True, **kwargs) -> None:
        Thread.__init__(self, **kwargs)
        self.autonomous_timeout = autonomous_timeout
        self.last_detect = time()
        self.last_id = None

        self.publisher = Topics.start_service(Services.autonomous)
        listener = Topics.start_listener(TopicNames.detection)
        self.worker = CallbackListener(listener, self.handler, daemon=False)
        if run:
            self.start()

    def handler(self, topic, message):
        if topic == TopicNames.detection:
            detection: DetectionPacket = message
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
            print('auto tracking %.2f %.2f -> [%.2f %.2f]' % (dx, dy, tilt, turn))
            self.last_detect = time()

            packet = Delta(dx=turn, dy=tilt, time=time())
            self.publisher[TopicNames.servo](packet)


if __name__ == '__main__':
    Autonomous()
