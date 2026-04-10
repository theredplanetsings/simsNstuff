.PHONY: test lint format-check quality run

test:
	python -m pytest -q

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

quality: test lint format-check

run:
	python -m streamlit run mineral_3d_model.py
