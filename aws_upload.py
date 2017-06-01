import botocore
from celery import Celery
import logging
import logging.config
import os
import sys
from time import time

from tools.config import (
    API_LOGS,
    LOG_CONFIGFILE,
    LOGS_DIR,
    AWS_S3_TARGET)
from S3.client import LogFiles


aws_logfile = os.path.join(API_LOGS,
                           'uploads',
                           'state_of_union.log')
logging.config.fileConfig(LOG_CONFIGFILE,
                          defaults={'logfilename': aws_logfile})
logger = logging.getLogger(__name__)

s3 = LogFiles().Main

BUCKET_DESTINATION = "sb_logs"

filesize_list = []

app = Celery('aws_upload',
             broker='redis://localhost:6379/10',
             backend='redis://localhost:6379/10')


def check_localfile(file):
    localfile = os.path.join(LOGS_DIR, file)
    localfile_size = os.stat(localfile).st_size

    if localfile_size not in filesize_list:
        filesize_list.append(localfile_size)

        # get the filename only
        f_name = localfile.split('/')[-1]
        return dict(destination=f"{BUCKET_DESTINATION}/{f_name}",
                    abs_path=localfile)

    return None


@app.task
def upload_to_s3(local_file,
                 bucket=AWS_S3_TARGET):
    start = time()
    aws_filepath = check_localfile(local_file)
    if aws_filepath is not None:
        try:
            abs_localfile = aws_filepath['abs_path']
            aws_destination = aws_filepath['destination']
            s3.upload_file(abs_localfile,
                           bucket,
                           aws_destination,
                           ExtraArgs={'ACL': 'public-read'})

            endpoint_url = s3.meta.endpoint_url
            pub_url = f"{endpoint_url}/{bucket}/{aws_destination}"
            if remove_localfile(aws_filepath['abs_path']):
                end = time() - start
                loginfo_string = f"Upload {local_file}, in {end:.4f} sec. " \
                                 f"to AWS S3: {pub_url}"
                loginfo(loginfo_string)
        except botocore.exceptions.ClientError as e:
            logwarn(f"Problem with S3: {e}")
    else:
        if remove_localfile(os.path.join(LOGS_DIR, local_file)):
            return True

    return None


def loginfo(msg):
    logger.info(msg)
    return True


def logwarn(msg):
    logger.warning(msg)
    sys.exit(1)


def remove_localfile(link):
    try:
        os.unlink(link)
        return True
    except:
        return False


def parse_local_logfiles(logfiles=os.listdir(LOGS_DIR)):
    if len(logfiles) > 0:
        for logfile in logfiles:
            upload_to_s3.delay(logfile)

        return (True, len(logfiles))

    return False


if __name__ == '__main__':
    action = parse_local_logfiles()
    if action[0]:
        print(f"{action[1]} logs were send to AWS S3 Bucket.")
    else:
        print("Nothing to do or something wrong\nCheck apilogs.")
