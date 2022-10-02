.DEFAULT_GOAL := help
.PHONY: deps help lint push test format check

deps:  ## Install dependencies
	pip install -e .
	pip install -e .[dev]

format:  ## Code formatting
	black linkrot

lint:  ## Linting
	flake8 linkrot

check:  ## Lint and static-check
	pylint linkrot
	mypy linkrot

test:  ## Run tests
	pytest -ra

push:  ## Push code with tags
	git push && git push --tags

coverage:  ## Run tests with coverage
	coverage erase
	coverage run --include=linkrot/* -m pytest -ra
	coverage report -m
