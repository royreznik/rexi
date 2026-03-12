BUMP_PART ?=
PYTEST_COV ?= xml
setup:
	python3 -m pip install uv

install:
	uv sync

test:
	uv run pytest -ssv --cov --cov-report=$(PYTEST_COV)

build:
	uv build

publish: build
	uv publish

format:
	uv run ruff format rexi/ tests/
	uv run ruff --fix rexi/ tests/

lint:
	uv run ruff rexi/ tests/
	uv run mypy rexi/ tests/

bump:
	uv run bump-my-version bump $(BUMP_PART)
