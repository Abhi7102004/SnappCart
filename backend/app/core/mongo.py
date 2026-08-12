from motor.motor_asyncio import AsyncIOMotorClient
from loguru import logger

from app.core.config import settings

client = AsyncIOMotorClient(settings.mongodb_url)
db = client["snappcart"]

products_collection = db["products"]

PRODUCT_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": [
            "name", "seller_id", "category_id",
            "price", "images", "variants",
        ],
        "properties": {
            "name":       {"bsonType": "string", "minLength": 1},
            "price":      {"bsonType": "int",    "minimum": 0},
            "images":     {"bsonType": "array",  "minItems": 1},
            "variants":   {"bsonType": "array",  "minItems": 1},
            "is_deleted": {"bsonType": "bool"},
        },
    }
}

async def check_mongo_connection() -> bool:
    """
    Health check — verify Atlas is reachable.
    Mirrors check_db_connection / check_redis_connection.
    """
    
    try:
        await client.admin.command("ping")
        logger.info("MongoDB connection successful.")
        return True
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return False
    
    
async def setup_product_collection() -> None:
    """
    Create the products collection with validation rules if it doesn't exist.
    """
    
    existing = await db.list_collection_names()
    
    if "products" not in existing:
        await db.create_collection("products", validator=PRODUCT_VALIDATOR)
        logger.info("Created 'products' collection with validation rules.")
    else:
        await db.command({
            "collMod": "products",
            "validator": PRODUCT_VALIDATOR,
            "validationLevel": "moderate",  # don't reject pre-existing docs
        })
        
        logger.info("Updated 'products' collection validator")
        
    # Indexes — create_index is idempotent, safe every startup.
    await products_collection.create_index("seller_id")
    await products_collection.create_index("category_id")
    await products_collection.create_index(
        [("seller_id", 1), ("slug", 1)], unique=True
    )
    logger.info("Product indexes ensured")
