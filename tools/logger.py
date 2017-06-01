import logging
import logging.config
import os

from tools.config import API_LOGS, LOG_CONFIGFILE

def Logger(where=""):
    dests = where.split('/')
    aws_logfile = os.path.join(API_LOGS,
                               dests[0],
                               dests[1])
    logging.config.fileConfig(LOG_CONFIGFILE,
                              defaults={'logfilename': aws_logfile})
    return logging.getLogger(dests[0])
