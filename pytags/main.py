"""
Entry point of the app. Handles command line arguments
"""
import sys
import getopt
import csv
import json
import string
import logging

import packages # pylint: disable=unused-import
from packages.interfaces.BankStatementParser import BankStatementParser
from packages.interfaces.ESSender import ESSender

def print_help(logger):
    """
    Prints the help text of the app
    """

    logger.info('Usage:')
    logger.info('tags.py -h | --help')
    logger.info('tags.py <command> -i | --input_file <cvs_bank_statement>')
    logger.info(' command:')
    logger.info('     -a, --analyse Convert the input and update tags.json file')
    logger.info('     -s, --send Analyse and send the data to Elasticsearch')

def on_analyse_command(logger, input_file_path):
    """
    Steps for the analyse command
    """
    logger.info('Received "analyse" command')

    output_file_path = string.rsplit(input_file_path, '.', 1)[0]
    output_file_path = output_file_path + '_NEW_FORMAT.csv'

    logger.info('Ouput file is: %s', output_file_path)
    logger.info('Available parsers: %s', BankStatementParser.__subclasses__())

    tags_input_file_path = './tags.json'

    bank_statement_parser = None

    with open(input_file_path, 'rb') as input_file:
        csv_reader = csv.DictReader(input_file)

        for parser in BankStatementParser.__subclasses__():
            if parser.has_supported_header_hormat(csv_reader):
                bank_statement_parser = parser()
                logger.info('The file does have a supported format')
                break

        if bank_statement_parser:
            with open(output_file_path, 'wb') as output_file:
                csv_writer = csv.DictWriter(output_file,
                                            fieldnames=bank_statement_parser.get_header_format(),
                                            extrasaction='raise')

                with open(tags_input_file_path, 'r+') as tags_input_file:
                    json_input = json.load(tags_input_file)

                    try:
                        json_output = bank_statement_parser.analyse(csv_reader,
                                                                    json_input,
                                                                    csv_writer)

                        logger.info('"Analyse" command went smoothly!')

                        tags_input_file.seek(0)
                        tags_input_file.truncate()
                        json.dump(json_output, tags_input_file)
                    except Exception as ex:
                        logger.warning('Parser threw an exception: ' + str(ex))

def on_send_command(logger, input_file_path):
    """
    Steps for the send command
    """
    logger.info('Received "send" command')
    logger.info('Available ES senders: %s, choosing the first one!', ESSender.__subclasses__())

    es_sender = None
    if ESSender.__subclasses__():
        es_sender = ESSender.__subclasses__()[0]()
    else:
        logger.error('No ES sender found!')
        return

    with open(input_file_path, 'rb') as input_file:
        csv_reader = csv.DictReader(input_file)
        try:
            es_sender.send(csv_reader)
        except Exception as ex:
            logger.warning('ES sender threw an exception: ' + str(ex))

    logger.info('"Send" command went smoothly!')

def main(argv):
    """
    Entry point
    """

    logging.basicConfig(level=logging.INFO)
    main_logger = logging.getLogger(__name__)

    try:
        opts, _ = getopt.getopt(argv, "hasi:", ["help", "analyse", "send", "input_file="])
    except getopt.GetoptError:
        main_logger.error('Unsupported arguments!')
        print_help(main_logger)
        sys.exit(2)

    if not opts:
        main_logger.error('No arguments provided!')
        print_help(main_logger)
        sys.exit(2)

    command = ''

    for opt, arg in opts:
        if opt == '-h' or opt == '--help':
            print_help(main_logger)
            sys.exit()
        elif opt in ('-i', '--input_file'):
            input_file_path = arg.strip()
        elif opt in ('-a', '--analyse'):
            command = 'analyse'
        elif opt in ('-s', '--s'):
            command = 'send'
        else:
            main_logger.error('Unsupported arguments: %s', opt)
            print_help(main_logger)
            sys.exit(2)

    main_logger.info('Input file is: %s', input_file_path)
    main_logger.info('Command is: %s', command)

    if command == 'analyse':
        on_analyse_command(main_logger, input_file_path)
    elif command == 'send':
        on_send_command(main_logger, input_file_path)
    else:
        main_logger.error('Unsupported command: %s', command)

if __name__ == '__main__':
    main(sys.argv[1:])
