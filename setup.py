from setuptools import setup

setup(
    name='usagelogger',
    version='2.0.2',
    description='Logging usage of Python-based services, with user privacy by design.',
    long_description="""Logging usage of Python-based services, with user privacy by design.

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
""",
    long_description_content_type='text/markdown',
    url='https://resurface.io',
    author='Resurface Labs',
    author_email='admin@resurface.io',
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: Log Analysis',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9'
    ],
    keywords='logging resurface',
    packages=['usagelogger'],
    python_requires='>=3.7, <4',
    install_requires=[],
    tests_require=['pytest'],
    project_urls={
        'Bug Reports': 'https://github.com/resurfaceio/logger-python/issues',
        'Source': 'https://github.com/resurfaceio/logger-python'
    }
)
