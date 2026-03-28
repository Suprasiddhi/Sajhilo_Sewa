from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.database import Base, engine, SessionLocal
from app import models
from app.routers import auth, gestures, stats, users, ml
from app.auth_utils import get_password_hash
from app.services.websocket_handler import ws_handler

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sajhilo Sewa API")

# Register Routers
app.include_router(auth.router)
app.include_router(gestures.router)
app.include_router(stats.router)
app.include_router(users.router)
app.include_router(ml.router, prefix="/api/ml", tags=["ML"])

@app.websocket("/ws/recognition/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_handler.handle(websocket, client_id)
origins = [
    "http://localhost:3000",
    "http://localhost:3001"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        # Check if user 'admin' exists
        admin_user = db.query(models.User).filter(models.User.username == "admin").first()
        if not admin_user:
            print("Creating default admin user...")
            admin_user = models.User(
                username="admin",
                email="admin@sajhilosewa.com",
                first_name="Admin",
                last_name="User",
                is_active=True
            )
            db.add(admin_user)
        # Always ensure the password is 'admin' for developer convenience
        admin_user.hashed_password = get_password_hash("admin")
        db.commit()
        print("Admin user 'admin' is ready with password 'admin'.")
    except Exception as e:
        print(f"Error initializing admin: {e}")
    finally:
        db.close()