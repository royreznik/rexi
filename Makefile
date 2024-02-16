BUMP_PART ?=
PYTEST_COV ?= xml
setup:
	python3 -m pip install poetry

install:
	poetry install

test:
	poetry run pytest -ssv --cov --cov-report=$(PYTEST_COV)

build:
	poetry build

publish: build
	poetry publish

format:
	poetry run ruff format rexi/ tests/
	poetry run ruff --fix rexi/ tests/

lint:
	poetry run ruff rexi/ tests/
	poetry run mypy rexi/ tests/

bump:
	poetry run bump-my-version bump $(BUMP_PART)
