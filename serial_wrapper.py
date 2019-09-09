from typing import List, Dict

import serial.tools.list_ports
from serial.tools.list_ports_linux import SysFS


def matcher(name: str, p: SysFS) -> bool:
    hints = [
        p.product,
        p.manufacturer,
        p.hwid,
    ]

    for hint in hints:
        if hint and name.lower() in str(hint).lower():
            return True
    return False


def find_serial(name: str) -> dict:
    ports = serial.tools.list_ports.comports()
    result = dict((port.device, port) for port in ports if matcher(name, port))
    return result


def info(ports: Dict[str, SysFS]):
    for k, p in ports.items():
        print()
        print(p.device)
        print(p.name)
        print(p.description)
        print(p.hwid)
        print(p.vid)
        print(p.pid)
        print(p.serial_number)
        print(p.location)
        print(p.manufacturer)
        print(p.product)
        print(p.interface)


if __name__ == '__main__':
    print("start")
    info(find_serial(''))
