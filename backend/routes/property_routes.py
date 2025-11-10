from fastapi import APIRouter
from services.data_service import filter_properties, merge_json_data
from typing import Optional

router = APIRouter()

@router.get("")
def get_properties(
    location: Optional[str] = None,
    budget: Optional[str] = None,
    bedrooms: Optional[str] = None
):
    """Get properties with optional filters"""
    results = filter_properties(location=location, budget=budget, bedrooms=bedrooms)
    return {"properties": results}

@router.get("/all")
def get_all_properties():
    """Get all properties"""
    properties = merge_json_data()
    return {"properties": properties}

