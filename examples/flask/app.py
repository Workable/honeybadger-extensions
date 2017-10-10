import logging
from flask import Flask, request

from honeybadger_extensions import HoneybadgerFlask

logger = logging.getLogger(__name__)


def generic_div(a, b):
    """Simple function to divide two numbers"""
    logger.debug('Called generic_div({}, {})'.format(a, b))
    return a / b


app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'test'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
HoneybadgerFlask(app, report_exceptions=True, context_generators={
    'request-id': lambda: request.headers.get('X-Request-ID')
})


@app.route('/')
def index():
    a = int(request.args.get('a'))
    b = int(request.args.get('b'))

    logger.info('Dividing two numbers {} {}'.format(a, b))
    return str(generic_div(a, b))
