=========================
resurfaceio-logger-python
=========================

© 2016-2019 Resurface Labs Inc.

Logging usage of Python cloud apps, with user privacy by design.

.. contents::

Dependencies
------------
The Resurface Labs logger package works on Python versions:

* 3.4.x and greater
* 3.5.x and greater
* 3.6.x and greater
* 3.7.x and greater

Installation
------------
The easiest way to install the Resurface Labs logger is to use `pip`_ in a ``virtualenv``::

    $ pip install usagelogger

or, if you are not installing in a ``virtualenv``, to install globally::

    $ sudo pip install usagelogger

or for your user::

    $ pip install --user usagelogger

If you have the logger installed and want to upgrade to the latest version
you can run::

    $ pip install --upgrade usagelogger

You can also just `download the tarball`_.  Once you have the logger directory structure on your workstation, you can just run::

    $ cd <path_to_logger>
    $ python setup.py install

Logging from Django
-------------------

Logging from Flask
------------------

Logging With API
----------------

Loggers can be directly integrated into your application using our API_. This requires the most effort compared with
the options described above, but also offers the greatest flexibility and control.

Protecting User Privacy
-----------------------

Loggers always have an active set of `Logging rules documentation`_ that control what data is logged
and how sensitive data is masked. All of the examples above apply a predefined set of rules (`include strict`),
but logging rules are easily customized to meet the needs of any application.


.. _pip: http://www.pip-installer.org/en/latest/
.. _`download the tarball`: https://pypi.org/project/resurfaceio/
.. _API: API.rst
.. _`Logging rules documentation`: https://resurface.io/rules.html
