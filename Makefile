install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check page_analyzer

PORT ?= 8000
start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

test:
	uv run pytest

.PHONY: db-init
db-init:
	@echo "Инициализация базы данных..."
	@# Загружаем .env через оболочку
	@eval $$(cat .env | sed 's/^/export /') && \
	if [ -z "$$DATABASE_URL" ]; then \
		echo "Ошибка: DATABASE_URL не задан в .env файле"; \
		exit 1; \
	fi
	@# Создаём базу данных (если её нет)
	@eval $$(cat .env | sed 's/^/export /') && \
	PGPASSWORD=$$(echo $$DATABASE_URL | sed -n 's/.*:\/\/.*:\(.*\)@.*/\1/p') \
	psql "$$DATABASE_URL" -c "CREATE DATABASE $$(echo $$DATABASE_URL | sed -n 's/.*\/\(.*\)$$/\1/p')" 2>/dev/null || true
	@# Выполняем SQL-скрипт
	@eval $$(cat .env | sed 's/^/export /') && \
	PGPASSWORD=$$(echo $$DATABASE_URL | sed -n 's/.*:\/\/.*:\(.*\)@.*/\1/p') \
	psql "$$DATABASE_URL" -f database.sql
	@echo "✅ База данных и таблицы созданы!"
