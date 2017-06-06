1. for **dwn.py**: getting task done (download distant log file here) & write a log message (success/error) into *apilogs/downloads/celery.log*.

```bash
$ celery -A dwn worker --beat
```

2. for **aws_uploads.py**:

```bash
$ celery -A aws_uploads worker --beat
```
