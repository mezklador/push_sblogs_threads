import logging as Log
import logging.config
import os

from tools.config import API_LOGS, LOG_CONFIGFILE

def Logger(where="", name=None):
    dests = where.split('/')
    aws_logfile = os.path.join(API_LOGS,
                               dests[0],
                               dests[1])
    logging.config.fileConfig(LOG_CONFIGFILE,
                              defaults={'logfilename': aws_logfile})
    if name is None:
        name = dests[0]
    return Log.getLogger(name)
