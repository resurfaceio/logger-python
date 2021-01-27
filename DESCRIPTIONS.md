Logging usage of Python-based services, with user privacy by design.

Visit <a href="https://resurface.io">resurface.io</a> for general information on usage logging.

## Middleware Integrations

Loggers can be added to <a href="https://github.com/resurfaceio/logger-python#logging-from-django">Django</a>
applications with only minor configuration changes.

## Logging With API

Loggers can be directly integrated into your application via our logging
<a href="https://github.com/resurfaceio/logger-python/blob/master/API.md">API</a>.
This requires more effort than middleware integrations, but also offers the greatest flexibility and control.

## Protecting User Privacy

Loggers always have an active set of <a href="https://resurface.io/rules.html">rules</a> that control what data is logged
and how sensitive data is masked. By default, loggers apply a strict set of predefined rules, but logging rules are easily
customized to meet the needs of any application.

---

&copy; 2016-2021 <a href="https://resurface.io">Resurface Labs Inc.</a>
