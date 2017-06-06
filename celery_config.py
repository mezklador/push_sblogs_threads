from celery.schedules import crontab


ENABLE_UTC = True
TIMEZONE = 'Europe/Paris'
BROKER_URL = 'redis://127.0.0.1:6379/10'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/10'
CELERYD_LOG_FILE = 'apilogs/celery.log'

CELERYBEAT_SCHEDULE = {
    'every-2-minutes': {
        'task': 'dwn.main_task',
        'schedule': crontab(minute='*/2')
    }
}