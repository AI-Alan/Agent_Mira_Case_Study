from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from services.auth_service import get_current_active_user
from models.user_model import UserInDB
from core.db import db

router = APIRouter()

class SavePropertyRequest(BaseModel):
    property_id: str
    property_data: Optional[dict] = None  # Optional: store full property data

@router.post("/save")
async def save_property_for_user(
    data: SavePropertyRequest,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Save a property for the current user - allows saving multiple properties"""
    try:
        # Check if property is already saved
        existing = await db.saved_properties.find_one({
            "user_id": current_user.id,
            "property_id": data.property_id
        })
        
        if existing:
            # Return success message even if already saved (idempotent)
            return {
                "message": "Property is already saved",
                "id": str(existing.get("_id", "")),
                "already_saved": True
            }
        
        # Get full property data if not provided
        property_data = data.property_data
        if not property_data:
            from services.data_service import merge_json_data
            all_properties = merge_json_data()
            for prop in all_properties:
                if str(prop.get("id", "")) == str(data.property_id):
                    property_data = prop
                    break
        
        # Save property with full data
        saved_property = {
            "user_id": current_user.id,
            "property_id": str(data.property_id),
            "property_data": property_data,  # Store full property snapshot
            "saved_at": datetime.utcnow()
        }
        
        result = await db.saved_properties.insert_one(saved_property)
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save property in database"
            )
        
        return {
            "message": "Property saved successfully",
            "id": str(result.inserted_id),
            "already_saved": False
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"Error saving property: {error_msg}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save property: {error_msg[:200]}"
        )

@router.get("/saved")
async def get_saved_properties(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get saved properties for the current user"""
    try:
        saved_items = await db.saved_properties.find({
            "user_id": current_user.id
        }).to_list(None)
        
        print(f"Found {len(saved_items)} saved items from database")
        
        if not saved_items:
            return {
                "user_id": current_user.id,
                "saved_properties": []
            }
        
        from services.data_service import is_indian_city
        formatted_properties = []
        
        # First, try to use stored property_data
        for item in saved_items:
            property_data = item.get("property_data")
            property_id = str(item.get("property_id", ""))
            
            # If we have stored property data, use it
            if property_data:
                prop = property_data
                print(f"Using stored property data for ID: {property_id}")
            else:
                # Fallback: try to find property in merged data
                print(f"No stored data for {property_id}, searching in merged data...")
                from services.data_service import merge_json_data
                all_properties = merge_json_data()
                prop = None
                for p in all_properties:
                    if str(p.get("id", "")) == property_id:
                        prop = p
                        break
                
                if not prop:
                    print(f"Warning: Property {property_id} not found in data")
                    continue
            
            # Format price
            price = prop.get("price", 0)
            if isinstance(price, str):
                try:
                    price = float(price.replace(',', '').replace('₹', '').replace('Rs', '').replace('$', '').strip())
                except (ValueError, AttributeError):
                    price = 0
            
            if not isinstance(price, (int, float)):
                price = 0
            
            # Format price string
            prop_location = prop.get("location", "")
            if is_indian_city(prop_location):
                if price >= 10000000:
                    price_str = f"₹{price/10000000:.1f}Cr"
                elif price >= 100000:
                    price_str = f"₹{price/100000:.1f}L"
                else:
                    price_str = f"₹{price:,.0f}" if price > 0 else "Price on request"
            else:
                price_str = f"${price:,.0f}" if price > 0 else "Price on request"
            
            # Get bedrooms
            bedrooms_count = prop.get("bedrooms") or prop.get("bedrooms_count") or prop.get("bhk") or 0
            if isinstance(bedrooms_count, str):
                import re
                match = re.search(r'(\d+)', bedrooms_count)
                if match:
                    bedrooms_count = int(match.group(1))
            
            formatted_properties.append({
                "id": str(prop.get("id", property_id)),
                "title": prop.get("title", "Property"),
                "price": price_str,
                "location": prop.get("location", "Unknown"),
                "bedrooms": int(bedrooms_count) if bedrooms_count else 0,
                "image": prop.get("image_url") or prop.get("image")
            })
        
        print(f"Returning {len(formatted_properties)} formatted properties")
        return {
            "user_id": current_user.id,
            "saved_properties": formatted_properties
        }
    except Exception as e:
        import traceback
        print(f"Error getting saved properties: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve saved properties: {str(e)[:200]}"
        )

@router.delete("/saved/{property_id}")
async def unsave_property(
    property_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Remove a saved property for the current user"""
    try:
        result = await db.saved_properties.delete_one({
            "user_id": current_user.id,
            "property_id": property_id
        })
        
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Saved property not found"
            )
        
        return {
            "message": "Property removed from saved list"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

