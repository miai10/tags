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

def print_help(logger):
    """
    Prints the help text of the app
    """

    logger.info('Usage:')
    logger.info('tags.py -h | --help')
    logger.info('tags.py <command> -i | --input_file <cvs_bank_statement>')
    logger.info(' command:')
    logger.info('     -a, --analyze Convert the input and update tags.json file')
    logger.info('     -s, --send Analyse and send the data to Elasticsearch')

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
    input_file = ''

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

    output_file_path = string.rsplit(input_file_path, '.', 1)[0]
    output_file_path = output_file_path + '_NEW_FORMAT.csv'

    tags_input_file_path = './tags.json'

    main_logger.info('Input file is: %s', input_file_path)
    main_logger.info('Ouput file is: %s', output_file_path)
    main_logger.info('Command is: %s', command)
    main_logger.info('Available parsers: %s', BankStatementParser.__subclasses__())

    bank_statement_parser = None

    with open(input_file_path, 'rb') as input_file:
        csv_reader = csv.DictReader(input_file)

        for parser in BankStatementParser.__subclasses__():
            if parser.has_supported_header_hormat(csv_reader):
                bank_statement_parser = parser()
                main_logger.info('The file does have supported format')
                break

        if bank_statement_parser:
            with open(output_file_path, 'wb') as output_file:
                csv_writer = csv.DictWriter(output_file,
                                            fieldnames=bank_statement_parser.get_header_format(),
                                            extrasaction='raise')

                with open(tags_input_file_path, 'r+') as tags_input_file:
                    json_input = json.load(tags_input_file)

                    if command == 'analyse':
                        try:
                            json_output = bank_statement_parser.analyse(csv_reader,
                                                                        json_input,
                                                                        csv_writer)
                        except Exception as ex:
                            main_logger.warning('Parser threw an exception: ' + str(ex))
                    else:
                        main_logger.error('"Send" command is not supported yet!')

                    tags_input_file.seek(0)
                    tags_input_file.truncate()
                    json.dump(json_output, tags_input_file)
                    main_logger.info('"Analyse" command went smoothly!')
        else:
            main_logger.error('The file does not have a supported format')

if __name__ == "__main__":
    main(sys.argv[1:])
