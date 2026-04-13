.PHONY: test test-verbose lint format-check quality smoke clean run

test:
	python -m pytest -q

test-verbose:
	python -m pytest -v

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

quality: test lint format-check

smoke:
	python -m compileall .

clean:
	rm -rf .pytest_cache */__pycache__ __pycache__ .ruff_cache

run:
	python -m streamlit run mineral_3d_model.py
