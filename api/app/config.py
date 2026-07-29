"""Runtime configuration, read from the environment.

Secrets (the database URL) live in the platform's environment, never in the repo
(see SCRUM-3). The default points at the local docker-compose Postgres so the
skeleton runs out of the box in development.
"""

from __future__ import annotations

import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://goodreadsby:goodreadsby@localhost:5432/goodreadsby",
)
