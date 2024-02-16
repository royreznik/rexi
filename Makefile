BUMP_PART ?=
PYTEST_COV ?= xml

POETRY ?= poetry

setup:
	python3 -m pip install poetry

install:
	$(POETRY) install

test:
	$(POETRY) run pytest -ssv --cov --cov-report=$(PYTEST_COV)

build:
	$(POETRY) build

publish: build
	$(POETRY) publish

format:
	$(POETRY) run ruff format rexi/ tests/
	$(POETRY) run ruff --fix rexi/ tests/

lint:
	$(POETRY) run ruff rexi/ tests/
	$(POETRY) run mypy rexi/ tests/

bump:
	$(POETRY) run bump-my-version bump $(BUMP_PART)