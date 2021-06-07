"""
Defines a Metric ABC (Interface).
"""
import abc


class Metric(abc.ABC):
    """
    Forces an interface to be available, which a data collector/producer will query.
    """

    @abc.abstractmethod(property)
    def metric_name(self) -> str:
        """
        Define or Return a str identifier.
        Does not need to be unique.
        :return: str
        """
        pass

    @abc.abstractmethod(classmethod)
    def measure(self) -> dict:
        """
        Measure all promised metrics.
        Return as dict (key, value pairs).
        Raise a ValueError if the measurement is not successful.
        :raises: ValueError
        :return: dict
        """
        pass
