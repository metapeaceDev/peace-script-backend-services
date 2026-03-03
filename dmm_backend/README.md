# Digital Mind Model API (Backend)

FastAPI + Beanie/MongoDB backend for the Digital Mind Model.

## Quickstart

1) Create .env

Copy the sample and adjust values if needed:

```
cp .env.example .env
```

Ensure Mongo is available (local or Atlas) and API key is set:

```
API_KEY=YOUR_SECRET_API_KEY
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=digital_mind_model
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

For cloud clusters (e.g., MongoDB Atlas) the URI can be a full SRV string, for example:

```
MONGO_URI=mongodb+srv://USER:PASSWORD@cluster0.example.mongodb.net/digital_mind_model?retryWrites=true&w=majority
```

2) Install backend deps into the local venv (recommended)

```
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

3) Seed sample data (optional for local dev)

```
./venv/bin/python -c "import os,sys; sys.path.insert(0, os.getcwd()); import asyncio; import seed_db; asyncio.run(seed_db.seed_database())"
```

4) Run the API

Fast path (from repo root, recommended):

```
make backend
# หรือเรียกตรงๆ: ./scripts/start_backend.sh
```

Manual (from this folder):

```
PYTHONPATH=. ./venv/bin/uvicorn main:app --host 127.0.0.1 --port 8000 --env-file .env
```

Or from repo root if you prefer the dotted module path:

```
dmm_backend/venv/bin/uvicorn dmm_backend.main:app --app-dir dmm_backend --host 127.0.0.1 --port 8000 --env-file dmm_backend/.env
```

5) Smoke test

```
curl http://127.0.0.1:8000/health
curl -H "X-API-KEY: $API_KEY" http://127.0.0.1:8000/models/
python ../scripts/smoke_backend.py  # in-process check hitting Mongo-backed endpoints
```

## Testing

Run backend tests:

```
./venv/bin/pytest -q tests
```

## Notes

- CORS is configured from `.env` via `CORS_ORIGINS`.
- API requires `X-API-KEY` for protected routes.
- For dev, the frontend uses `VITE_API_BASE_URL` and `VITE_API_KEY` to call the backend.

## P0 Endpoints (Dreams & Timelines)

All routes below require the header:

```
X-API-KEY: YOUR_SECRET_API_KEY
```

Dream Journals
- GET /api/v1/dream-journals/?model_id={id}&skip={n}&limit={m}
	- Sorted by _id desc for stable pagination
	- Optional cursor: after_id (ObjectId string). When provided, returns docs with _id < after_id.
- POST /api/v1/dream-journals/
- GET /api/v1/dream-journals/{dream_id}
- PATCH /api/v1/dream-journals/{dream_id}
- PUT /api/v1/dream-journals/{dream_id}
- DELETE /api/v1/dream-journals/{dream_id}

Simulation Timelines
- GET /api/v1/simulation-timelines/?model_id={id}&skip={n}&limit={m}
	- Sorted by _id desc for stable pagination
	- Optional cursor: after_id (ObjectId string). When provided, returns docs with _id < after_id.
- POST /api/v1/simulation-timelines/
- GET /api/v1/simulation-timelines/{timeline_id}
- PATCH /api/v1/simulation-timelines/{timeline_id}
- PUT /api/v1/simulation-timelines/{timeline_id}
- DELETE /api/v1/simulation-timelines/{timeline_id}

### Curl examples

Create Dream:

```
curl -sS -H "X-API-KEY: $API_KEY" -H "Content-Type: application/json" \
	-d '{
		"model_id":"peace-mind-001",
		"dream_text":"A clear stream and a bright moon.",
		"tags":["calm","clarity"],
		"emotion_score":0.9
	}' \
	http://127.0.0.1:8000/api/v1/dream-journals/
```

List Dreams:

```
curl -sS -H "X-API-KEY: $API_KEY" \
	"http://127.0.0.1:8000/api/v1/dream-journals/?skip=0&limit=50" -i
```

Create Timeline:

```
curl -sS -H "X-API-KEY: $API_KEY" -H "Content-Type: application/json" \
	-d '{
		"model_id":"peace-mind-001",
		"simulation_id":"sim-001",
		"timeline_type":"physical",
		"events":[{"type":"start","payload":{"note":"begin"}}]
	}' \
	http://127.0.0.1:8000/api/v1/simulation-timelines/
```

List Timelines for a model:

```
curl -sS -H "X-API-KEY: $API_KEY" \
	"http://127.0.0.1:8000/api/v1/simulation-timelines/?model_id=peace-mind-001&skip=0&limit=50" -i

Pagination headers returned on list endpoints:
- X-Page-Skip, X-Page-Limit, X-Returned, X-Next-Skip
- X-Total-Count, X-Has-More (when count available)
- X-Next-After-Id (cursor for next page when using after_id)

Cursor pagination example (Dreams):

1) First page (inspect X-Next-After-Id):

```
curl -sS -H "X-API-KEY: $API_KEY" \
	"http://127.0.0.1:8000/api/v1/dream-journals/?limit=3" -i
```

2) Next page, using after_id from the previous response header:

```
AFTER_ID="<paste X-Next-After-Id>"
curl -sS -H "X-API-KEY: $API_KEY" \
	"http://127.0.0.1:8000/api/v1/dream-journals/?limit=3&after_id=${AFTER_ID}" -i
```

## Health and Metrics

- Health endpoint: `/health` (no auth). It performs a Mongo ping and returns basic DB info.
	Example:

	```
	curl -sS http://127.0.0.1:8000/health | jq
	```

- Prometheus metrics: `/metrics` (no auth). Exposes request counters and latency histograms.

## VS Code Tasks

We provide helpful tasks under `.vscode/tasks.json`:

- Run backend (local venv)
- Run frontend (Vite)
- Seed database
- Run backend tests

Use Terminal > Run Task… in VS Code to start them.
```
