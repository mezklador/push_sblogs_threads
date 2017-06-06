1. for **dwn.py**: 
```
celery -A dwn worker -B --loglevel=info
```
2. for **aws_uploads.py**:
```python
celery -A aws_uploads worker -B --loglevel=info
```
