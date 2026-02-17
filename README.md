# ShadowPlant AI

Factory Performance Intelligence with FastAPI + Vue.

## Core Architecture
- `backend/app/domain`: entities + anomaly/forecast domain logic
- `backend/app/application`: use-cases/DTO orchestration
- `backend/app/infrastructure`: SQLAlchemy models/repos/security/logging/metrics
- `backend/app/api`: routers/dependencies/schemas

## Local MVP (existing)
1. Copy `.env.example` to `.env`.
2. `docker compose up --build`
3. `make migrate && make seed`
4. Open UI at `http://localhost:5173`

Default users:
- `admin/admin123`
- `viewer/viewer123`

## OT-Safe Production Deployment

### Zone Diagram (IEC-62443 style)

```text
                         IT ZONE
     +---------------------------------------------------+
     | Corporate users / BI / ticketing / email          |
     |                                                   |
     |  HTTPS 443 (approved)                            |
     |      |                                            |
     +------|--------------------------------------------+
            v
+----------------------------------------------------------------+
| INDUSTRIAL DMZ (ShadowPlant analytics layer)                   |
|                                                                |
|  +--------------------+      8000/tcp       +---------------+  |
|  | shadowplant-proxy  | ------------------> | shadowplant-  |  |
|  | (nginx TLS, :443)  |  /api               | api (FastAPI) |  |
|  | routes /ui + /api  |                     +---------------+  |
|  |                    | ----> /ui ----------> shadowplant-ui |  |
|  +--------------------+                     (static nginx)    |  |
|            ^                              +---------------+   |  |
|            |                    5432/tcp  | shadowplant-db |<--+ |
|            |                              +---------------+   |  |
|            |                                      ^           |  |
|            |                                      |           |  |
|            |                               shadowplant-worker |  |
|            |                           (heartbeat + jobs)     |  |
|            |                                                  |  |
|  ot_ingest net ---> shadowplant-collector (read-only ingest) |  |
+----------------------------------------------------------------+
            ^
            |
            | one-way push/scheduled pull (preferred)
            |
+----------------------------------------------------------------+
| OT ZONE                                                          |
| PLCs | SCADA | Historians | MES DB                               |
| No direct write path from ShadowPlant                            |
+----------------------------------------------------------------+
```

### Allowed Flows and Ports
- `OT -> DMZ`:
  - Data drop/push into collector inbox (preferred one-way path)
  - Optional scheduled pull from DMZ collector to approved OT endpoints
- `IT -> OT`: blocked
- `IT -> DMZ`: `443/tcp` to `shadowplant-proxy` only
- `DMZ internal only`:
  - `shadowplant-api:8000`
  - `shadowplant-db:5432`
  - `shadowplant-collector -> shadowplant-api:8000`
- `Optional observability (restricted)`:
  - `9090/tcp` Prometheus (localhost bind by default)
  - `3000/tcp` Grafana (localhost bind by default)

### Deployment Profiles
Profile composition is defined in `docker-compose.deploy.yml`.

- `edge` (recommended):
  - Runs all analytics components in DMZ (`api`, `worker`, `db`, `ui`, `proxy`, optional `collector`)
- `hybrid`:
  - Same DMZ core, exposed to IT consumers through `proxy` on `443`
  - Collector remains in DMZ with OT-facing ingest path
- `dev`:
  - Same container topology for local validation

### Files Added for Deployment
- Compose profiles: `docker-compose.deploy.yml`
- Nginx reverse proxy: `deploy/nginx/shadowplant.conf`
- Self-signed TLS helper: `deploy/tls/generate-self-signed.sh`
- Prometheus scrape config: `deploy/prometheus/prometheus.yml`
- Environment templates: `.env.edge.example`, `.env.hybrid.example`

### Step-by-Step (Edge Mode, Offline-Capable)
1. Copy `.env.edge.example` to `.env.edge` and set secrets.
2. Generate certs:
   - `./deploy/tls/generate-self-signed.sh`
3. Start stack:
   - `docker compose --env-file .env.edge -f docker-compose.deploy.yml --profile edge up -d --build`
4. Verify:
   - `https://<dmz-host>/healthz`
   - `https://<dmz-host>/api/healthz`
   - `https://<dmz-host>/api/readyz`
5. Load data (collector): drop CSVs into `collector/inbox/`.

Runtime internet is not required after images/dependencies are preloaded in the environment.

### Step-by-Step (Hybrid Mode)
1. Copy `.env.hybrid.example` to `.env.hybrid` and set secrets.
2. Generate certs:
   - `./deploy/tls/generate-self-signed.sh`
3. Start stack:
   - `docker compose --env-file .env.hybrid -f docker-compose.deploy.yml --profile hybrid up -d --build`
4. Share `https://<dmz-or-approved-proxy-host>/ui/` with IT users.

### Health and Readiness
- Liveness: `GET /healthz`
- Readiness: `GET /readyz`
  - DB connectivity check
  - Alembic migration revision check
  - Worker heartbeat freshness check

Legacy endpoint `GET /health` remains for compatibility.

### Security Controls (Least Privilege)
- No ShadowPlant direct writes to OT assets.
- API and DB are not published externally.
- TLS termination at `shadowplant-proxy` with strict headers.
- Reverse-proxy path isolation (`/api`, `/ui`).
- Collector uses least-privileged API account and read-only inbox pattern.

### Single-Node Baseline and HA-Ready Notes
Single-node baseline:
- Persistent volumes:
  - `pgdata` (database)
  - `heartbeat` (worker readiness signal)
  - `promdata`, `grafanadata` (optional)
- Restart policies: `unless-stopped` for long-running services

HA-ready expansion:
- Externalize Postgres to managed or replicated cluster.
- Add automated DB backups (daily full + WAL archive/PITR).
- Put nginx behind redundant DMZ load balancers.
- Move collector inbox to durable message bus or replicated file share.
- Enforce retention:
  - DB data lifecycle by policy
  - Prometheus retention via `PROM_RETENTION`

## Commands
- `make dev`: start legacy local stack
- `make migrate`: run Alembic
- `make seed`: generate synthetic data
- `make test`: run backend tests
- `make lint`: run ruff + black checks

## API Highlights
- `POST /auth/login`
- `POST /datasets/upload` (admin only)
- `GET /datasets`
- `GET /kpi/overview?date=YYYY-MM-DD`
- `GET /kpi/machines?from=YYYY-MM-DD&to=YYYY-MM-DD&machine_id=M-100`
- `GET /kpi/shifts?from=YYYY-MM-DD&to=YYYY-MM-DD&machine_id=M-100`
- `GET /kpi/days?from=YYYY-MM-DD&to=YYYY-MM-DD&machine_id=M-100`
- `GET /anomalies?from=...&to=...&severity=high&limit=50&offset=0`
- `GET /forecasts?machine_id=M-100&horizon_days=3`
- `GET /insights?date=YYYY-MM-DD`
- `GET /metrics`
- `GET /healthz`
- `GET /readyz`
