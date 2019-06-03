=========================
resurfaceio-logger-python
=========================

© 2016-2019 Resurface Labs Inc.

.. contents::

----------
Logger API
----------

Creating Loggers
----------------

To get started, first you'll need to create a ``HttpLogger`` instance.
Here there are options to specify a URL (for where JSON messages will be
sent) and/or a specific set of logging rules (for what privacy
protections to apply). Default values will be used for either of these
if specific values are not provided.

.. code:: python

   import resurfaceio.logger

   # with default url and rules
   logger = HttpLogger()

   # with specific url and default rules
   logger = HttpLogger(url='https://...')

   # with specific url and rules
   logger = HttpLogger(url='https://...', rules='include strict')

Logging HTTP Calls
------------------

Now that you have a logger instance, let's do some logging. Here you can
pass standard request/response objects, as well as response body and
request body content when these are available.

.. code:: python

   # with standard objects
   logger.log request, response

   # with response body
   logger.log(request, response, 'my-response-body')

   # with response and request body
   logger.log(request, response, 'my-response-body', 'my-request-body')

If standard request and response objects aren't available in your case,
create mock implementations to pass instead.

.. code:: python

   # define request to log
   request = HttpRequestImpl.new
   request.body = 'some json'
   request.content_type = 'application/json'
   request.headers['A'] = '123'
   request.request_method = 'GET'
   request.url = 'http://google.com'

   # define response to log
   response = HttpResponseImpl.new
   response.body = 'some html'
   response.content_type = 'text/html'
   response.headers['B'] = '234'
   response.status = 200

   # log objects defined above
   logger.log(request, response)

Setting Default Rules
---------------------

If no rules are provided when creating a logger, the default value of
``include strict`` will be applied. A different default value can be
specified as shown below.

.. code:: python

   HttpLogger.default_rules = 'include debug'

When specifying multiple default rules, put each on a separate line.
This is most easily done with a string literal.

.. code:: python

   HttpLogger.default_rules = """
     include debug
     sample 10
   """

Setting Default URL
-------------------

If your application creates more than one logger, or requires different
URLs for different environments (development vs testing vs production),
then set the ``USAGE_LOGGERS_URL`` environment variable. This value will
be applied if no other URL is specified when creating a logger::

   # from command line
   export USAGE_LOGGERS_URL="https://..."

   # in config.ru
   ENV['USAGE_LOGGERS_URL']='https://...'

   # for Heroku app
   heroku config:set USAGE_LOGGERS_URL=https://...

Enabling and Disabling Loggers
------------------------------

Individual loggers can be controlled through their ``enable`` and
``disable`` methods. When disabled, loggers will not send any logging
data, and the result returned by the ``log`` method will always be true
(success).

All loggers for an application can be enabled or disabled at once with
the ``UsageLoggers`` class. This even controls loggers that have not yet
been created by the application.

.. code:: python

   UsageLoggers.disable       # disable all loggers
   UsageLoggers.enable        # enable all loggers

All loggers can be permanently disabled with the
``USAGE_LOGGERS_DISABLE`` environment variable. When set to true,
loggers will never become enabled, even if ``UsageLoggers.enable`` is
called by the application. This is primarily done by automated tests to
disable all logging even if other control logic exists::

   # from command line
   export USAGE_LOGGERS_DISABLE="true"

   # in config.ru
   ENV['USAGE_LOGGERS_DISABLE']='true'

   # for Heroku app
   heroku config:set USAGE_LOGGERS_DISABLE=true
