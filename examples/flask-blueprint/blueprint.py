import logging

from flask import Blueprint, request

logger = logging.getLogger(__name__)


simple_page = Blueprint('simple_page', __name__)


def generic_div(a, b):
    """Simple function to divide two numbers"""
    logger.debug('Called generic_div({}, {})'.format(a, b))
    return a / b


@simple_page.route('/')
def index():
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))

    logger.info('Dividing two numbers {} {}'.format(a, b))
    return str(generic_div(a, b))
