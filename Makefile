install:
	poetry install

dev:
	poetry run flask --app page_analyzer:app run

pbuild:
	poetry build

build:
	./build.sh

publish:
	poetry publish --dry-run

lint:
	poetry run flake8 page_analyzer

test-coverage:
	poetry run pytest --cov=page_analyzer --cov-report xml

test:
	poetry run pytest

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app