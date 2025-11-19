"""
Database Schemas for Saaz International – Online Shopping

Each Pydantic model maps to a MongoDB collection. The collection name is the
lowercase class name (e.g., User -> "user").
"""
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr

# Users
class User(BaseModel):
    user_id: Optional[str] = Field(None, description="Custom user id (public)")
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., description="Hashed password")
    address: Optional[str] = None

# Products
class Product(BaseModel):
    product_id: Optional[str] = None
    name: str
    category: str
    price: float = Field(..., ge=0)
    images: List[str] = Field(default_factory=list)
    stock: int = Field(..., ge=0)
    description: Optional[str] = None
    ratings: Optional[float] = Field(0, ge=0, le=5)
    discount: Optional[float] = Field(0, ge=0, le=100, description="Percent discount")

# Categories
class Category(BaseModel):
    category_id: Optional[str] = None
    name: str
    icon: Optional[str] = None

# Orders
class OrderItem(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1)
    price: float = Field(..., ge=0)

class Order(BaseModel):
    order_id: Optional[str] = None
    user_id: str
    items: List[OrderItem]
    payment_method: str
    total_amount: float = Field(..., ge=0)
    order_status: str = Field("pending", description="pending|processing|shipped|delivered|cancelled")
    shipping_address: str
    tracking_code: Optional[str] = None

# Wishlist
class Wishlist(BaseModel):
    user_id: str
    product_id: str
