"""
Abstract classes
"""

from abc import ABCMeta
from abc import abstractmethod

class ESSender(object):
    """
    Declares the interface that should be implemented by a ES sender
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstractmethod
    def send(self, csv_reader):
        """
        Sends the csv doc to ES
        """
        raise NotImplementedError

