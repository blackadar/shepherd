"""
Runs the Shepherd server serv-ice.
"""
from server.net.broker import Broker
from server.net.collector import Collector


def main():
    broker = Broker()
    collector = Collector()


if __name__ == '__main__':
    main()
