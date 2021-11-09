from distutils import util

from setuptools import setup


def read_file(name):
    with open(name) as fd:
        return fd.read()


middleware = util.convert_path("usagelogger/middleware")
utils = util.convert_path("usagelogger/utils")
artifacts = util.convert_path("usagelogger/artifacts")

setup(
    name="usagelogger",
    version="2.2.6",
    description="Logging usage of Python-based services, with user privacy by design.",
    long_description=read_file("DESCRIPTIONS.md"),
    long_description_content_type="text/markdown",
    url="https://resurface.io",
    author="Resurface Labs",
    author_email="admin@resurface.io",
    license="Apache License 2.0",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: System Administrators",
        "Topic :: Internet :: Log Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    keywords="logging resurface",
    package_dir={
        "usagelogger": "usagelogger",
        "usagelogger.middleware": middleware,
        "usagelogger.utils": utils,
        "usagelogger.artifacts": artifacts,
    },
    packages=[
        "usagelogger",
        "usagelogger.middleware",
        "usagelogger.utils",
        "usagelogger.artifacts",
    ],
    # packages=find_packages(exclude=["tests"]),
    python_requires=">=3.7, <4",
    install_requires=["requests>=2", "joblib>=1.0.1"],
    include_package_data=True,
    tests_require=["pytest"],
    project_urls={
        "Bug Reports": "https://github.com/resurfaceio/logger-python/issues",
        "Source": "https://github.com/resurfaceio/logger-python",
    },
)
