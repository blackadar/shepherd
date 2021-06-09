"""
Defines a Subscriber ABC (Interface).
"""
import abc


class Subscriber(abc.ABC):
    """
    Forces an interface to be available, which a data producer will call with an update.
    """
    @abc.abstractmethod(abc.abstractproperty)
    def subscriber_name(self) -> str:
        """
        Define or Return a str identifier.
        Does not need to be unique.
        :return: str
        """
        pass

    @abc.abstractmethod(abc.abstractclassmethod)
    def update(self, update: dict) -> None:
        """
        Receive an update from the data source.
        :param update:
        :return:
        """
        pass


class ConsoleSubscriber(Subscriber):
    """
    Prints all updates to the console.
    """

    def subscriber_name(self) -> str:
        return "console"

    def update(self, update: dict) -> None:
        print(f"Update: {update}", flush=True)
