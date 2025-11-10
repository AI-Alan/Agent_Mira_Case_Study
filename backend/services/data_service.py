import json
from pathlib import Path
from typing import Optional, List, Dict

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

def load_json(filename: str) -> List[Dict]:
    """Load JSON data from file"""
    try:
        with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return []
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}")
        return []

def merge_json_data() -> List[Dict]:
    """
    Merge data from three JSON files:
    - property_basics.json (id, title, price, location)
    - property_characteristics.json (id, bedrooms, bathrooms, size_sqft, amenities)
    - property_images.json (id, image_url)
    """
    basics = load_json("property_basics.json")
    chars = load_json("property_characteristics.json")
    images = load_json("property_images.json")

    # Create lookup dictionaries for faster merging
    chars_dict = {c["id"]: c for c in chars}
    images_dict = {i["id"]: i for i in images}

    # Merge all data
    merged = []
    for p in basics:
        pid = p["id"]
        merged_property = {
            **p,  # Start with basics
            **chars_dict.get(pid, {}),  # Add characteristics
            **images_dict.get(pid, {})  # Add images
        }
        merged.append(merged_property)

    return merged

def parse_budget_range(budget: Optional[str]) -> tuple:
    """Parse budget range string to min and max values in Rupees"""
    if not budget:
        return (0, float('inf'))
    
    budget_lower = budget.lower().replace(' ', '').replace('-', '')
    
    if '50l1cr' in budget_lower or '50l-1cr' in budget_lower:
        return (5000000, 10000000)  # 50L to 1Cr (5M to 10M)
    elif '050l' in budget_lower or '0-50l' in budget_lower:
        return (0, 5000000)  # 0 to 50L (0 to 5M)
    elif '1cr2cr' in budget_lower or '1cr-2cr' in budget_lower:
        return (10000000, 20000000)  # 1Cr to 2Cr (10M to 20M)
    elif '2cr' in budget_lower:
        return (20000000, float('inf'))  # Above 2Cr
    else:
        return (0, float('inf'))

def is_indian_city(location: str) -> bool:
    """Check if location is an Indian city"""
    indian_cities = ["mumbai", "delhi", "bangalore", "pune", "gurgaon", "noida", "hyderabad", "chennai"]
    location_lower = location.lower()
    return any(city in location_lower for city in indian_cities)

def convert_usd_to_inr(usd_price: float) -> float:
    """Convert USD to INR (approximate conversion rate: 83)"""
    return usd_price * 83

def filter_properties(
    location: Optional[str] = None, 
    budget: Optional[str] = None, 
    bedrooms: Optional[str] = None
) -> List[Dict]:
    """
    Filter properties based on location, budget, and bedrooms
    Handles both US properties (USD) and Indian properties (INR)
    
    Args:
        location: City name (e.g., "Mumbai", "Delhi", "Bangalore", "Pune", "New York")
        budget: Budget range (e.g., "0-50L", "50L-1Cr", "1Cr-2Cr")
        bedrooms: Number of bedrooms (e.g., "1", "2", "3", "4")
    
    Returns:
        List of filtered properties with all merged data
    """
    properties = merge_json_data()
    min_budget, max_budget = parse_budget_range(budget)
    
    results = []
    for p in properties:
        prop_location = p.get("location", "")
        
        # Location filter (case-insensitive)
        if location:
            location_lower = location.lower()
            prop_location_lower = prop_location.lower()
            # Check if location matches (supports partial matches like "Mumbai" in "Mumbai, Maharashtra")
            if location_lower not in prop_location_lower:
                continue
        
        # Budget filter
        if budget:
            price = p.get("price", 0)
            # Ensure price is a number
            if isinstance(price, str):
                try:
                    price = float(price.replace(',', '').replace('₹', '').replace('Rs', '').replace('$', '').strip())
                except (ValueError, AttributeError):
                    price = 0
            
            if not isinstance(price, (int, float)):
                price = 0
            
            # Determine if property is in India or US
            # If location contains Indian city, price is in INR
            # Otherwise, assume USD and convert to INR for comparison
            if is_indian_city(prop_location):
                # Price is already in INR
                price_inr = price
            else:
                # Price is in USD, convert to INR for comparison
                price_inr = convert_usd_to_inr(price)
            
            # Check if price is in budget range
            if price_inr < min_budget or price_inr > max_budget:
                continue
        
        # Bedrooms filter
        if bedrooms:
            prop_bedrooms = p.get("bedrooms") or p.get("bedrooms_count") or 0
            # Handle string format like "3 BHK"
            if isinstance(prop_bedrooms, str):
                import re
                match = re.search(r'(\d+)', prop_bedrooms)
                if match:
                    prop_bedrooms = int(match.group(1))
            
            if str(prop_bedrooms) != str(bedrooms):
                continue
        
        results.append(p)
    
    return results
