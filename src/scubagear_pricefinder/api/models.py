from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ProductResponse(BaseModel):
    id: str
    sku: str
    name: str
    category: Optional[str] = None
    price_eur: Optional[float] = None
    retailer_id: str
    retailer_url: Optional[str] = None
    image_url: Optional[str] = None
    in_stock: bool
    last_updated: datetime
    
    class Config:
        from_attributes = True
