.PHONY: help install migrate test run clean docker-build docker-up docker-down

help:
	@echo "FFPAS v2.0 - Available Commands"
	@echo "================================"
	@echo "install       - Install dependencies"
	@echo "migrate       - Run database migration"
	@echo "test          - Run tests"
	@echo "test-cov      - Run tests with coverage"
	@echo "run           - Start development server"
	@echo "clean         - Clean cache and temp files"
	@echo "docker-build  - Build Docker image"
	@echo "docker-up     - Start Docker containers"
	@echo "docker-down   - Stop Docker containers"
	@echo "lint          - Run code linting"
	@echo "format        - Format code with black"

install:
	pip install -r requirements.txt

migrate:
	python database/migrate.py

test:
	pytest

test-cov:
	pytest --cov=. --cov-report=html --cov-report=term

run:
	python start.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf htmlcov/
	rm -f .coverage

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f ffpas

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

format:
	black . --line-length 100

dev:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 5000
