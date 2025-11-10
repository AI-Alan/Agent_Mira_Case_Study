from core.db import db

async def save_property(user_id: str, property_id: str):
    await db.saved.insert_one({"user_id": user_id, "property_id": property_id})
    return {"message": "Property saved successfully."}

async def get_saved(user_id: str):
    saved = await db.saved.find({"user_id": user_id}).to_list(None)
    return saved
