# Agents Network

FastAPI service for the Agents Network project.

## Run everything with Docker (recommended)

This starts the frontend, backend, and a private PostgreSQL database. Install and
open Docker Desktop first, then run these commands from this directory:

```powershell
Copy-Item .env.example .env  # only if .env does not already exist
# In .env, set APP_POSTGRES_PASSWORD and APP_JWT_SECRET_KEY to long random values.
docker compose up --build
```

If you already have a `.env`, keep your existing API keys and add the four
`APP_POSTGRES_*` / `APP_JWT_SECRET_KEY` entries from `.env.example`. Docker ignores
the existing `APP_DATABASE_URL` value and uses its own database container.

Open `http://localhost:8080`. The API is available at `http://localhost:8000/docs`.
Stop the stack with `docker compose down`. Your database is retained in the
`postgres_data` Docker volume. To remove the database too, run
`docker compose down -v`.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt   # runtime + dev deps
cp .env.example .env
```

## Run

```bash
export PYTHONPATH=src
uvicorn app.main:app --reload
```

The API is served at `http://127.0.0.1:8000`, interactive docs at `/docs`.

## Health check

```bash
curl http://127.0.0.1:8000/api/health
# {"status":"ok"}
```

## API versioning

Routes are grouped by version under `src/app/api/`. `src/app/api/v1/__init__.py` builds an `APIRouter(prefix="/api/v1")` and includes each route module from `src/app/api/v1/routes/`. To add a new version, create `src/app/api/v2/` with the same shape and mount it in [main.py](src/app/main.py) alongside `v1`.

## Configuration

Settings are loaded from environment variables (prefix `APP_`) or a `.env` file — see [.env.example](.env.example).

## Dependencies

- `requirements.txt` — runtime dependencies
- `requirements-dev.txt` — runtime + dev/test dependencies

Add new packages with `pip install <package>`, then pin the version in the relevant requirements file.
