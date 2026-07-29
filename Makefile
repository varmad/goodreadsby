# Walking skeleton (SCRUM-2). One command per moving part.
.PHONY: help db-up db-down seed ingest api web api-test

help:
	@echo "Targets:"
	@echo "  db-up     start local Postgres (docker compose)"
	@echo "  db-down   stop local Postgres"
	@echo "  seed      rebuild the skeleton's data from empty"
	@echo "  ingest    load Open Library dumps: make ingest FILES=\"authors.txt works.txt editions.txt\""
	@echo "  api       run the FastAPI service on :8000"
	@echo "  web       run the Next.js public site on :3000"
	@echo "  api-test  run the API unit tests"

db-up:
	docker compose up -d db

db-down:
	docker compose down

seed:
	cd api && python -m app.seed

# Load Open Library monthly dumps into our own Works and Editions (SCRUM-4).
# Pass authors before works so a work resolves its author's name. Idempotent and
# resumable, so re-running or restarting after an interruption is safe.
ingest:
	cd api && python -m app.ingest $(FILES)

api:
	cd api && uvicorn app.main:app --reload --port 8000

web:
	cd web && npm run dev

api-test:
	cd api && python -m unittest discover -s tests
