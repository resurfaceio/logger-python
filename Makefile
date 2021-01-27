# Makefile
SHELL := /bin/bash

## Configuration

BUILD_TIME := $(shell date +%FT%T%z)
PROJECT    := $(shell basename $(PWD))




## Setup developpement environment
setup-dev:
	python -m venv .venv
	source .venv/bin/activate
	pip install -r requirements_dev.txt


run-test:
	pytest

precommit-check:
	pre-commit run --all-files
