from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging
from src.scubagear_pricefinder.config import settings
from src.scubagear_pricefinder.db.models import Base

logger = logging.getLogger(__name__)

if "sqlite" in settings.db_url:
    engine = create_engine(
        settings.db_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    engine = create_engine(
        settings.db_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db():
    logger.info(f"Initializing database: {settings.db_url}")
    Base.metadata.create_all(bind=engine)
    logger.info("✓ Database initialized")

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
