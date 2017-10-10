import unittest
from unittest.mock import patch
from celery import Celery
from honeybadger import honeybadger

from honeybadger_extensions import install_celery_handler, uninstall_celery_handler


class ConnectFailureHandlerTestCase(unittest.TestCase):

    def setUp(self):
        super(ConnectFailureHandlerTestCase, self).setUp()
        self.celery = Celery(__name__)
        self.celery.conf.CELERY_ALWAYS_EAGER = True

    def tearDown(self):
        uninstall_celery_handler()

    def assert_send_notice_once_with(self, mock_send_notice, component, action, params, cgi_data, context):
        mock_send_notice.assert_called_once()
        actual = mock_send_notice.call_args[0][1]['request']
        self.assertEqual(component, actual['component'], msg='Incorrect component')
        self.assertEqual(action, actual['action'], msg='Incorrect action')
        self.assertDictEqual(params, actual['params'], msg='Different params')
        self.assertDictEqual(cgi_data, actual['cgi_data'], msg='Different headers')
        self.assertDictEqual(context, actual['context'], msg='Different context')

    @patch('honeybadger.core.send_notice')
    def test_without_generators(self, mock_send_notice):
        install_celery_handler(self.celery.conf, report_exceptions=True)

        @self.celery.task
        def dummy_task(x, y=1):
            return x / y

        dummy_task.apply_async(args=(1, ), kwargs={'y': 0}, task_id='abc')
        self.assert_send_notice_once_with(mock_send_notice,
                                          'tests.celery_tests',
                                          'tests.celery_tests.dummy_task',
                                          {'args': [1], 'kwargs': {'y': 0}},
                                          {'task_id': 'abc', 'retries': 0, 'max_retries': 3},
                                          {})

    @patch('honeybadger.core.send_notice')
    def test_auto_report_disabled(self, mock_send_notice):
        install_celery_handler(self.celery.conf, report_exceptions=False)

        @self.celery.task
        def dummy_task(x, y=1):
            return x / y

        dummy_task.apply_async(args=(1,), kwargs={'y': 0}, task_id='abc')
        mock_send_notice.assert_not_called()

    @patch('honeybadger.core.send_notice')
    def test_with_generators(self, mock_send_notice):
        install_celery_handler(config=self.celery.conf, context_generators={
            'ringbearer': lambda: 'frodo'
        }, report_exceptions=True)

        @self.celery.task
        def dummy_task(x, y=1):
            return x / y

        dummy_task.apply_async(args=(1, ), kwargs={'y': 0}, task_id='abc')

        self.assert_send_notice_once_with(mock_send_notice,
                                          'tests.celery_tests',
                                          'tests.celery_tests.dummy_task',
                                          {'args': [1], 'kwargs': {'y': 0}},
                                          {'task_id': 'abc', 'retries': 0, 'max_retries': 3},
                                          {'ringbearer': 'frodo'})

    @patch('honeybadger.core.send_notice')
    def test_custom_notify_with_generators(self, mock_send_notice):
        install_celery_handler(config=self.celery.conf, context_generators={
            'ringbearer': lambda: 'frodo'
        }, report_exceptions=True)

        @self.celery.task
        def dummy_task(x, y=1):
            try:
                return x / y
            except ZeroDivisionError as e:
                honeybadger.notify(e, context={'q': 3})

        dummy_task.apply_async(args=(1,), kwargs={'y': 0}, task_id='abc')

        self.assert_send_notice_once_with(mock_send_notice,
                                          'tests.celery_tests',
                                          'tests.celery_tests.dummy_task',
                                          {'args': [1], 'kwargs': {'y': 0}},
                                          {'task_id': 'abc', 'retries': 0, 'max_retries': 3},
                                          {'ringbearer': 'frodo', 'q': 3})

    @patch('honeybadger.core.send_notice')
    def test_with_named_task(self, mock_send_notice):
        install_celery_handler(self.celery.conf, report_exceptions=True)

        @self.celery.task(name='divider')
        def dummy_task(x, y=1):
            return x / y

        dummy_task.apply_async(args=(1,), kwargs={'y': 0}, task_id='abc')
        self.assert_send_notice_once_with(mock_send_notice,
                                          'tests.celery_tests',
                                          'divider',
                                          {'args': [1], 'kwargs': {'y': 0}},
                                          {'task_id': 'abc', 'retries': 0, 'max_retries': 3},
                                          {})
