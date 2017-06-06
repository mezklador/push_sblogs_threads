from datetime import datetime
import logging
import logging.config
import os
import re
import sys
from time import time

from tools.config import (
    LOGS_DIR,
    LOGFILE_URL
)
from tools.logger import Logger

from celery import Celery
from celery.decorators import periodic_task
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import requests

'''
aws_local_logfile = os.path.join(API_LOGS, 'downloads', 'timeline.log')
logging.config.fileConfig(LOG_CONFIGFILE,
                          defaults={'logfilename': aws_local_logfile})
logger = logging.getLogger(__name__)
'''
logger = Logger('downloads/timeline.log', name=__name__)
cel_logger = get_task_logger(__name__)

logs_filesize_list = []

app = Celery('dwn',
             broker='redis://localhost:6379/10',
             backend='redis://localhost:6379/10')
app.conf.timezone = 'Europe/Paris'

verbose = False


def check_logs_location():
    if not os.path.isdir(LOGS_DIR):
        os.makedirs(LOGS_DIR)

    return LOGS_DIR


def local_logs_files_parser():
    logs = os.listdir(LOGS_DIR)
    if len(logs) > 0:
        logs_filesize_list.append([os.stat(os.path.join(LOGS_DIR, log)).st_size
                                   for log in logs])
        return logs

    return None

# FROM: https://stackoverflow.com/questions/14270698/get-file-size-using-python-requests-while-only-getting-the-header#answer-44299915
# requests.get(url, stream=True).headers['Content-length'] -> getting filesize of the document


@periodic_task(run_every=crontab(minute='*/2'))
def main(url=LOGFILE_URL):
    '''
    Executed every 2 minutes by Celery
    :param url:
    :return:
    '''
    try:
        start = time()
        r = requests.get(url, stream=True)
        nu_filesize = len(r.content)

        # local_logs = check_logs_location()
        all_local_logs = local_logs_files_parser()

        if all_local_logs is not None:
            last_log = os.path.join(LOGS_DIR, all_local_logs[-1])
        else:
            last_log = False

        last_log_size = os.stat(last_log).st_size if last_log else 0

        if verbose:
            print(last_log)
            print(f"request file: {nu_filesize} vs. last "
                  f"log size: {last_log_size}")

        if nu_filesize > last_log_size or last_log_size < 1:
            if r.status_code != 200:
                msg = r.raise_for_status()
                logger.warning(f"Bad request: {msg}")
                cel_logger.warning(f"Bad request: {msg}")
                sys.exit(1)

            content_type = re.sub('[\s+]',
                                  '',
                                  r.headers['content-type']).split(';')[0]
            if content_type != 'text/plain':
                r.status_code = 500
                msg = r.raise_for_status()
                logger.warning(f"Server failure: {msg}")
                cel_logger.warning(f"Server failure: {msg}")
                sys.exit(1)

            now = datetime.now()

            filename_date = f"{now.year}{now.month:02d}{now.day:02d}-" \
                            f"{now.hour:02d}_{now.minute:02d}_" \
                            f"{now.second:02d}.log"

            with open(os.path.join(LOGS_DIR, filename_date), 'wb') as f:
                for data in r.iter_content(32 * 1024):
                    f.write(data)

            end = time() - start
            final_msg = f"GET: {filename_date}, for {end:04f} sec."
            logger.info(final_msg)
            cel_logger.info(final_msg)
            if verbose:
                print(final_msg)

            return final_msg

        return None

    except requests.exceptions.RequestException as e:
        err = f"Bad request: {e}"
        logger.warning(err)
        cel_logger.warning(err)
        sys.exit(1)

    except requests.exceptions.Timeout as tm:
        err = f"Request Timeout: {tm}"
        logger.warning(err)
        cel_logger.warning(err)
        sys.exit(1)

    except requests.exceptions.HTTPError as he:
        err = f"HTTP error: {he}"
        logger.warning(err)
        cel_logger.warning(err)
        sys.exit(1)


if __name__ == '__main__':
    verbose = True
    main()
