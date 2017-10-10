from __future__ import print_function, absolute_import

import logging
from six import iteritems

from flask import request_started, request_tearing_down, got_request_exception
from flask import current_app, session, request as _request
from honeybadger import payload
from honeybadger.utils import filter_dict

from .base import HoneybadgerExtension
from ._helpers import csv_to_list

DEFAULT_SKIP_HEADERS = ', '.join([
    'Authorization',
    'Proxy-Authorization'
])

logger = logging.getLogger(__name__)


class HoneybadgerFlask(HoneybadgerExtension):
    """
    Flask extension for honeybadger. Initializes honeybadger and adds a flask error handler that notifies honeybadger
    of exceptions.
    """
    def __init__(self, app=None, context_generators={}, report_exceptions=False):
        """
        Initialize Honeybadger.
        :param flask.Application app: the application to wrap for the exception.
        :param dict context_generators: a dictionary with key the name of additional context property to add and value
        a callable that generates the actual value of the property.
        :param bool report_exceptions: whether to automatically report exceptions on requests or not.
        """
        super(HoneybadgerFlask, self).__init__(context_generators=context_generators,
                                               report_exceptions=report_exceptions)
        self.app = app
        self.skip_headers = []
        if app is not None:
            self.init_app(app, context_generators=context_generators, report_exceptions=report_exceptions)

    def init_app(self, app, context_generators={}, report_exceptions=False):
        """
        Initialize honeybadger and listen for errors
        :param app: the Flask application object.
        :param context_generators: a dictionary with key the name of additional context property to add and value a
        callable that generates the actual value of the property.
        :param bool report_exceptions: whether to automatically report exceptions on requests or not.
        """
        self.context_generators = context_generators
        self.report_exceptions = report_exceptions
        self.initialize_honeybadger(app.config)
        self._patch_generic_request_payload()
        self.skip_headers = set(csv_to_list(app.config.get('HONEYBADGER_EXCLUDE_HEADERS', DEFAULT_SKIP_HEADERS)))
        request_started.connect(self.setup_context, sender=app, weak=False)
        request_tearing_down.connect(self.reset_context, sender=app, weak=False)
        logger.info('Honeybadger Flask helper installed')

        if self.report_exceptions:
            logger.info('Enabling auto-reporting exceptions')
            got_request_exception.connect(self._handle_exception, sender=app, weak=False)

    def _patch_generic_request_payload(self):
        """
        Monkey-patches Honeybadger's generic_request_payload to add information from Flask.
        """
        def generic_request_payload_decorator(original):
            def _wrapper(request, context, config):
                current_view = current_app.view_functions[_request.endpoint]
                if hasattr(current_view, 'view_class'):
                    component = '.'.join((current_view.__module__, current_view.view_class.__name__))
                else:
                    component = current_view.__module__
                payload = {
                    'url': _request.base_url,
                    'component': component,
                    'action': _request.endpoint,
                    'params': {},
                    'session': filter_dict(dict(session), config.params_filters),
                    'cgi_data': {
                        k: v
                        for k, v in iteritems(_request.headers)
                        if k not in self.skip_headers
                    },
                    'context': context
                }

                # Add query params
                params = filter_dict(dict(_request.args), config.params_filters)
                params.update(filter_dict(dict(_request.form), config.params_filters))
                payload['params'] = params

                return payload

            return _wrapper

        payload.generic_request_payload = generic_request_payload_decorator(payload.generic_request_payload)
        logger.info('Monkey-patched generic_request_payload')

    def _handle_exception(self, sender, exception=None):
        """
        Actual code handling the exception and sending it to honeybadger if it's enabled.
        :param T sender: the object sending the exception event.
        :param Exception exception: the exception to handle.
        """
        self.handle_exception(exception=exception)
