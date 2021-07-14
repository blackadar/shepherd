"""
Runs the Shepherd server serv-ice.
"""
from server.net.broker import Broker
from server.net.collector import Collector
from server.processor import ConsoleProcessor
from server.plot.dash_processor import DashProcessor
from server.db.mysql_processor import MySQLProcessor


def main():
    broker = Broker('localhost', 3306, 'user', 'password', 'schema')
    collector = Collector()
    collector.add_processor(ConsoleProcessor())
    # collector.add_processor(DashProcessor())
    collector.add_processor(MySQLProcessor('localhost', 3306, 'user', 'password', 'schema'))


if __name__ == '__main__':
    main()
