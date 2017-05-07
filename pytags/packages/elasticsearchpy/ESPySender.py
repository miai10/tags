"""
ES sender implemented with the help of elasticsearch-py lib
"""
import logging
from datetime import datetime
from elasticsearch import helpers, Elasticsearch

from ..interfaces import ESSender

class ESPySender(ESSender):
    """
    Implements the ES sender interface
    """

    def __init__(self):
        super(ESPySender, self).__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.es_client = Elasticsearch()

    def send(self, csv_reader):
        """
        Sends the csv doc to ES
        """
        actions = []
        for row in csv_reader:
            new_row = {}
            for item in row.viewitems():
                key, value = item
                if key == 'id':
                    new_row['_id'] = value
                elif key == 'timestamp':
                    new_row[key] = datetime.strptime(value, '%m-%d-%Y %I:%M%p')
                elif key == 'amount':
                    new_row[key] = float(value)
                else:
                    new_row[key] = value
            actions.append(new_row)

        helpers.bulk(self.es_client, actions, index='expenses2', doc_type='ING-csv')
