from __future__ import division, print_function, absolute_import

import logging

from honeybadger import payload

from celery import current_task
from celery.signals import task_failure, task_prerun, task_postrun
from .base import HoneybadgerExtension

logger = logging.getLogger(__name__)


class CeleryHoneybadgerFailureHandler(HoneybadgerExtension):

    def __init__(self):
        self.context_generators = {}
        self.report_exceptions = False

    def install(self, config={}, context_generators={}, report_exceptions=False):
        """
        Setup Celery - Honeybadger integration.
        :param dict[str, T] config: a configuration object to read config from.
        :param context_generators: Context generators
        :param bool report_exceptions: whether to automatically report exceptions on tasks or not.
        """
        self.initialize_honeybadger(config)
        self.context_generators = context_generators
        self.report_exceptions = report_exceptions
        task_prerun.connect(self.setup_context, weak=False)
        task_postrun.connect(self.reset_context, weak=False)
        if self.report_exceptions:
            task_failure.connect(self._failure_handler, weak=False)

        self._patch_generic_request_payload()
        logger.info('Registered Celery signal handlers')

    def _failure_handler(self, sender, task_id, exception, args, kwargs, traceback, einfo, **kw):
        """
        Handle failures.
        :param celery.Task sender: the task object sending the error.
        :param str task_id: the id of the task reporting the exception.
        :param Exception exception: the exception instance raised.
        :param list args: positional arguments the task was called with.
        :param dict kwargs: keyword arguments the task was called with.
        :param traceback: stack trace object.
        :param billiard.einfo.ExceptionInfo einfo: The billiard.einfo.ExceptionInfo instance.

        :param dict kw: any other arguments
        """
        self.handle_exception(exception=exception)

    def _patch_generic_request_payload(self):
        """
        Monkey-patches Honeybadger's generic_request_payload to add information from Celery task.
        """
        def generic_request_payload_decorator(original):
            def _wrapper(request, context, config):
                payload = {
                    'component': current_task.__module__,
                    'action': current_task.name,
                    'params': {
                        'args': list(current_task.request.args),
                        'kwargs': current_task.request.kwargs
                    },
                    'cgi_data': {
                        'task_id': current_task.request.id,
                        'retries': current_task.request.retries,
                        'max_retries': current_task.max_retries
                    },
                    'context': context
                }

                return payload

            return _wrapper

        payload.generic_request_payload = generic_request_payload_decorator(payload.generic_request_payload)
        logger.info('Monkey-patched generic_request_payload')

    def teardown(self):
        """
        Removes current failure handler
        """
        task_prerun.disconnect(self.setup_context)
        task_postrun.disconnect(self.reset_context)
        if self.report_exceptions:
            task_failure.disconnect(self._failure_handler)
        logger.info('Honeybadger Celery support uninstalled')
