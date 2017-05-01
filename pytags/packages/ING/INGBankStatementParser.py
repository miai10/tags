"""
ING implementation
"""
import string
import logging
from ..interfaces import BankStatementParser

class INGBankStatementParser(BankStatementParser):
    """
    ING implementation
    """
    newFormatHeader = ['id', 'timestamp', 'transaction', 'amount', 'partner', 'details']
    INGFormatHeader = ['Data', 'Detalii tranzactie', 'Debit', 'Credit']

    def __init__(self):
        super(INGBankStatementParser, self).__init__()

        self.logger = logging.getLogger(self.__class__.__name__)

    @classmethod
    def obtain_amount(cls, amount_string):
        """
        Returns the amount as float from the provided string
        """
        return float(string.replace(amount_string, ',', '.'))

    @classmethod
    def obtain_partner(cls, partner_string):
        """
        Returns the partener from the provided string
        """
        return string.split(partner_string, ':')[1]

    @classmethod
    def obtain_date(cls, date_string):
        """
        Returns the date from the provided string
        """
        date_split = string.split(string.split(string.split(date_string, ' ')[0], ':')[1], '-')
        return date_split[1] + '-' + date_split[0] + '-' + date_split[2]

    @classmethod
    def has_supported_header_hormat(cls, csv_reader):
        """
        Checks the header of the cvs object to see if is supported
        """
        return csv_reader.fieldnames == cls.INGFormatHeader

    @classmethod
    def get_header_format(cls):
        """
        Returns the header format
        """
        return cls.newFormatHeader

    def analyse(self, csv_reader, json_input, csv_writer):
        """
        Reads the input and conerts it to the new format
        """
        csv_writer.writeheader()

        new_rows_count = 1

        while True:
            try:
                row = csv_reader.next()
            except StopIteration:
                break

            new_row = dict()

            try:
                transaction_type = row['Detalii tranzactie']

                if transaction_type == 'Cumparare POS':
                    # Data                 ,Detalii tranzactie                         ,Debit      ,Credit
                    # 02 decembrie 2015    ,Cumparare POS                              ,"246,33"   ,
                    #                      ,Nr.card:42XXX3965                          ,           ,
                    #                      ,Terminal:AUCHAN                            ,           ,
                    #                      ,Data:29-11-2015 Autorizare: 495514         ,           ,

                    new_row['id'] = new_rows_count
                    new_row['transaction'] = transaction_type
                    new_row['amount'] = INGBankStatementParser.obtain_amount(row['Debit'])

                    new_row['details'] = csv_reader.next()['Detalii tranzactie']

                    row = csv_reader.next()
                    new_row['partner'] = INGBankStatementParser.obtain_partner(row['Detalii tranzactie'])
                    new_row['details'] += ' ' + row['Detalii tranzactie']

                    row = csv_reader.next()
                    new_row['timestamp'] = INGBankStatementParser.obtain_date(row['Detalii tranzactie']) + ' 10:0' + str(new_rows_count % 10) + 'AM'
                    new_row['details'] += ' ' + row['Detalii tranzactie']

                else:
                    self.logger.warning('Unknown transaction type, ignoring row: ' + str(row.items()))

            except Exception as ex:
                self.logger.warning('Exception caught: ' + str(ex))
                self.logger.warning('Exception around row: ' + str(row.items()))
                self.logger.warning('Ignoring partial composed new row:  after row: ' + str(new_row.items()))

            if new_row.items():
                self.logger.debug('Adding new row: ' + str(new_row.items()))
                csv_writer.writerow(new_row)
                new_rows_count += 1

        return json_input
