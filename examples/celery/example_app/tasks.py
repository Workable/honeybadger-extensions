from celery.utils.log import get_task_logger
from .celery import celery as app

logger = get_task_logger(__name__)

@app.task()
def generic_div(a, b):
    """Simple function to divide two numbers"""
    logger.info('Called generic_div({}, {})'.format(a, b))
    return a / b
