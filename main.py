import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson.objectid import ObjectId

from database import db, create_document, get_documents
from schemas import User, Product, Category, Order, Wishlist

app = FastAPI(title="Saaz International – Online Shopping API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utility to convert ObjectId to string

def serialize_doc(doc):
    if not doc:
        return doc
    doc = dict(doc)
    if "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc


@app.get("/")
def read_root():
    return {"brand": "Saaz International", "status": "ok"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": [],
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, "name") else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response


# Auth light (email/password only for demo)
class AuthPayload(BaseModel):
    email: str
    password: str


@app.post("/auth/signup")
def signup(payload: User):
    # Uniqueness by email
    existing = db["user"].find_one({"email": payload.email}) if db else None
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user_data = payload.model_dump()
    user_data.pop("user_id", None)
    inserted_id = create_document("user", user_data)
    doc = db["user"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)


@app.post("/auth/login")
def login(payload: AuthPayload):
    user = db["user"].find_one({"email": payload.email}) if db else None
    if not user or not payload.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return serialize_doc(user)


# Products
@app.get("/products")
def list_products(category: Optional[str] = None, q: Optional[str] = None, limit: int = 50):
    filt = {}
    if category:
        filt["category"] = category
    if q:
        filt["name"] = {"$regex": q, "$options": "i"}
    items = db["product"].find(filt).limit(limit) if db else []
    return [serialize_doc(i) for i in items]


@app.post("/products")
def create_product(payload: Product):
    data = payload.model_dump()
    data.pop("product_id", None)
    inserted_id = create_document("product", data)
    doc = db["product"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)


@app.get("/products/{product_id}")
def get_product(product_id: str):
    doc = db["product"].find_one({"_id": ObjectId(product_id)}) if db else None
    if not doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return serialize_doc(doc)


# Categories
@app.get("/categories")
def list_categories():
    items = db["category"].find({}) if db else []
    return [serialize_doc(i) for i in items]


@app.post("/categories")
def create_category(payload: Category):
    data = payload.model_dump()
    data.pop("category_id", None)
    inserted_id = create_document("category", data)
    doc = db["category"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)


# Cart is client-side for demo; Orders
@app.post("/orders")
def create_order(payload: Order):
    data = payload.model_dump()
    data.pop("order_id", None)
    inserted_id = create_document("order", data)
    doc = db["order"].find_one({"_id": ObjectId(inserted_id)})
    return serialize_doc(doc)


@app.get("/orders")
def list_orders(user_id: Optional[str] = None, status: Optional[str] = None):
    filt = {}
    if user_id:
        filt["user_id"] = user_id
    if status:
        filt["order_status"] = status
    items = db["order"].find(filt) if db else []
    return [serialize_doc(i) for i in items]


@app.get("/orders/{order_id}")
def get_order(order_id: str):
    doc = db["order"].find_one({"_id": ObjectId(order_id)}) if db else None
    if not doc:
        raise HTTPException(status_code=404, detail="Order not found")
    return serialize_doc(doc)


# Wishlist
@app.get("/wishlist/{user_id}")
def get_wishlist(user_id: str):
    items = db["wishlist"].find({"user_id": user_id}) if db else []
    return [serialize_doc(i) for i in items]


@app.post("/wishlist")
def add_wishlist(item: Wishlist):
    data = item.model_dump()
    create_document("wishlist", data)
    return {"ok": True}


# Support placeholder endpoints
@app.get("/support/options")
def support_options():
    return {
        "live_chat": True,
        "whatsapp": True,
        "email": "support@saazintl.com",
        "whatsapp_number": "+1-202-555-0123",
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
