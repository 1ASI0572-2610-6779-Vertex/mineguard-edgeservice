# MineGuard Smart Band Edge Service (`untitledEdge`)

Lightweight IoT **edge** API that ingests heart-rate (`bpm`) telemetry emitted by
smart-band devices and **synchronizes it with the MineGuard cloud platform**.
Built with a Domain-Driven Design (DDD) layered architecture, mirroring the
bounded contexts of the MineGuard RESTful API.

It is the edge counterpart of the MineGuard platform: the platform exposes
`POST /api/v1/health-monitoring/data-records` (authenticated by device
`X-API-Key`) and raises fatigue alerts on abnormal readings — this edge buffers
readings locally (SQLite) and pushes them to that endpoint.

## Bounded Contexts

Same context map as the MineGuard platform (only the ones the edge needs are
populated; the rest are reserved packages kept for alignment):

- **iam** — device identity & authentication (`Device`, `X-API-Key`).
- **monitoring** — heart-rate ingestion (`HeartRateReading`), local persistence
  and cloud synchronization (MineGuard anti-corruption client).
- **subscriptions, profile, planning, analytics, assets** — reserved (empty).
- **shared** — SQLite database and configuration.

Each context follows the edge layered structure: `domain/`, `application/`,
`infrastructure/`, `interfaces/`.

## Tech Stack

- Python 3.13+ · Flask · Peewee · SQLite · python-dateutil · requests

## Getting Started

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py            # edge runs on http://127.0.0.1:5001
```

The database (`smart_band_edge.db`) and the test device are created on the first
request.

## Configuration (environment variables)

| Variable | Description | Default |
|---|---|---|
| `MINEGUARD_API_URL` | Base URL of the MineGuard platform | `http://localhost:8080` |
| `MINEGUARD_HEALTH_PATH` | Cloud ingestion path | `/api/v1/health-monitoring/data-records` |
| `MINEGUARD_SYNC_ENABLED` | Push readings to the cloud | `true` |
| `MINEGUARD_SYNC_TIMEOUT` | Cloud HTTP timeout (s) | `5` |
| `EDGE_TEST_DEVICE_ID` | Seeded device id | `smart-band-001` |
| `EDGE_TEST_DEVICE_API_KEY` | Seeded device API key | `test-api-key-123` |

> The seeded device credentials match the device seeded in the MineGuard backend,
> so synchronization works out-of-the-box against a local platform instance.

## API Contract

### Create a heart-rate record
`POST /api/v1/health-monitoring/data-records`

Headers: `Content-Type: application/json`, `X-API-Key: <device api key>`

```json
{ "device_id": "smart-band-001", "bpm": 72.5, "created_at": "2025-06-04T18:23:00-05:00" }
```

`201 Created`:
```json
{ "id": 1, "device_id": "smart-band-001", "bpm": 72.5,
  "created_at": "2025-06-04T23:23:00+00:00Z", "synced": true, "cloud_id": 1 }
```
- `synced` / `cloud_id` reflect whether the reading reached the MineGuard cloud.
- Errors: `400` (missing/invalid fields), `401` (missing/invalid credentials).

### Flush buffered readings to the cloud
`POST /api/v1/health-monitoring/sync` (header `X-API-Key`)

Retries every reading with `synced = false`. `200 OK`:
```json
{ "pending": 3, "synced": 3, "failed": 0 }
```

### Edge readiness
`GET /health` → `{ "status": "ok", "cloud": "...", "syncEnabled": true }`

## How synchronization works

1. A smart band POSTs a reading to the edge.
2. IAM validates the device (`device_id` + `X-API-Key`).
3. Monitoring validates the BPM, stores the reading locally, then pushes it to
   the MineGuard platform via the anti-corruption client
   (`monitoring/infrastructure/mineguard_client.py`).
4. If the cloud is unreachable the reading stays `synced = false` and can be
   flushed later via `POST /api/v1/health-monitoring/sync` (store-and-forward).

## Development Test Device

`device_id = smart-band-001`, `api_key = test-api-key-123` (development only).
