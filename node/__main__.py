"""
Runs the Node module on the target machine.
"""
from node.telemetry.subscriber import ConsoleSubscriber
from node.telemetry.heart import Heart
from node.telemetry.metrics.cpu import CPU
from node.telemetry.metrics.ram import RAM
from node.telemetry.metrics.disk import Disk


def main():
    """
    The work for the Node
    :return:
    """

    heart = Heart(0, 0, 0.5)
    debug = ConsoleSubscriber()
    heart.register_subscriber(debug)

    cpu = CPU()
    ram = RAM()
    disk = Disk()
    heart.register_metric(cpu)
    heart.register_metric(ram)
    heart.register_metric(disk)


if __name__ == '__main__':
    main()
