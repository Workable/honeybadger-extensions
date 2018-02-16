from .celery import CeleryHoneybadgerFailureHandler
from .flask import HoneybadgerFlask


__version__ = '0.1.2'

celery_handler = CeleryHoneybadgerFailureHandler()

install_celery_handler = celery_handler.install
uninstall_celery_handler = celery_handler.teardown


__all__ = [
    'install_celery_handler',
    'uninstall_celery_handler',
    'HoneybadgerFlask'
]
