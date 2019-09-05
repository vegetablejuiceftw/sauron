from importlib import import_module
from multiprocessing import Process
from typing import List
from argparse import ArgumentParser

import settings

parser = ArgumentParser()
parser.add_argument("-c", "--config", dest="config", default="default",
                    help="which launch configuration to load")
parser.add_argument("-m", "--mock", dest="mock", action="store_true", default=False,
                    help="no actual actuators are invoked (even if they exist)")
parser.add_argument("-n", "--nuke", dest="nuke", action="store_true", default=False,
                    help="nuke ros on exit")
parser.add_argument("-r", "--remote", dest="remote", action="store_true", default=False,
                    help="listen to remote")
args = parser.parse_args()


def load_launcher(node_descriptor):
    module_name, launch_name = node_descriptor.split(':')
    module = import_module(module_name)
    return getattr(module, launch_name, None)


class Launcher:
    def __init__(self) -> None:
        self.nodes: List[Process] = []

    def launch(self, descriptor=None, *args, **kwargs):
        target = load_launcher(descriptor)
        p = Process(target=target, args=args, name=descriptor, kwargs=kwargs)
        self.nodes.append(p)

        p.start()
        print(f'Started node {descriptor}')

    def spin(self):
        try:
            for process in reversed(self.nodes):
                process.join()
                process.terminate()
        except KeyboardInterrupt:
            print("\nKeyboard interrupt")

        for process in self.nodes:
            process.terminate()

        if args.nuke:
            nuke = f'pkill -f {__file__}'
            print("Nuking sauron", nuke)
            import os
            os.system(nuke)

        print("Game over!")


print("Config name:", args.config)
launcher = Launcher()

config = settings.CONFIG[args.config]

for node in config:
    launcher.launch(**node)

launcher.spin()
