# Honeybadger extensions examples

This directory contains examples for using Honeybadger-Extensions in your projects. All
examples contain a simple function that divides two integers. If you specify 0 as the denominator
a ZeroDivisionError will be raised and logged to Honeybadger.

Note that some examples might have additional requirements. You can install them using
[requirements.txt](requirements.txt) file.

## Celery

This example triggers a task that divides two integers.

#### Configuration

Edit file [celery/example_app/celery.py](celery/example_app/celery.py) and add your Honeybadger key.

> Note that this celery example uses default broker configuration. You'll need to start a RabbitMQ locally with default username/password.

#### Running

Move to directory `celery`.

Start celery worker:

```bash
$ celery worker --app worker -l info
```

You can use `divide.py` to trigger a task.

```bash
$ python divide.py 1 2                 # No error
$ python divide.py 1 0                 # Error, should be logged in honeybadger
```

## Flask

Flask examples are pretty much the same. A single endpoint at `/` divides two integers passed as arguments via parameters `a` (numerator) and `b` (denominator).
For example, by performing a GET at [http://localhost:5000?a=5&b=7](http://localhost:5000?a=5&b=7), it will return the result of 5/7.

 The example is packaged using three different Flask project structures:

 - Single endpoint
 - Blueprint
 - [Flask-Restplus](http://flask-restplus.readthedocs.io/)

### Single endpoint

#### Configuration

Edit file [flask/app.py](flask/app.py) and add your Honeybadger key.

#### Running

Run

```bash
$ FLASK_APP=app.py flask run
```

Visit [http://localhost:5000?a=5&b=0](http://localhost:5000?a=5&b=0) to get an error and log it to Honeybadger.

This example also contains context generators. You can test it by running:

```bash
$ curl "http://localhost:5000/?a=3&b=0" -H "X-Request-ID: abc123"
```

You will notice that `request-id` has been added to context.

### Flask blueprint

#### Configuration

Edit file [flask-blueprint/app.py](flask-blueprint/app.py) and add your Honeybadger key.

#### Running

Run

```bash
$ FLASK_APP=app.py flask run
```

Visit [http://localhost:5000/fraction?a=5&b=0](http://localhost:5000/fraction?a=5&b=0) to get an error and log it to Honeybadger.
