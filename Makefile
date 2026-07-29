# Walking skeleton (SCRUM-2). One command per moving part.
.PHONY: help db-up db-down seed api web api-test

help:
	@echo "Targets:"
	@echo "  db-up     start local Postgres (docker compose)"
	@echo "  db-down   stop local Postgres"
	@echo "  seed      rebuild the skeleton's data from empty"
	@echo "  api       run the FastAPI service on :8000"
	@echo "  web       run the Next.js public site on :3000"
	@echo "  api-test  run the API unit tests"

db-up:
	docker compose up -d db

db-down:
	docker compose down

seed:
	cd api && python -m app.seed

api:
	cd api && uvicorn app.main:app --reload --port 8000

web:
	cd web && npm run dev

api-test:
	cd api && python -m unittest discover -s tests
