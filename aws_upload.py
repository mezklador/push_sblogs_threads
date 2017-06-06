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
from tools.logger import Logger
from tools.utils import human_filesize as hfs
from S3.client import LogFiles


logger = Logger('uploads/state_of_union.log')

s3 = LogFiles().Main

BUCKET_DESTINATION = "sb_logs"

filesize_list = []

app = Celery('aws_upload',
             broker='redis://localhost:6379/10',
             backend='redis://localhost:6379/10')

approved = True
do_not_remove = False


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
            abs_filepath = aws_filepath['abs_path']
            aws_destination = aws_filepath['destination']

            if approved:
                s3.upload_file(abs_filepath,
                               bucket,
                               aws_destination,
                               ExtraArgs={'ACL': 'public-read'})

            endpoint_url = s3.meta.endpoint_url
            pub_url = f"{endpoint_url}/{bucket}/{aws_destination}"

            if not do_not_remove:
                delete_localfiles = remove_file(aws_filepath['abs_path'])
                if delete_localfiles:
                    end = time() - start
                    info_string = f"Upload {local_file}, in {end:.4f} sec. " \
                                  f"to AWS S3: {pub_url}"
                    loginfo(info_string)
                else:
                    logwarn(f"{local_file} was NOT removed from logs/.")
        except botocore.exceptions.ClientError as e:
            logwarn(f"Problem with S3: {e}")
    else:
        if remove_file(os.path.join(LOGS_DIR, local_file)):
            return True

    return None


def loginfo(msg):
    logger.info(msg)
    return True


def logwarn(msg):
    logger.warning(msg)
    sys.exit(1)


def remove_file(link):
    try:
        os.unlink(link)
        return True
    except:
        return False


def parse_local_logfiles(logfiles=os.listdir(LOGS_DIR)):
    total_filesize = []
    if len(logfiles) > 0:
        for logfile in logfiles:
            logfile_path = os.path.join(LOGS_DIR, logfile)
            total_filesize.append(os.stat(logfile_path).st_size)
            upload_to_s3(logfile)

        return (True,
                len(logfiles),
                hfs(sum(total_filesize)))

    return False


if __name__ == '__main__':
    action = parse_local_logfiles()
    if action[0]:
        print(f"{action[1]} logs were send to AWS S3 Bucket.",
              f"Weight: {action[2]}.",
              sep='\n')
    else:
        print("Nothing to do or something wrong\nCheck apilogs.")
