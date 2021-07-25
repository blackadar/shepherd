import sqlalchemy as sa
from sqlalchemy import desc
from sqlalchemy.orm import Session
from threading import Lock
import pandas as pd
from server.db.mappings import Update, AnomalyRecord


class ShepherdConnection:
    """
    Establishes and maintains a connection to the Shepherd database.
    Facilitates gathering data based on a Node ID, live or historical.
    """

    def __init__(self, host: str, port: int, user: str, password: str, dbname: str):
        """
        Sets up the Shepherd connection.
        :param host:
        :param port:
        :param user:
        :param password:
        :param dbname:
        """
        # Create DB Session
        print("Connecting to Database...")
        engine = sa.create_engine(f"mysql://{user}:{password}@{host}:{port}/"
                                  f"{dbname}", echo=False)
        self.session = Session(engine)
        print("Database connected.")
        self.lock = Lock()

    def get_updates(self, node_id: int, num_updates: int):
        """
        Retrieves most num_updates recent Update objects for Node node_id.
        :param node_id: int Node ID
        :param num_updates: int # Updates to fetch, most n recent
        :return: pd.DataFrame
        """
        with self.lock:
            query = self.session.query(Update).filter(Update.node_id == node_id).order_by(desc(Update.timestamp)).limit(num_updates)
            return pd.read_sql(query.statement, query.session.bind)

    def get_anomalies(self):
        """
        Retrieves all unresolved Anomalies
        :return: pd.DataFrame
        """
        with self.lock:
            query = self.session.query(AnomalyRecord).filter(AnomalyRecord.resolved == 0)
            return pd.read_sql(query.statement, query.session.bind)

    def get_nodes(self):
        """
        Gets all Node IDs with Update records.
        :return: list of ints
        """
        with self.lock:
            nodes = self.session.query(Update.node_id).distinct()
            return [node[0] for node in nodes]
