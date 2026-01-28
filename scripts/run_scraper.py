#!/usr/bin/env python
import logging
import sys
import uuid
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scubagear_pricefinder.config import settings
from src.scubagear_pricefinder.scraper.retailers.subacquea_it import SubacqueitScraper
from src.scubagear_pricefinder.db.connection import SessionLocal, init_db
from src.scubagear_pricefinder.db.models import Retailer, Product, ScrapeJob
import click

logger = logging.getLogger(__name__)

SCRAPERS = {
    "subacquea-it": SubacqueitScraper,
}

def scrape_retailer(retailer_id: str, db) -> int:
    
    if retailer_id not in SCRAPERS:
        logger.error(f"Unknown retailer: {retailer_id}")
        return 0
    
    # ✅ CREATE RETAILER FIRST (before ScrapeJob)
    retailer = db.query(Retailer).filter_by(id=retailer_id).first()
    if not retailer:
        scraper_class = SCRAPERS[retailer_id]
        scraper = scraper_class()
        retailer = Retailer(
            id=retailer_id,
            name=scraper.retailer_id.replace('-', ' ').title(),
            base_url=scraper.base_url,
            scraper_enabled=True
        )
        db.add(retailer)
        db.commit()
        logger.info(f"✓ Created retailer: {retailer_id}")
    
    # ✅ NOW create ScrapeJob (FK constraint satisfied)
    job_id = str(uuid.uuid4())
    job = ScrapeJob(
        id=job_id,
        retailer_id=retailer_id,
        status="running",
        started_at=datetime.now()
    )
    db.add(job)
    db.commit()
    
    logger.info(f"🚀 Job {job_id}: scraping {retailer_id}")
    
    try:
        scraper_class = SCRAPERS[retailer_id]
        scraper = scraper_class()
        products = scraper.scrape()
        
        updated = 0
        for product_data in products:
            product_id = f"{retailer_id}_{product_data['retailer_sku']}"
            
            product = db.query(Product).filter_by(id=product_id).first()
            if product:
                product.name = product_data['name']
                product.category = product_data.get('category')
                product.price_eur = product_data.get('price_eur')
                product.retailer_url = product_data['retailer_url']
                product.in_stock = product_data.get('in_stock', True)
                product.last_updated = datetime.now()
                updated += 1
            else:
                product = Product(
                    id=product_id,
                    sku=product_data['sku'],
                    name=product_data['name'],
                    category=product_data.get('category'),
                    price_eur=product_data.get('price_eur'),
                    retailer_id=retailer_id,
                    retailer_url=product_data['retailer_url'],
                    retailer_sku=product_data['retailer_sku'],
                    in_stock=product_data.get('in_stock', True),
                    last_updated=datetime.now()
                )
                db.add(product)
        
        db.commit()
        
        job.status = "success"
        job.products_found = len(products)
        job.products_updated = updated
        job.completed_at = datetime.now()
        db.commit()
        
        logger.info(f"✅ Job {job_id}: success (found={len(products)}, updated={updated})")
        return len(products)
        
    except Exception as e:
        logger.error(f"❌ Job {job_id}: failed", exc_info=True)
        job.status = "failed"
        job.error_message = str(e)
        job.completed_at = datetime.now()
        db.commit()
        raise

@click.command()
@click.option("--retailer", default="subacquea-it", help="Retailer ID")
def main(retailer: str):
    init_db()
    db = SessionLocal()
    try:
        scrape_retailer(retailer, db)
    finally:
        db.close()

if __name__ == "__main__":
    main()
