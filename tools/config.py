from tools.yaml_reader import Setup
import os
from pathlib import Path

ROOT = Path(__file__).parents[1]
CONFIG_DIR = os.path.join(ROOT, '.configfiles')
LOG_CONFIGFILE = os.path.join(CONFIG_DIR, 'local_logs_config.ini')
LOGS_DIR = os.path.join(ROOT, 'logs')
API_LOGS = os.path.join(ROOT, 'apilogs')

YML_FILE = os.path.join(CONFIG_DIR, 'config.yml')
s = Setup(yml_file=YML_FILE)

AWS_S3_KEY = s.aws.client
AWS_S3_SECRET = s.aws.secret
AWS_S3_REGION = s.aws.region
AWS_S3_ENDPOINT = s.aws.endpoint
AWS_S3_TARGET = s.aws.target

LOGFILE_URL = s.misc.logfile_url


if __name__ == '__main__':
    s = Setup(YML_FILE)
    print(f"AWS client: {s.aws.client}")
    print(f"AWS secret: {s.aws.secret}")
    print(f"AWS region: {s.aws.region}")
    print(f"AWS endpoint: {s.aws.endpoint}")
    print(f"AWS target: {s.aws.target}")
    print(f"Distant Log File URL: {s.misc.logfile_url}")
