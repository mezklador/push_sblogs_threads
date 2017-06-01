from S3.client import LogFiles

s3 = LogFiles()


def last_S3_file(as_dict=True):
    '''
    Returns the last file in AWS S3 Bucket.
    :return: dict|tuple
    '''
    last = s3.last
    if as_dict:
        return _to_dict(last)

    return last


def S3_listing(as_dict=True):
    all = s3.all
    if as_dict:
        return _to_dict(all)

    return all


def _to_dict(l):
    return dict(public_link=l[0],
                date=l[1],
                uuid=l[2],
                size=l[3])
