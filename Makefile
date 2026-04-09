.PHONY: test lint format-check

test:
	python -m unittest discover -s tests -p "test_*.py"

lint:
	ruff check .

format-check:
	ruff format --check .
