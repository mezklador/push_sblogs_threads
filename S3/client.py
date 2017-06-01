from tools.config import (
    AWS_S3_KEY,
    AWS_S3_SECRET,
    AWS_S3_REGION,
    AWS_S3_ENDPOINT,
    AWS_S3_TARGET,
)

import boto3
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
        return dict(public_link=log[0],
                    date=log[1],
                    uuid=log[2],
                    size=log[3])

    @property
    def all(self):
        return self._get_logs()

    @property
    def last(self):
        last_log = self.all[-1]
        return last_log

    @property
    def first(self, as_dict=True):
            first_log = self.all[0]
            if as_dict:
                return self._dict_display(first_log)

            return first_log
