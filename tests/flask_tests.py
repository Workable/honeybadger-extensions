import unittest
import flask
import werkzeug

from unittest.mock import patch

from flask import Blueprint, session
from flask.views import MethodView
from honeybadger_extensions import HoneybadgerFlask


class HoneybadgerFlaskTestCase(unittest.TestCase):

    def setUp(self):
        self.default_headers = {
           'Content-Length': '0',
           'Host': 'localhost',
           'User-Agent': 'werkzeug/%s' % werkzeug.__version__
        }
        self.app = flask.Flask(__name__)
        self.app.config.update({
            'HONEYBADGER_ENVIRONMENT': 'production_flask'
        })

    def assert_send_notice_once_with(self, mock_send_notice, url, component, action, params, session, cgi_data,
                                     context):
        self.assertEqual(1, mock_send_notice.call_count, msg='send_notice should be called exactly once')
        actual = mock_send_notice.call_args[0][1]['request']
        self.assertEqual(url, actual['url'], msg='URL not matching')
        self.assertEqual(component, actual['component'], msg='Incorrect component')
        self.assertEqual(action, actual['action'], msg='Incorrect action')
        self.assertDictEqual(params, actual['params'], msg='Different params')
        self.assertDictEqual(session, actual['session'], msg='Different session data')
        self.assertDictEqual(cgi_data, actual['cgi_data'], msg='Different headers')
        self.assertDictEqual(context, actual['context'], msg='Different context')

    @patch('honeybadger.connection.send_notice')
    def test_without_generators(self, mock_send_notice):
        HoneybadgerFlask(self.app, report_exceptions=True)

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_with_generators(self, mock_send_notice):
        HoneybadgerFlask(self.app, report_exceptions=True, context_generators={
            'ringbearer': lambda: 'bilbo'
        })

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={'ringbearer': 'bilbo'})

    @patch('honeybadger.connection.send_notice')
    def test_with_headers(self, mock_send_notice):
        HoneybadgerFlask(self.app, report_exceptions=True)

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error', headers={'X-Wizard-Color': 'grey', 'Authorization': 'Bearer 123'})

        expected_headers = {'X-Wizard-Color': 'grey'}
        expected_headers.update(self.default_headers)

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={},
                                          session={},
                                          cgi_data=expected_headers,
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_without_auto_reporting(self, mock_send_notice):
        self.app = flask.Flask(__name__)
        HoneybadgerFlask(self.app)

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error')

        mock_send_notice.assert_not_called()

    @patch('honeybadger.connection.send_notice')
    def test_with_additional_skip_headers(self, mock_send_notice):
        self.app.config.update(HONEYBADGER_EXCLUDE_HEADERS='Authorization, X-Dark-Land')
        HoneybadgerFlask(self.app, report_exceptions=True)

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error', headers={
            'X-Wizard-Color': 'grey',
            'Authorization': 'Bearer 123',
            'X-Dark-Land': 'Mordor'
        })

        expected_headers = {'X-Wizard-Color': 'grey'}
        expected_headers.update(self.default_headers)

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={},
                                          session={},
                                          cgi_data=expected_headers,
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_do_not_report(self, mock_send_notice):
        HoneybadgerFlask(self.app)

        @self.app.route('/error')
        def error():
            return 1 / 0

        self.app.test_client().get('/error?a=1&b=2&b=3')

        mock_send_notice.assert_not_called()

    @patch('honeybadger.connection.send_notice')
    def test_with_blueprint(self, mock_send_notice):
        bp = Blueprint('blueprint', __name__)

        @bp.route('/error')
        def error():
            return 1 / 0

        self.app.register_blueprint(bp)

        HoneybadgerFlask(self.app, report_exceptions=True)

        self.app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='blueprint.error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_with_view_class(self, mock_send_notice):

        class ErrorView(MethodView):
            def get(self):
                return 1 / 0

        self.app.add_url_rule('/error', view_func=ErrorView.as_view('error'))

        HoneybadgerFlask(self.app, report_exceptions=True)

        self.app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests.ErrorView',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_post_form(self, mock_send_notice):
        self.app.config.update(HONEYBADGER_API_KEY='abcd', HONEYBADGER_PARAMS_FILTERS='skip,password')
        HoneybadgerFlask(self.app, report_exceptions=True)

        @self.app.route('/error', methods=['POST'])
        def error():
            return 1 / 0

        self.app.test_client().post('/error?a=1&b=2&b=3', data={
            'foo': 'bar',
            'password': 'qwerty',
            'a': 'newvalue',
            'skip': 'secret'
        })

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={
                                              'a': ['newvalue'],
                                              'b': ['2', '3'],
                                              'foo': ['bar'],
                                              'skip': '[FILTERED]',
                                              'password': '[FILTERED]'
                                          },
                                          session={},
                                          cgi_data={
                                              'Content-Length': '46',
                                              'Content-Type': 'application/x-www-form-urlencoded',
                                              'Host': 'localhost',
                                              'User-Agent': 'werkzeug/%s' % werkzeug.__version__
                                          },
                                          context={})

    @patch('honeybadger.connection.send_notice')
    def test_session(self, mock_send_notice):
        self.app.config.update(dict(
            HONEYBADGER_API_KEY='abcd',
            HONEYBADGER_PARAMS_FILTERS='skip,password',
            SECRET_KEY='key'
        ))
        HoneybadgerFlask(self.app, report_exceptions=True)

        @self.app.route('/error')
        def error():
            session['answer'] = '42'
            session['password'] = 'this is fine'

            1 / 0

        self.app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={
                                              'a': ['1'],
                                              'b': ['2', '3']
                                          },
                                          session={
                                              'answer': '42',
                                              'password': '[FILTERED]'
                                          },
                                          cgi_data=self.default_headers,
                                          context={})
