.PHONY: help install setup train init-kb run-api run-streamlit docker-build docker-up docker-down test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make setup        - Initial setup (install + init KB)"
	@echo "  make train        - Train ML model"
	@echo "  make init-kb      - Initialize knowledge base"
	@echo "  make run-api      - Run FastAPI server"
	@echo "  make run-streamlit - Run Streamlit app"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start services with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose services"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean temporary files"

install:
	pip install -r requirements.txt

setup: install init-kb
	@echo "Setup complete!"

train:
	python scripts/train_model.py

init-kb:
	python scripts/initialize_knowledge_base.py

run-api:
	uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

run-streamlit:
	streamlit run src/app/main.py --server.port 8501

docker-build:
	docker build -t investment-assistant .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

test:
	pytest tests/ -v

lint:
	ruff check src/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	rm -rf .pytest_cache
	rm -rf .ruff_cache

