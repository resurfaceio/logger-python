from setuptools import setup

setup(
    name='usagelogger',
    version='0.1.5',
    description='Logging usage of Python cloud apps',
    long_description='© 2016-2019 Resurface Labs Inc.\n\nLogging usage of Python cloud apps, with user privacy by design.',
    long_description_content_type='text/plain',
    url='https://github.com/resurfaceio/logger-python',
    author='Resurface Labs',
    author_email='admin@resurface.io',
    license="Apache License 2.0",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: Internet :: Log Analysis',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    keywords='logging resurface',
    packages=['usagelogger'],
    python_requires='>=3.4, <4',
    install_requires=[],
    tests_require=['expects', 'mamba'],
    project_urls={
        'Bug Reports': 'https://github.com/resurfaceio/logger-python/issues',
        'Source': 'https://github.com/resurfaceio/logger-python'
    }
)
