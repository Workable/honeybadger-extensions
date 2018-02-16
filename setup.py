"""
Honeybadger-Extensions
======================

|CircleCI|

**Honeybadger-Extensions** extend current `Honeybadger Python library`_ to better support `Celery`_ & `Flask`_.

It offers:

- Improved reporting, including details for component, action etc.
- Easier Honeybadger via Flask's or Celery's configuration object.
- (Optional) Automatic reporting of errors detected by Celery or Flask.


Features
--------

Honeybadger-Extensions provides the ``install_celery_handler()`` function which can be used
at any time which can be used to initialize both Honeybadger & allow improved Honeybadger reporting. It also offers the
``HoneybadgerFlask`` Flask extension that adds more information to Honeybadger logging, as well as automatic logging of
errors raised in the view functions.

Example 1: Initialize Celery
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In the following example, we will use the ``install_celery_handler`` to setup Honeybadger reporting.

.. code:: python

    from celery import Celery
    from honeybadger_extensions import install_celery_handler

    celery = Celery(__name__)
    celery.config_from_object({
        'HONEYBADGER_API_KEY': '<your key>',
        'HONEYBADGER_ENVIRONMENT': 'development'
    })

    install_celery_handler(config=celery.conf, report_exceptions=True)


Example 2: Initialize Flask
~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use HoneybadgerFlask extension to load Honeybadger configuration from Flask configuration object.

.. code:: python

    from flask import Flask, jsonify
    from honeybadger_extensions import HoneybadgerFlask

    app = Flask(__name__)
    app.config['HONEYBADGER_ENVIRONMENT'] = 'development'
    app.config['HONEYBADGER_API_KEY'] = '<your key>'
    app.config['HONEYBADGER_EXCLUDE_HEADERS'] = 'Authorization, Proxy-Authorization, X-Custom-Key'
    app.config['HONEYBADGER_PARAMS_FILTERS'] = 'password, secret, credit-card'

    # Setup Honeybadger and listen for exceptions
    HoneybadgerFlask(app, report_exceptions=True)

    @app.route('/')
    def index():
        a = int(request.args.get('a'))
        b = int(request.args.get('b'))

        logger.info('Dividing two numbers {} {}'.format(a, b))
        return jsonify({'result': a / b})

Installation
------------
The easiest way to install it is using ``pip`` from PyPI

.. code:: bash

    pip install Honeybadger-Extensions


License
-------

See the `LICENSE`_ file for license rights and limitations (MIT).

.. _Honeybadger Python Library: https://github.com/honeybadger-io/honeybadger-python
.. _Flask: http://flask.pocoo.org/
.. _Celery: http://www.celeryproject.org/
.. _LICENSE: https://github.com/Workable/honeybadger-extensions/blob/master/LICENSE.md
.. |CircleCI| image:: https://img.shields.io/circleci/project/github/Workable/honeybadger-extensions.svg
   :target: https://circleci.com/gh/Workable/honeybadger-extensions

"""
import re
import ast
from setuptools import setup

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('honeybadger_extensions/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

test_requirements = [
    'nose',
    'mock==2.0.0',
    'coverage~=4.3.4'
]

setup(
    name='Honeybadger-Extensions',
    version=version,
    url='http://github.com/Workable/honeybadger-extensions',
    license='MIT',
    author='Ioannis Foukarakis, Konstantinos Paliouras',
    author_email='ioannis.foukarakis@gmail.com, squarious@gmail.com',
    description='Honeybadger extension that can log exceptions raised '
                'by Flask or Celery, adding more context than the original  '
                'honeybadger python library.',
    long_description=__doc__,
    maintainer="Ioannis Foukarakis",
    maintainer_email="ioannis.foukarakis@gmail.com",
    packages=[
        'honeybadger_extensions'
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'honeybadger==0.1.2',
        'blinker>=1.1',
        'Flask>=0.8',
        'celery~=4.1.0'
    ],
    tests_require=test_requirements,
    setup_requires=[
        "flake8",
        "nose"
    ],
    extras_require={
        'test': test_requirements,
        'celery': ["celery~=4.1.0"],
    },
    test_suite='nose.collector',
    classifiers=[
        'Environment :: Web Environment', 'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])
