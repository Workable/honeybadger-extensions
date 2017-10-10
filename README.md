
# Honeybadger-Extensions

**Honeybadger-Extensions** extend current [Honeybadger Python library](https://github.com/honeybadger-io/honeybadger-python) to better
support [Celery](http://www.celeryproject.org/) & [Flask](http://flask.pocoo.org). It offers:

- Improved reporting, including details for component, action etc.
- Easier Honeybadger via Flask's or Celery's configuration object.
- (Optional) Automatic reporting of errors detected by Celery or Flask.

## Installation

The easiest way to install it is using ``pip`` from PyPI

```bash
pip install Honeybadger-Extensions
```


## Celery Usage

Honeybadger-Extensions provides the `install_celery_handler()` function which can be used to initialize both Honeybadger & the Celery extensions. The arguments to this function are:

- `config`: a dict-like object to use for configuring Honeybadger.
- `context_generators`: allows adding dynamically context on each call to `honeybadger.notify`.  It should be a dictionary, with key the name of the context variable to use and value a lambda or callable that generates the value.
- `report_exceptions`: boolean, whether to report exceptions raised by tasks. False by default. Uses [task_failure signal](http://docs.celeryproject.org/en/latest/userguide/signals.html#task-failure) to detect failures.


> Hint: You can reuse configuration properties from celery's configuration object.

> Hint: It's a good idea to initialize honeybadger as soon as possible in order to catch errors while initializing celery

The following conventions are used for reporting:

- **component**: The module that the task is defined in is used.
- **action**: The name of the task is used.
- **params**: A dictionary containing `args` and `kwargs` passed to the task.
- **cgi_data**: Task ID, current retry and max retries are added as values.

### Example: Setup Honeybadger and automatically report exceptions

The following example will setup Honeybadger and automatically report exceptions raised by the tasks.
 
It will also add `component`, `action`, `params`, `cgi_data` and context (as generated by context generators) to all errors sent using `honeybadger.notify()`. 

```python

from celery import Celery
from honeybadger_extensions import install_celery_handler

celery = Celery(__name__)
celery.config_from_object({
    'HONEYBADGER_API_KEY': '<your key>',
    'HONEYBADGER_ENVIRONMENT': 'development'
})

install_celery_handler(config=celery.conf, report_exceptions=True)

[...]

@celery.task
def mytask():
    [...]
    try:
        # Do something dangerous
        [...]
    except Exception as e:
        honeybadger.notify(e) # Additional info will be added!

```


## Flask usage

A Flask extension is available for initializing and configuring Honeybadger: `honeybadger_extensions.HoneybadgerFlask`. The extensions add the following information:

- **url**: The URL the request was sent to.
- **component**: The module that the view is defined at. If the view is a class-based view, then the name of the class is also added.
- **action**: The name of the function called. If the action is defined within a blueprint, then the action name will have the name of the blueprint prefixed.
- **params**: A dictionary containing query parameters and form data. If a variable is defined in both, then the form data are stored. Params are filtered (see [Configuration](#config)).
- **session**: Session data, filtered (see [Configuration](#config)).
- **cgi_data**: Request headers, filtered (see [Configuration](#config)).

Let's see it in action with an example:

### Example 1: Setup Honeybadger and automatically report exceptions

```python
    from flask import Flask, jsonify
    from honeybadger_extensions import HoneybadgerFlask

    app = Flask(__name__)
    app.config['HONEYBADGER_ENVIRONMENT'] = 'development'
    app.config['HONEYBADGER_API_KEY'] = '<your key>'
    app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
    app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
    HoneybadgerFlask(app, report_exceptions=True)

    @app.route('/')
    def index():
        a = int(request.args.get('a'))
        b = int(request.args.get('b'))

        logger.info('Dividing two numbers {} {}'.format(a, b))
        return jsonify({'result': a / b})

[...]

```

The code above will:

- Initialize honeybadger using provided configuration.
- Listen for exceptions.
- Log unhandled exceptions to Honeybadger.
- It will also add `url`, `component`, `action`, `params`, `cgi_data` and context (as generated by context generators) to all errors send using `honeybadger.notify()`. 

You can get an error by passing 0 as argument `b`. The logged `action` will be `index`.

> Note: Using `report_exceptions=True` will result in recording all exceptions thrown by your view functions, including `HTTPError`'s raised by calls to `abort` methods.

> Note: HoneybadgerFlask uses `got_request_exception` signal to detect errors. If you don't see some errors, check if an [errorhandler](http://flask.pocoo.org/docs/0.12/patterns/errorpages/#error-handlers) handles it before raising an error.


### Example 2: Setup Honeybadger with dynamic context

```python
from flask import Flask
from flask.views import MethodView
from honeybadger_extensions import HoneybadgerFlask

app = Flask(__name__)
app.config['HONEYBADGER_ENVIRONMENT'] = 'development'
app.config['HONEYBADGER_API_KEY'] = '<your key>'
app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'
HoneybadgerFlask(app, context_generators={
    'request-id': lambda: request.headers.get('X-Request-ID')
})

[...]

```


Application `app` will:

- Initialize honeybadger using provided configuration.
- It will **NOT** listen for exceptions
- Everything logged to Honeybadger will contain `request-id` in the context, with value the value of HTTP header `X-Request-ID`

### More examples

You can find more examples under [examples](examples/README.md) directory.

## <a name="config"></a>Configuration

The following parameters can be configured through Flask's configuration system:

| Configuration Name | Description |
| ------------------ | ----------- |
| **HONEYBADGER\_API\_KEY**|  Honeybadger's API key. If it's not present, honeybadger won't be initialized. |
| **HONEYBADGER_ENVIRONMENT** | The name of the environment to use in honeybadger. |
| **HONEYBADGER\_EXCLUDE\_HEADERS** | **Flask only!** Headers to exclude from logging. If this variable is not configured, then `Authorization` and `Proxy-Authorization` headers are the default. |
| **HONEYBADGER\_PARAMS\_FILTERS** | **Flask only!** Parameters from query string, form post or session to exclude. Replaces them with string `[FILTERED]`. |


## License

See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
