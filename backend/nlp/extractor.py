import re
from typing import Dict, Optional

# Indian cities
INDIAN_CITIES = ["mumbai", "delhi", "bangalore", "pune", "gurgaon", "noida", "hyderabad", "chennai", "bandra", "andheri", "koramangala", "whitefield", "hinjewadi", "kothrud", "connaught place"]

# US cities (for reference, but filtering works for any location)
US_CITIES = ["new york", "miami", "los angeles", "austin", "san francisco", "chicago", "dallas", "seattle", "boston"]

# Budget keywords
BUDGET_KEYWORDS = {
    "0-50l": ["0-50l", "0 to 50l", "upto 50l", "under 50l", "below 50l", "less than 50l"],
    "50l-1cr": ["50l-1cr", "50l to 1cr", "50l-1 cr", "50 lakhs to 1 crore"],
    "1cr-2cr": ["1cr-2cr", "1cr to 2cr", "1-2cr", "1 to 2 cr", "1 crore to 2 crore"]
}

def extract_location(text: str) -> Optional[str]:
    """Extract location/city from text"""
    text_lower = text.lower()
    
    for city in INDIAN_CITIES:
        if city in text_lower:
            # Return capitalized city name
            return city.capitalize()
    
    return None

def extract_budget(text: str) -> Optional[str]:
    """Extract budget range from text"""
    text_lower = text.lower().replace(" ", "")
    
    # Check for budget ranges
    for budget_key, keywords in BUDGET_KEYWORDS.items():
        for keyword in keywords:
            if keyword.replace(" ", "") in text_lower:
                return budget_key
    
    # Check for numeric patterns
    # Look for patterns like "50 lakhs", "1 crore", etc.
    lakhs_pattern = r'(\d+)\s*lakhs?'
    crore_pattern = r'(\d+)\s*crores?'
    
    lakhs_match = re.search(lakhs_pattern, text_lower)
    crores_match = re.search(crore_pattern, text_lower)
    
    if crores_match:
        crore_value = int(crores_match.group(1))
        if crore_value >= 2:
            return "1cr-2cr"
        elif crore_value >= 1:
            return "50l-1cr"
    
    if lakhs_match:
        lakhs_value = int(lakhs_match.group(1))
        if lakhs_value >= 50:
            return "50l-1cr"
        else:
            return "0-50l"
    
    return None

def extract_bedrooms(text: str) -> Optional[str]:
    """Extract number of bedrooms from text"""
    text_lower = text.lower()
    
    # Pattern for "2 BHK", "3 bedroom", etc.
    patterns = [
        r'(\d+)\s*bhk',
        r'(\d+)\s*bedroom',
        r'(\d+)\s*bed',
        r'(\d+)\s*room'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            bedrooms = match.group(1)
            # Validate it's a reasonable number (1-5)
            if 1 <= int(bedrooms) <= 5:
                return bedrooms
    
    # Check for written numbers
    number_words = {
        "one": "1", "two": "2", "three": "3", 
        "four": "4", "five": "5"
    }
    
    for word, num in number_words.items():
        if word in text_lower:
            return num
    
    return None

def extract_filters(text: str) -> Dict[str, Optional[str]]:
    """
    Extract location, budget, and bedrooms from text message
    
    Args:
        text: User's message text
    
    Returns:
        Dict with location, budget, and bedrooms (if found)
    """
    if not text:
        return {}
    
    return {
        "location": extract_location(text),
        "budget": extract_budget(text),
        "bedrooms": extract_bedrooms(text)
    }

