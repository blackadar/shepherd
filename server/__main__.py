"""
Runs the Shepherd server serv-ice.
"""
from server.net.broker import Broker
from server.net.collector import Collector
from server.processor import ConsoleProcessor
from server.plot.dash_processor import DashProcessor
from server.db.mysql_processor import MySQLProcessor

import server.constants as const


def main():
    broker = Broker(const.DB_URL, const.DB_PORT, const.DB_USER, const.DB_PASSWORD, const.DB_SCHEMA)
    collector = Collector()
    collector.add_processor(ConsoleProcessor())
    # collector.add_processor(DashProcessor())
    collector.add_processor(MySQLProcessor(const.DB_URL, const.DB_PORT, const.DB_USER, const.DB_PASSWORD, const.DB_SCHEMA))


if __name__ == '__main__':
    main()
