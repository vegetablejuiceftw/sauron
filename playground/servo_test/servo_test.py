import time
import RPi.GPIO as GPIO
from PCA9685 import PCA9685


pwm = PCA9685()
pwm.setPWMFreq(50)

tilt = lambda x: pwm.setRotationAngle(0, x)
turn = lambda x: pwm.setRotationAngle(1, x)


def main():
    while True:
        for i in range(0, 180, 1):
            turn(i)
            if i < 80:
                tilt(i)
            time.sleep(0.001)

        for i in range(180, 0, -1):
            turn(i)
            if i < 80:
                tilt(i)
            time.sleep(0.001)


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print(e)
        print("Exiting the servo test")

    # stop the servo power
    pwm.exit_PCA9685()
    GPIO.cleanup()
