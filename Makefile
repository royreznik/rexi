BUMP_PART ?=

setup:
	python3 -m pip install poetry

install:
	poetry install

test:
	poetry run pytest -ssv --cov --cov-report=xml

build:
	poetry build

publish: build
	poetry publish

format:
	poetry run black rexi/ tests/

lint:
	poetry run ruff rexi/ tests/
	poetry run mypy rexi/ tests/

bump:
	poetry run bump-my-version bump $(BUMP_PART)