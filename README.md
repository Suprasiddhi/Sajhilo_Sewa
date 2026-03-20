# Sajhilo Sewa 


- `sajhilo-sewa-frontend` (React app)
- `sajhilo-sewa-backend` (FastAPI app)
- PostgreSQL database (via Docker)

## Quick Start (Recommended)

-Run the project
```bash
cd Sajhilo_Sewa
docker compose up -d --build
```

Open:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Postgres: `localhost:5433`

Stop all services:

```bash
docker compose down
```

View logs:

```bash
docker compose logs -f
```


### Frontend

- Path: `sajhilo-sewa-frontend`
- Container port: `3000`
- Host port: `3000`
- API base URL in container setup: `http://localhost:8000`

### Backend

- Path: `sajhilo-sewa-backend`
- Host/container port: `8000`
- Uses `DATABASE_URL` from Docker Compose:
  - `postgresql://postgres:Supra@db:5432/sajhilosewadb`

### Database

- Image: `postgres:16-alpine`
- Host port: `5433`
- Credentials:
  - DB: `sajhilosewadb`
  - User: `postgres`
  - Password: `Supra`

## Local Run Without Docker


### 1) Backend

```bash
cd sajhilo-sewa-backend
python3 -m venv .venv-linux
source .venv-linux/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Set your local `.env` for backend database connection if not using Docker DB.

### 2) Frontend

```bash
cd sajhilo-sewa-frontend
npm install
npm run dev
```

## Common Commands

Rebuild containers after dependency changes:

```bash
docker compose up -d --build
```

Restart only one service:

```bash
docker compose restart backend
docker compose restart frontend
```

Check container status:

```bash
docker compose ps
```
