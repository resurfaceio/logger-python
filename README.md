# resurfaceio-logger-python
Logging usage of Python-based services, with user privacy by design.

Visit <a href="https://resurface.io">resurface.io</a> for general information on usage logging.

[![PyPI version](https://badge.fury.io/py/usagelogger.svg)](https://badge.fury.io/py/usagelogger)

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

Requires Python 3.7 or higher. No other dependencies to conflict with your app.

<a name="installing_with_pip"/>

## Installing With pip

```
pip3 install --upgrade usagelogger
```

<a name="logging_from_django"/>

## Logging From Django

After <a href="#installing_with_pip">installing the package</a>, edit `settings.py` to register middleware.

```python
MIDDLEWARE = [
    "django.middleware...",
    "usagelogger.django.HttpLoggerForDjango",
]
```

Now add a new section to `settings.py` for logging configuration.

```python
USAGELOGGER = {
    'url': 'http://localhost:4001/message',
    'rules': 'include debug'
}
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
