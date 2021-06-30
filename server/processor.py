"""
Defines an Interface for a Data Processor.
This interface will receive data updates from all Nodes, when the Collector receives them.
"""
import abc


class Processor(abc.ABC):
    """
    Guarantees the availability of the following for an implementation.
    Called by Collector with new data.
    """

    @abc.abstractmethod(abc.abstractproperty)
    def processor_name(self) -> str:
        """
        Define or Return a str identifier.
        Does not need to be unique.
        :return: str
        """
        pass

    @abc.abstractmethod(abc.abstractclassmethod)
    def update(self, pool_id: int, node_id: int, update: dict) -> None:
        """
        Receive an update from the data source.
        :param pool_id:
        :param node_id:
        :param update:
        :return:
        """
        pass


class ConsoleProcessor(Processor):
    """
    Prints all updates to the console.
    """

    def processor_name(self) -> str:
        return "console"

    def update(self, pool_id, node_id, update: dict) -> None:
        print(f"{pool_id}/{node_id}: {update}", flush=True)
