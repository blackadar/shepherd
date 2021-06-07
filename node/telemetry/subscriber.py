"""
Defines a Subscriber ABC (Interface).
"""
import abc


class Subscriber(abc.ABC):
    """
    Forces an interface to be available, which a data producer will call with an update.
    """
    @abc.abstractmethod(property)
    def subscriber_name(self) -> str:
        """
        Define or Return a str identifier.
        Does not need to be unique.
        :return: str
        """
        pass

    @abc.abstractmethod(classmethod)
    def update(self, update: dict) -> None:
        """
        Receive an update from the data source.
        :param update:
        :return:
        """
        pass
