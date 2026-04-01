from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_yY6zAXcoNt3e@ep-shy-scene-a8h4xt4s-pooler.eastus2.azure.neon.tech/neondb?sslmode=require&channel_binding=require",
)

engine = create_engine(
    DATABASE_URL, 
    pool_pre_ping=True,                         # Verify connection is alive before using
    pool_recycle=300,                           # Refresh connections every 5 mins
    connect_args={
        "keepalives": 1,                         # Enable TCP keepalives
        "keepalives_idle": 60,                   # Seconds of inactivity before sending keepalive
        "keepalives_interval": 10,               # Seconds between keepalive probes
        "keepalives_count": 5,                   # Max probes to lose before disconnect
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
