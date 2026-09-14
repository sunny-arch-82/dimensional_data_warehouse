.PHONY: setup run seed build reconcile test status logs teardown clean

setup:
	@test -f .env || (echo "Creating .env from .env.example" && cp .env.example .env)
	docker compose config -q
	docker compose pull postgres cube metabase
	docker compose build dagster-webserver dagster-daemon
	docker compose up -d postgres
	docker compose up -d dagster-webserver dagster-daemon
	docker compose exec dagster-webserver bash -lc "cd /opt/dagster/app/dbt_project && dbt seed --profiles-dir . --full-refresh && dbt build --profiles-dir ."
	docker compose up -d cube metabase
	@echo "Setup complete. Dagster: http://localhost:3000 | Cube: http://localhost:4000 | Metabase: http://localhost:3001"

run:
	docker compose up -d

seed:
	docker compose exec dagster-webserver bash -lc "cd /opt/dagster/app/dbt_project && dbt seed --profiles-dir . --full-refresh"

build:
	docker compose exec dagster-webserver bash -lc "cd /opt/dagster/app/dbt_project && dbt build --profiles-dir ."

reconcile:
	docker compose exec dagster-webserver python scripts/reconcile_metrics.py

test:
	docker compose exec dagster-webserver bash -lc "cd /opt/dagster/app/dbt_project && dbt test --profiles-dir ."
	docker compose exec dagster-webserver pytest -q

status:
	docker compose ps

logs:
	docker compose logs --tail=120

teardown:
	docker compose down

clean:
	docker compose down -v --remove-orphans
