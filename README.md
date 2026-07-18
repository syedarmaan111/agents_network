# Agents Network

FastAPI service for the Agents Network project.

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
