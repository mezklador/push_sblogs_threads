from tools.config import (
    AWS_S3_KEY,
    AWS_S3_SECRET,
    AWS_S3_REGION,
    AWS_S3_ENDPOINT,
    AWS_S3_TARGET,
)

import boto3
import itertools
import os
import re


class LogFiles:
    def __init__(self,
                 key=AWS_S3_KEY,
                 secret=AWS_S3_SECRET,
                 region=AWS_S3_REGION,
                 endpoint=AWS_S3_ENDPOINT,
                 bucket=AWS_S3_TARGET):
        self._key = key
        self._secret = secret
        self._region = region
        self._endpoint = endpoint
        self._bucket = bucket
        self.Main = self._s3_client()

    def _s3_client(self):
        return boto3.client('s3',
                            aws_access_key_id=self._key,
                            aws_secret_access_key=self._secret,
                            region_name=self._region,
                            endpoint_url=self._endpoint,
                            config=boto3.session.Config(
                                signature_version="s3v4"
                            ))

    def _get_logs(self):
        '''
        List all objects contained inside the AWS S3 Bucket.
        :return:GENERATOR
        '''
        obj_link = self.Main.meta.endpoint_url
        endpoint = os.path.join(obj_link, self._bucket)
        pattern = re.compile(r'.*log$')
        try:
            s3_obj = self.Main.list_objects_v2(Bucket=self._bucket)
            buckets_gen = ((os.path.join(endpoint, k['Key']),
                            k['LastModified'],
                            k['ETag'],
                            k['Size'])
                           for k in s3_obj['Contents']
                           if pattern.search(k['Key']))

            return buckets_gen

        except Exception as e:
            """
            error = str(e).split(': ')[-1]
            sys.stderr.write(f"something wrong: {error}")
            check_cli(out=False)
            sys.exit(1)
            """
            return False

    def _dict_display(self, log):
        a = ()
        for l in log:
            a = a + (dict(public_link=l[0],
                          date=l[1],
                          uuid=l[2],
                          size=l[3]),)
        return a

    @staticmethod
    def _get_from_generator(gen, depth=1, inverted=False):
        t = gen
        if inverted:
            t = list(reversed(t))
        t = tuple(t)
        return t[:depth]

    @property
    def all(self):
        return list(self._get_logs())

    def last(self, depth=1, as_dict=False):
        last_log = self._get_from_generator(self.all,
                                            depth=depth,
                                            inverted=True)
        if as_dict:
            return self._dict_display(last_log)

        return last_log

    def first(self, depth=1, as_dict=False):
            first_log = self._get_from_generator(self.all,
                                                 depth=depth)
            if as_dict:
                return self._dict_display(first_log)
            
            return first_log
