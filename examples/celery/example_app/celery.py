from celery import Celery
from honeybadger_extensions import install_celery_handler

celery = Celery(__name__)
celery.config_from_object({
    'HONEYBADGER_API_KEY': '<your key>',
    'HONEYBADGER_ENVIRONMENT': 'development'
})

install_celery_handler(config=celery.conf, report_exceptions=True)

