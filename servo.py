from threading import Thread
from time import time, sleep

from math import tanh

from pubsub import CallbackListener, get_listener, Topics, Ports, Delta


class Servo(Thread):

    def __init__(self, timeout: float = 20.0, **kwargs) -> None:
        Thread.__init__(self, **kwargs)

        self.timeout = timeout
        self.last_update = time()

        try:
            from PCA9685 import PCA9685
            self.pwm = PCA9685()
            self.pwm.setPWMFreq(50)
        except:
            self.pwm = None

        self.turn: float = 90
        self.tilt: float = 50

        self.current_turn: float = self.turn
        self.current_tilt: float = self.tilt

        print('init servo')

        self.history = []
        self.max_history = 1

        listener = get_listener(Ports.servo, [Topics.servo])
        self.callback_thread = CallbackListener(listener, self.handler, daemon=True)

    def handler(self, topic, message):
        if topic == Topics.servo:
            delta = Delta.parse_raw(message)
            self.turn += delta.dx
            self.tilt += delta.dy
            self.normalize()
            print("received servo", self.turn, self.tilt)
        else:
            print("failed", topic)

    def normalize(self):
        self.turn = max(0., min(self.turn, 180.))
        self.tilt = max(0., min(self.tilt, 180.))
        self.current_turn = max(0., min(self.current_turn, 180.))
        self.current_tilt = max(0., min(self.current_tilt, 180.))

    def apply(self):
        self.pwm_start()
        self.normalize()
        self.pwm and self.pwm.setRotationAngle(0, self.current_tilt)
        self.pwm and self.pwm.setRotationAngle(1, self.current_turn)

    def pwm_stop(self):
        self.pwm and self.pwm.exit_PCA9685()

    def pwm_start(self):
        self.pwm and self.pwm.start_PCA9685()
        self.pwm and self.pwm.setPWMFreq(50)

    def append_history(self, dx, dy):
        self.history.append((dx, dy))
        self.history = self.history[-self.max_history:]

    def average_history(self):
        dx, dy = 0, 0
        for x, y in self.history:
            dx, dy = dx + x, dy + y

        if self.history:
            dx, dy = dx / len(self.history), dy / len(self.history)

        return dx, dy

    def run(self):
        while True:
            self.normalize()

            travel_speed = 1.5

            change = False
            if round(self.current_turn) != round(self.turn):
                self.current_turn += travel_speed if self.turn > self.current_turn else -travel_speed
                change = True

            if round(self.current_tilt) != round(self.tilt):
                self.current_tilt += travel_speed if self.tilt > self.current_tilt else -travel_speed
                change = True

            if change:
                self.apply()
                self.last_update = time()
            elif time() - self.last_update > self.timeout:
                print("stop")
                self.pwm_stop()
                self.last_update = time()

            sleep(0.030)

    def __delete__(self, instance):
        self.pwm_stop()


if __name__ == '__main__':
    servo = Servo()
    servo.start()
