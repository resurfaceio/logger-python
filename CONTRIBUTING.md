# Contributing

## Coding Conventions

For the code linting and formatting, we use both black and flake8. Pre-commit hooks are implemented to automate the formatting and linting before commit.

## Git Workflow

```bash
$ git clone git@github.com:resurfaceio/logger-python.git resurfaceio-logger-python
$ cd resurfaceio-logger-python


## Create python virtual env and activate
$ python -m venv .venv
$ source .venv/bin/activate

## Install dev requirements
$ pip install -r requirements_dev.txt

## Restart env after requirements installation

$ deactivate
$ source .venv/bin/activate
```

Running unit tests:

```
$ pytest
```

## Install pre-commit hooks

$ pre-commit install

Precommit check:

```
$ pre-commit run --all-files
```

Committing changes:

```bash
$ git add -A
$ git commit -m "#123 Updated readme"       (123 is the GitHub issue number)
$ git pull --rebase                         (avoid merge bubbles)
$ git push origin master
```

## Release Process

All [integration tests](https://github.com/resurfaceio/logger-tests) must pass first.

Push artifacts to [pypi.org](https://pypi.org/):

```bash
$ python setup.py sdist bdist_wheel
$ twine check dist/*
$ twine upload dist/*
```

Tag release version:

```bash
$ git tag v2.x.x
$ git push origin master --tags
```

Start the next version by incrementing the version number in both `setup.py` and `__init__.py` files.
