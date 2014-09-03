""" functions for logging and printing info """
import json
import logging
import logging.config
import os
import sys
from . import const

def start_logger(options):
    """ start the logger """
    config = {
        'version'                  : 1,
        'disable_existing_loggers' : False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s - %(message)s'
            },
            'mimimal': {
                'format': '%(message)s'
            }
        },
        'handlers': {
            'log_file_handler': {
                'class'        : 'logging.handlers.RotatingFileHandler',
                'level'        : 'DEBUG',
                'formatter'    : 'detailed',
                'filename'     : 'panzer.log',
                'maxBytes'     : 10485760,
                'backupCount'  : 5,
                'encoding'     : const.ENCODING
            },
            'console': {
                'class'      : 'logging.StreamHandler',
                'level'      : 'INFO',
                'formatter'  : 'mimimal',
                'stream'     : 'ext://sys.stderr'
            }
        },
        'loggers': {
            __name__: {
                'handlers'   : ['console', 'log_file_handler'],
                'level'      : 'DEBUG',
                'propagate'  : True
            }
        }
    }
    # - check debug flag
    if not options['panzer']['debug']:
        config['loggers'][__name__]['handlers'].remove('log_file_handler')
        del config['handlers']['log_file_handler']
        # - set verbosity level
        verbosity = ['CRITICAL', 'WARNING', 'INFO']
        index = options['panzer'].get('verbose', 1)
        try:
            verbosity_level = verbosity[index]
        except IndexError:
            print('ERROR: Unknown setting for ---verbose. '
                  'Setting ---verbose 2.', file=sys.stderr)
            verbosity_level = 'INFO'
        config['handlers']['console']['level'] = verbosity_level
        # - send configuration to logger
        logging.config.dictConfig(config)
        log('DEBUG', 'panzer', '>>>>> panzer starts <<<<<')
        log('DEBUG', 'panzer', pretty_lined('OPTIONS'))
        log('DEBUG', 'panzer', pretty_json_dump(options))

def log(level_str, sender, message):
    """ send a log message """
    my_logger = logging.getLogger(__name__)
    # - lookup table for internal strings to logging levels
    levels = {
        'CRITICAL' : logging.CRITICAL,
        'ERROR'    : logging.ERROR,
        'WARNING'  : logging.WARNING,
        'INFO'     : logging.INFO,
        'DEBUG'    : logging.DEBUG,
        'NOTSET'   : logging.NOTSET
    }
    # - lookup table for internal strings to pretty output strings
    pretty_levels = {
        'CRITICAL' : 'FATAL:   ',
        'ERROR'    : 'ERROR:   ',
        'WARNING'  : 'WARNING: ',
        'INFO'     : '         ',
        'DEBUG'    : '         ',
        'NOTSET'   : '         '
    }
    message = str(message)
    sender_str = ''
    message_str = ''
    level = levels.get(level_str, levels['ERROR'])
    # -- level
    pretty_level_str = pretty_levels.get(level_str, pretty_levels['ERROR'])
    # -- sender - right justify name if less than 8 chars long
    if sender != 'panzer':
        sender_str = sender + ': '
    # -- message
    message_str = message
    output = ''
    output += pretty_level_str
    output += sender_str
    output += message_str
    my_logger.log(level, output)

def log_stderr(stderr, sender=str()):
    """ send a log from external executable """
    # 1. check for blank input
    if not stderr:
        # - nothing to do
        return
    # 2. get a string with sender's name
    if sender:
        # - remove file extension from sender's name if present
        sender = os.path.splitext(sender)[0]
    # 3. now handle the messages sent by sender
    # - split the input (based on newlines) into list of json strings
    for line in stderr.split('\n'):
        if not line:
            # - skip blank lines: no valid json or message to decode
            continue
        incoming = dict()
        try:
            incoming = json.loads(line)
        except ValueError:
            # - if json cannot be decoded, just log as ERROR prefixed by '!'
            log('DEBUG',
                'panzer',
                'failed to decode json message from %s: "%s"' % (sender, line))
            incoming = [{'error_msg': {'level': 'ERROR',
                                       'message': '!' + line}}]
        for item in incoming:
            level = item['error_msg']['level']
            message = item['error_msg']['message']
            log(level, sender, message)

def pretty_keys(dictionary):
    """ return pretty printed list of dictionary keys, num per line """
    if not dictionary:
        return []
    # - number of keys printed per line
    num = 5
    # - turn into sorted list
    keys = list(dictionary.keys())
    keys.sort()
    # - fill with blank elements to width num
    missing = num - (len(keys) % num)
    keys.extend([''] * missing)
    # - turn into 2D matrix
    matrix = [[keys[i+j] for i in range(0, num)]
              for j in range(0, len(keys), num)]
    # - calculate max width for each column
    len_matrix = [[len(col) for col in row] for row in matrix]
    max_len_col = [max([row[j] for row in len_matrix])
                   for j in range(0, num)]
    # - pad with spaces
    matrix = [[row[j].ljust(max_len_col[j]) for j in range(0, num)]
              for row in matrix]
    # - return list of lines to print
    matrix = ["    ".join(row) for row in matrix]
    return matrix

def pretty_list(input_list):
    """ return pretty printed list """
    output = '    %s' % ", ".join(input_list)
    return output

def pretty_json_dump(json_data):
    """ return pretty printed json_data """
    return json.dumps(json_data, sort_keys=True, indent=1)

def pretty_lined(title):
    """ return pretty printed title """
    output = '-' * 20 + title + '-' * 20
    return output
