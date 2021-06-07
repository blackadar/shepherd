"""
Runs the Node module on the target machine.
"""
from node.telemetry.subscriber import ConsoleSubscriber
from node.telemetry.heart import Heart
from node.telemetry.metrics.cpu import CPU


def main():
    """
    The work for the Node
    :return:
    """

    heart = Heart(0, 0, 1)
    debug = ConsoleSubscriber()
    heart.register_subscriber(debug)

    cpu = CPU()
    heart.register_metric(cpu)


if __name__ == '__main__':
    main()
