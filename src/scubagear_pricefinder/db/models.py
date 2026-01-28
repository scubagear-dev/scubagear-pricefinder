from sqlalchemy import (
    Column, String, Float, Boolean, DateTime, Integer, 
    ForeignKey, Text, func, Index
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Retailer(Base):
    __tablename__ = "retailers"
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    base_url = Column(String(500))
    scraper_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(100), primary_key=True)
    sku = Column(String(100), nullable=False)
    name = Column(String(500), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    price_eur = Column(Float)
    retailer_id = Column(String(50), ForeignKey("retailers.id"), nullable=False)
    retailer_url = Column(String(500))
    retailer_sku = Column(String(100))
    image_url = Column(String(500))
    in_stock = Column(Boolean, default=True)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index('idx_retailer_id', 'retailer_id'),
        Index('idx_name', 'name'),
        Index('idx_category', 'category'),
    )

class PriceHistory(Base):
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(String(100), ForeignKey("products.id"), nullable=False)
    price_eur = Column(Float)
    checked_at = Column(DateTime, default=func.now())

class ScrapeJob(Base):
    __tablename__ = "scrape_jobs"
    
    id = Column(String(36), primary_key=True)
    retailer_id = Column(String(50), ForeignKey("retailers.id"), nullable=False)
    status = Column(String(20))
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime)
    error_message = Column(Text)
    products_found = Column(Integer, default=0)
    products_updated = Column(Integer, default=0)
