.PHONY: help install install-dev clean build deploy wizard test dev setup

help:
	@echo "Available commands:"
	@echo "  make install      - Install basic Python dependencies"
	@echo "  make install-dev  - Install all development dependencies"
	@echo "  make install-video - Install video processing dependencies"
	@echo "  make setup        - Complete setup (Python + Node dependencies)"
	@echo "  make build        - Build static site from listings"
	@echo "  make wizard       - Run interactive wizard"
	@echo "  make deploy       - Deploy to Netlify"
	@echo "  make dev          - Start local development server"
	@echo "  make clean        - Remove generated files and caches"
	@echo "  make test         - Run tests"

install:
	pip install -r requirements.txt

install-dev:
	pip install -e ".[dev]"
	npm install

install-video:
	pip install -e ".[video]"
	@echo "Note: Ensure ffmpeg is installed on your system"
	@echo "  macOS: brew install ffmpeg"
	@echo "  Ubuntu: sudo apt-get install ffmpeg"
	@echo "  Windows: Download from https://ffmpeg.org/download.html"

setup: install
	npm install
	@echo "Setup complete! Run 'make wizard' to start creating a listing."

build:
	python site.py build

wizard:
	python site.py wizard

deploy:
	@if [ -d "dist" ]; then \
		netlify deploy --prod --dir=dist; \
	else \
		echo "Error: dist/ directory not found. Run 'make build' first."; \
		exit 1; \
	fi

dev:
	@if [ -d "dist" ]; then \
		python -m http.server 8000 --directory dist; \
	else \
		echo "Error: dist/ directory not found. Run 'make build' first."; \
		exit 1; \
	fi

clean:
	rm -rf __pycache__ .pytest_cache .mypy_cache .ruff_cache
	rm -rf dist/ output/ generated-assets/ video_output/
	rm -rf node_modules/
	rm -f *.log
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

test:
	@echo "No tests configured yet"
	@echo "To add tests, create a tests/ directory and update this command"

format:
	black *.py
	ruff check --fix *.py

lint:
	black --check *.py
	ruff check *.py
	mypy *.py --ignore-missing-imports