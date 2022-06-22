release: python manage.py migrate --noinput
web: gunicorn --bind :$PORT --workers 4 --worker-class uvicorn.workers.UvicornWorker fast_django.asgi:application
worker: celery -A fast_django worker -P prefork --loglevel=INFO
beat: celery -A fast_django beat --loglevel=INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
