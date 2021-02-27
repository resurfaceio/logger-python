# resurfaceio-logger-python

Logging usage of Python-based services, with user privacy by design.

Visit <a href="https://resurface.io">resurface.io</a> for general information on usage logging.

![Python Version](https://img.shields.io/badge/python-3.7+-blue?style=for-the-badge&logo=python) [![CodeFactor](https://www.codefactor.io/repository/github/resurfaceio/logger-python/badge?style=for-the-badge)](https://www.codefactor.io/repository/github/resurfaceio/logger-python) [![License](https://img.shields.io/github/license/resurfaceio/logger-python?style=for-the-badge)](https://github.com/resurfaceio/logger-python/blob/master/LICENSE) <a href="https://github.com/resurfaceio/logger-python/blob/master/CONTRIBUTING.md" target="_blank" title="Contributions are welcome"><img src="https://img.shields.io/badge/contributions-welcome-green.svg?style=for-the-badge"></a>

<a href="https://badge.fury.io/py/usagelogger" target="_blank" title="PyPI version"><img src="https://badge.fury.io/py/usagelogger.svg"></a>

## Contents

<ul>
<li><a href="#dependencies">Dependencies</a></li>
<li><a href="#installing_with_pip">Installing With pip</a></li>
<li><a href="#logging_from_django">Logging From Django</a></li>
<li><a href="#logging_with_api">Logging With API</a></li>
<li><a href="#privacy">Protecting User Privacy</a></li>
</ul>

<a name="dependencies"/>

## Dependencies

Requires Python 3.7 or higher and a `requests` HTTP library. No other dependencies to conflict with your app.

<a name="installing_with_pip"/>

## Installing With pip

```
pip3 install --upgrade usagelogger
```

<a name="logging_from_requests"/>

## Logging From requests

```python

import requests

from usagelogger.middlewares import MiddlewareHTTPAdapter, ResurfaceLoggerMiddleware

middlewares = [
    ResurfaceLoggerMiddleware(
        url="http://localhost:4001/message", rules="include debug"
    )
]
session = requests.Session()
adapter = MiddlewareHTTPAdapter(middlewares)
session.mount("http://", adapter)
session.mount("https://", adapter)
response = session.get(
    url="https://demo.url.com/?id=1&name=my_name",
)

```

<a name="logging_from_django"/>

## Logging From Django

After <a href="#installing_with_pip">installing the package</a>, edit `settings.py` to register middleware.

```python
MIDDLEWARE = [
    "django.middleware...",
    "usagelogger.middlewares.HttpLoggerForDjango",
]
```

Now add a new section to `settings.py` for logging configuration.

```python
USAGELOGGER = {
    'url': 'http://localhost:4001/message',
    'rules': 'include debug'
}
```

<a name="logging_from_flask"/>

## Logging From Flask

```python
from flask import Flask

from usagelogger.middlewares import HttpLoggerForFlask

app = Flask(__name__)

app.wsgi_app = HttpLoggerForFlask(  # type: ignore
    app=app.wsgi_app, url="http://localhost:4001/message", rules="include debug"
)

@app.route("/")
def home():
    return "This route works!"

app.run(debug=True)

```

<a name="logging_with_api"/>

## Logging With API

Loggers can be directly integrated into your application using our [API](API.md). This requires the most effort compared with
the options described above, but also offers the greatest flexibility and control.

[API documentation](API.md)

<a name="privacy"/>

## Protecting User Privacy

Loggers always have an active set of <a href="https://resurface.io/rules.html">rules</a> that control what data is logged
and how sensitive data is masked. All of the examples above apply a predefined set of rules (`include debug`),
but logging rules are easily customized to meet the needs of any application.

<a href="https://resurface.io/rules.html">Logging rules documentation</a>

---

<small>&copy; 2016-2021 <a href="https://resurface.io">Resurface Labs Inc.</a></small>

```

```
