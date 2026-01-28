from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.scubagear_pricefinder.db.connection import get_db
from src.scubagear_pricefinder.db.models import Product
from src.scubagear_pricefinder.api.models import ProductResponse

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db), limit: int = 50, skip: int = 0):
    return db.query(Product).limit(limit).offset(skip).all()

@router.get("/search", response_model=list[ProductResponse])
def search(q: str, db: Session = Depends(get_db), max_price: float = None):
    if not q:
        raise HTTPException(status_code=400, detail="q required")
    
    filters = [
        or_(
            Product.name.ilike(f"%{q}%"),
            Product.sku.ilike(f"%{q}%")
        )
    ]
    
    if max_price:
        filters.append(Product.price_eur <= max_price)
    
    return db.query(Product).filter(and_(*filters)).limit(50).all()

@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter_by(id=product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Not found")
    return product
