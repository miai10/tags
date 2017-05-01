"""
Abstract classes
"""
from abc import ABCMeta
from abc import abstractmethod

class BankStatementParser(object):
    """
    Declares the interface that should be implemented by a parser
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @classmethod
    def has_supported_header_hormat(cls, csv_reader):
        """
        Checks the header of the cvs object to see if is supported
        """
        raise NotImplementedError

    @classmethod
    def get_header_format(cls):
        """
        Returns the header format`
        """
        raise NotImplementedError

    @abstractmethod
    def analyse(self, csv_reader, json_input, csv_writer):
        """
        Reads the input and conerts it to the new format
        """
        raise NotImplementedError
