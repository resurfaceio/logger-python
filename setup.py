from setuptools import find_packages, setup


def read_file(name):
    with open(name) as fd:
        return fd.read()


setup(
    name="usagelogger",
    version="2.2.4",
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
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.7, <4",
    install_requires=read_file("requirements.txt").splitlines(),
    include_package_data=True,
    tests_require=["pytest"],
    project_urls={
        "Bug Reports": "https://github.com/resurfaceio/logger-python/issues",
        "Source": "https://github.com/resurfaceio/logger-python",
    },
)
