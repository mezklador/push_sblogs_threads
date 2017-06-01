import math
import os

from tools.config import LOGS_DIR
from S3.client import LogFiles

s3 = LogFiles()


def last_S3_file(as_dict=True):
    '''
    Returns the last file in AWS S3 Bucket.
    :return: dict|tuple
    '''
    last = list(s3.last)
    if as_dict:
        return _to_dict(last)

    return last


def S3_listing(as_dict=True):
    all = list(s3.all)
    if as_dict:
        return _to_dict(all)

    return all


def _to_dict(blocks):
    return [dict(public_link=l[0],
                date=l[1],
                uuid=l[2],
                size=human_filesize(l[3]))
            for l in blocks]


def human_filesize(size):
   if (size == 0):
       return '0B'
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size, 1024)))
   p = math.pow(1024, i)
   s = round(size / p, 2)
   return f"{s}{size_name[i]}"

def localfiles():
    return (os.path.join(LOGS_DIR, f) for f in os.listdir(LOGS_DIR))