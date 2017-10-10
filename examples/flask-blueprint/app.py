import logging

from flask import Flask

from honeybadger_extensions import HoneybadgerFlask
from blueprint import simple_page

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'test'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
HoneybadgerFlask(app, report_exceptions=True)

app.register_blueprint(simple_page)
