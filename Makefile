include .env
export


services:
	docker-compose -f docker-compose.services.yml up

makemigrations:
	PYTHONPATH=. alembic revision --autogenerate

migrate:
	PYTHONPATH=. alembic upgrade head

dev:
	uvicorn main:app --host 0.0.0.0 --reload

psql:
	psql -h localhost -U postgres -d postgres

format:
	chmod +x ./.github/lint.sh
	./.github/lint.sh format

run_tests:
	pytest .

mypy:
	chmod +x ./.github/lint.sh
	./.github/lint.sh check-mypy

lint:
	chmod +x ./.github/lint.sh
	./.github/lint.sh check-isort
	./.github/lint.sh check-black
	./.github/lint.sh check-flake8
	./.github/lint.sh check-mypy