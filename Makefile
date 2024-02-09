BUMP_PART ?=

setup:
	python3 -m pip install poetry

install:
	poetry install

test:
	poetry run pytest -ssv --cov --cov-report=html

build:
	poetry build

publish: build
	poetry publish

format:
	poetry run ruff --fix rexi/ tests/
	poetry run ruff format rexi/ tests/

lint:
	poetry run ruff rexi/ tests/
	poetry run mypy rexi/ tests/

bump:
	poetry run bump-my-version bump $(BUMP_PART)