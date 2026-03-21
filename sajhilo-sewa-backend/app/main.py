from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app import models
from app.routers import auth, gestures, stats

app = FastAPI(title="Sajhilo Sewa API")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"DEBUG: {request.method} {request.url.path}")
    try:
        response = await call_next(request)
        print(f"DEBUG: Response {response.status_code}")
        return response
    except Exception as e:
        print(f"DEBUG: Middleware Exception: {e}")
        raise

# ── Create all tables on startup ──────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

# ── CORS — allow your React frontend ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(gestures.router)
app.include_router(stats.router)

# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/")
def read_root():
    return {"Hello": "World"}