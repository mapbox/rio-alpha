SHELL = /bin/bash

.PHONY: install test

install:
	pip install -U pip
	pip install wheel
	pip wheel numpy
	pip install --use-wheel numpy
	pip wheel -r requirements.txt
	pip install --use-wheel -r requirements.txt
	pip wheel -r requirements-dev.txt
	pip install --use-wheel -r requirements-dev.txt
	pip install -e .[test]
	pip install -e .[plot]

test:
	py.test --cov rio_alpha --cov-report term-missing --ignore=venv
