# resurfaceio-logger-python
Logging usage of Python-based services, with user privacy by design.

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

Requires Python 3.5 or higher. No other dependencies to conflict with your app.

<a name="installing_with_pip"/>

## Installing With pip

```
pip install --upgrade usagelogger
```

<a name="logging_from_django"/>

## Logging From Django

<a name="logging_with_api"/>

## Logging With API

Loggers can be directly integrated into your application using our [API](API.md). This requires the most effort compared with
the options described above, but also offers the greatest flexibility and control.

[API documentation](API.md)

<a name="privacy"/>

## Protecting User Privacy

Loggers always have an active set of <a href="https://resurface.io/rules.html">rules</a> that control what data is logged
and how sensitive data is masked. All of the examples above apply a predefined set of rules (`include strict`),
but logging rules are easily customized to meet the needs of any application.

<a href="https://resurface.io/rules.html">Logging rules documentation</a>

---
<small>&copy; 2016-2019 <a href="https://resurface.io">Resurface Labs Inc.</a></small>
