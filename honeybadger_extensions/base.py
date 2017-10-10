import logging
from honeybadger import honeybadger
from ._helpers import csv_to_list
from six import iteritems

logger = logging.getLogger(__name__)


class HoneybadgerExtension(object):
    """
    Base class for honeybadger extensions.
    """
    def __init__(self, context_generators={}, report_exceptions=False):
        """
        Initialize Honeybadger extension.
        :param dict context_generators: a dictionary with key the name of additional context property to add and value
        a callable that generates the actual value of the property.
        :param bool report_exceptions: whether to automatically report exceptions on requests or not.
        """
        self.context_generators = context_generators
        self.report_exception = report_exceptions

    def initialize_honeybadger(self, config):
        """
        Initializes honeybadger exception handler only if HONEYBADGER_API_KEY exists in config. If
        HONEYBADGER_ENVIRONMENT environment variable is set, honeybadger environment is also set.
        :param dict[str, T] config: the configuration object.
        """
        api_key = config.get('HONEYBADGER_API_KEY')
        # Initialize only if configured
        if api_key:
            logger.info('Configuring Honeybadger')
            honeybadger.configure(api_key=api_key,
                                  environment=config.get('HONEYBADGER_ENVIRONMENT', 'development'),
                                  params_filters=csv_to_list(config.get('HONEYBADGER_PARAMS_FILTERS',
                                                                        'password,password_confirmation,credit_card'))
                                  )
            logging.getLogger('honeybadger').addHandler(logging.StreamHandler())
            return True
        else:
            logger.info('No Honeybadger API KEY found, skipping configuration')
            return False

    def _generate_context(self):
        """
        Generate context for exception handling.
        :return: a dictionary with the context.
        :rtype: dict
        """
        context = {}
        for name, generator in iteritems(self.context_generators):
            context[name] = generator()

        return context

    def setup_context(self, *args, **kwargs):
        """
        Sets context for the request.
        :param T sender: the object sending the signal.
        :param extra: extra arguments passed by the signal.
        """
        honeybadger.set_context(**self._generate_context())

    def reset_context(self, *args, **kwargs):
        """
        Resets context when request is done.
        :param T sender: the object sending the signal
        :param Exception exc: exception caused during handling.
        :param extra: extras passed by the signal.
        """
        honeybadger.reset_context()

    def handle_exception(self, exception=None):
        """
        Actual code handling the exception and sending it to honeybadger if it's enabled.
        :param Exception exception: the exception to handle.
        """
        honeybadger.notify(exception)
