import os
import yaml

# from tools.config import CONFIG_DIR

# DUMMY_YML_FILE = os.path.join(CONFIG_DIR, 'config.yml.example')
DUMMY_YML_FILE = '../.configfiles/config.yml.example'


class Setup:

    def __init__(self, yml_file=DUMMY_YML_FILE):
        '''
        Check if YAML file exists here
        Don't forget to declare any additional property
        (as redis, aws, etc) here

        :param yml_file: YAML object
        '''
        filepath = os.path.join(os.getcwd(), yml_file)
        if filepath:
            with open(filepath) as ymlfile:
                cfg = yaml.load(ymlfile)
            self.cfg = cfg
        else:
            raise(f"No {yml_file} as YAML config file exists.")

    @property
    def redis(self):
        self.obj = self.cfg['redis']
        return self

    @property
    def aws(self):
        self.obj = self.cfg['aws']
        return self

    @property
    def misc(self):
        self.obj = self.cfg['misc']
        return self

    def __getattr__(self, key):
        if self.obj is not None:
            if key in self.obj:
                return self.obj[key]
        return False


if __name__ == '__main__':
    s = Setup()

    host = s.redis.host
    port = s.redis.port
    db = s.redis.db
    channel = s.channel

    aws_client_key = s.aws.client
    aws_client_secret = s.aws.secret

    msg_1 = f"Host: {host}\nPort: {port}\nDb: {db}\nChannel name: {channel}"
    msg_2 = f"AWS KEY: {aws_client_key}\nAWS SECRET: {aws_client_secret}"

    print(msg_1)
    print("-" * len(msg_1))
    print(msg_2)
    print("-" * len(msg_2))
