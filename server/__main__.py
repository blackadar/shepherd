"""
Runs the Shepherd server serv-ice.
"""
from server.net.broker import Broker
from server.net.collector import Collector
from server.processor import ConsoleProcessor
from server.plot.dash_processor import DashProcessor


def main():
    broker = Broker()
    collector = Collector()
    collector.add_processor(ConsoleProcessor())
    collector.add_processor(DashProcessor())


if __name__ == '__main__':
    main()
