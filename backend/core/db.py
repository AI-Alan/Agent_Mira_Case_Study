from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

# Initialize MongoDB client
# MongoDB automatically creates databases when you first write to them
client = AsyncIOMotorClient(settings.MONGO_URI, serverSelectionTimeoutMS=10000)
db = client[settings.DATABASE_NAME]

# Test connection function
async def test_connection():
    """Test MongoDB connection and return status"""
    try:
        await client.admin.command('ping')
        # Verify database access
        await db.list_collection_names()
        return {"status": "success", "message": "MongoDB connection successful!", "database": settings.DATABASE_NAME}
    except Exception as e:
        error_msg = str(e)
        return {
            "status": "error", 
            "message": f"MongoDB connection failed: {error_msg}",
            "database": settings.DATABASE_NAME,
            "hint": "Please check your MONGO_URI in the .env file. MongoDB creates databases automatically when you first write to them."
        }
