import logging
from time import sleep

import serial

from serial_wrapper import find_serial

logger = logging.getLogger("driver_arduino")


class Controller:
    def __init__(self, descriptor="arduino"):
        self.motor_serial = None
        self.descriptor = descriptor
        self.try_reconnect()

    def try_reconnect(self):
        if self.motor_serial:
            self.motor_serial.close()
        self.motor_serial = None
        while self.motor_serial is None:
            controller_serial = next(iter(find_serial(self.descriptor)), None)
            logger.info("Opening %s", controller_serial)

            if not controller_serial:
                logger.error('Reconnect serial device not found!')
                sleep(1)
                continue

            try:
                self.motor_serial = serial.Serial(
                    port=controller_serial,
                    baudrate=115200, timeout=0.01)
            except Exception as e:
                logger.error('Reconnect failed: %s', e)
                sleep(1)

    def set_angle(self, channel, angle):
        if not 0 <= angle <= 180:
            return

        channel = ['y', 'x'][channel]
        command = f"{angle}{channel}"

        try:
            self.motor_serial.write(command.encode("ascii"))
        except Exception as e:
            logger.error("Motors dead: %s", e)
            self.try_reconnect()

    def start(self):
        # not implemented
        pass

    def exit(self):
        # not implemented
        pass
