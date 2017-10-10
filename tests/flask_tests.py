import unittest
import flask

from unittest.mock import patch

from flask import Blueprint, session
from flask.views import MethodView
from honeybadger_extensions import HoneybadgerFlask


class HoneybadgerFlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.default_headers = {
           'Content-Length': '0',
           'Content-Type': '',
           'Host': 'localhost',
           'User-Agent': 'werkzeug/0.12.2'
        }

    def assert_send_notice_once_with(self, mock_send_notice, url, component, action, params, session, cgi_data, context):
        mock_send_notice.assert_called_once()
        actual = mock_send_notice.call_args[0][1]['request']
        self.assertEqual(url, actual['url'], msg='URL not matching')
        self.assertEqual(component, actual['component'], msg='Incorrect component')
        self.assertEqual(action, actual['action'], msg='Incorrect action')
        self.assertDictEqual(params, actual['params'], msg='Different params')
        self.assertDictEqual(session, actual['session'], msg='Different session data')
        self.assertDictEqual(cgi_data, actual['cgi_data'], msg='Different headers')
        self.assertDictEqual(context, actual['context'], msg='Different context')

    @patch('honeybadger.core.send_notice')
    def test_without_generators(self, mock_send_notice):
        app = flask.Flask(__name__)
        HoneybadgerFlask(app, report_exceptions=True)

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.core.send_notice')
    def test_with_generators(self, mock_send_notice):
        app = flask.Flask(__name__)
        HoneybadgerFlask(app, report_exceptions=True, context_generators={
            'ringbearer': lambda: 'bilbo'
        })

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={'ringbearer': 'bilbo'})

    @patch('honeybadger.core.send_notice')
    def test_with_headers(self, mock_send_notice):
        app = flask.Flask(__name__)
        HoneybadgerFlask(app, report_exceptions=True)

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error', headers={'X-Wizard-Color': 'grey', 'Authorization': 'Bearer 123'})

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

    @patch('honeybadger.core.send_notice')
    def test_without_auto_reporting(self, mock_send_notice):
        app = flask.Flask(__name__)
        HoneybadgerFlask(app)

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error')

        mock_send_notice.assert_not_called()

    @patch('honeybadger.core.send_notice')
    def test_with_additional_skip_headers(self, mock_send_notice):
        app = flask.Flask(__name__)
        app.config.update(HONEYBADGER_EXCLUDE_HEADERS='Authorization, X-Dark-Land')
        HoneybadgerFlask(app, report_exceptions=True)

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error', headers={
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

    @patch('honeybadger.core.send_notice')
    def test_do_not_report(self, mock_send_notice):
        app = flask.Flask(__name__)
        HoneybadgerFlask(app)

        @app.route('/error')
        def error():
            return 1 / 0

        app.test_client().get('/error?a=1&b=2&b=3')

        mock_send_notice.assert_not_called()

    @patch('honeybadger.core.send_notice')
    def test_with_blueprint(self, mock_send_notice):
        app = flask.Flask(__name__)
        bp = Blueprint('blueprint', __name__)

        @bp.route('/error')
        def error():
            return 1 / 0

        app.register_blueprint(bp)

        HoneybadgerFlask(app, report_exceptions=True)

        app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests',
                                          action='blueprint.error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.core.send_notice')
    def test_with_view_class(self, mock_send_notice):
        app = flask.Flask(__name__)

        class ErrorView(MethodView):
            def get(self):
                return 1 / 0

        app.add_url_rule('/error', view_func=ErrorView.as_view('error'))

        HoneybadgerFlask(app, report_exceptions=True)

        app.test_client().get('/error?a=1&b=2&b=3')

        self.assert_send_notice_once_with(mock_send_notice,
                                          url='http://localhost/error',
                                          component='tests.flask_tests.ErrorView',
                                          action='error',
                                          params={'a': ['1'], 'b': ['2', '3']},
                                          session={},
                                          cgi_data=self.default_headers,
                                          context={})

    @patch('honeybadger.core.send_notice')
    def test_post_form(self, mock_send_notice):
        app = flask.Flask(__name__)
        app.config.update(HONEYBADGER_API_KEY='abcd', HONEYBADGER_PARAMS_FILTERS='skip,password')
        HoneybadgerFlask(app, report_exceptions=True)

        @app.route('/error', methods=['POST'])
        def error():
            return 1 / 0

        app.test_client().post('/error?a=1&b=2&b=3', data={
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
                                              'User-Agent': 'werkzeug/0.12.2'
                                          },
                                          context={})

    @patch('honeybadger.core.send_notice')
    def test_session(self, mock_send_notice):
        app = flask.Flask(__name__)
        app.config.update(HONEYBADGER_API_KEY='abcd',
                          HONEYBADGER_PARAMS_FILTERS='skip,password',
                          SECRET_KEY='key')
        HoneybadgerFlask(app, report_exceptions=True)

        @app.route('/error')
        def error():
            session['answer'] = '42'
            session['password'] = 'this is fine'

            1 / 0

        app.test_client().get('/error?a=1&b=2&b=3')

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
