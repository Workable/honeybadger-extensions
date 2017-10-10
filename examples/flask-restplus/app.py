import logging

from flask import Flask

from honeybadger_extensions import HoneybadgerFlask
from flask_restplus import Resource, Api, reqparse

logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'test'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
HoneybadgerFlask(app, report_exceptions=True)

api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('a', type=int, help='Numerator')
parser.add_argument('b', type=int, help='Denominator')


@api.route('/fraction')
class Fraction(Resource):
    def get(self):
        args = parser.parse_args()
        logger.info('Dividing two numbers {} {}'.format(args.a, args.b))
        return {'result': args.a / args.b}
