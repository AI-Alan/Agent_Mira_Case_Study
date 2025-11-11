import re
import json
from typing import Dict, Optional, List, Tuple
from pathlib import Path
from difflib import SequenceMatcher
from nlp import config

# Cache for loaded cities
_CITIES_CACHE = None
_DATA_DIR = Path(__file__).parent.parent / "data"


def _load_cities_from_data() -> List[str]:
    """Dynamically load all unique cities from property data"""
    global _CITIES_CACHE
    
    if _CITIES_CACHE is not None:
        return _CITIES_CACHE
    
    cities = set()
    try:
        property_file = _DATA_DIR / "property_basics.json"
        if property_file.exists():
            with open(property_file, 'r') as f:
                properties = json.load(f)
                for prop in properties:
                    location = prop.get('location', '')
                    # Extract city name (before comma)
                    if location:
                        city = location.split(',')[0].strip()
                        cities.add(city.lower())
    except Exception as e:
        print(f"Warning: Could not load cities from data: {e}")
        # Fallback to common cities from config
        cities = set(config.FALLBACK_CITIES)
    
    _CITIES_CACHE = list(cities)
    return _CITIES_CACHE


def _fuzzy_match(text: str, candidates: List[str], threshold: float = 0.6) -> Optional[Tuple[str, float]]:
    """Fuzzy match text against candidates, return best match if above threshold"""
    text_lower = text.lower()
    best_match = None
    best_score = 0.0
    
    for candidate in candidates:
        # Check exact substring match first
        if candidate in text_lower:
            return (candidate, 1.0)
        
        # Check fuzzy similarity
        score = SequenceMatcher(None, candidate, text_lower).ratio()
        if score > best_score:
            best_score = score
            best_match = candidate
    
    if best_score >= threshold:
        return (best_match, best_score)
    
    return None

def extract_location(text: str) -> Optional[str]:
    """Extract location/city from text using fuzzy matching"""
    if not text:
        return None
    
    cities = _load_cities_from_data()
    text_lower = text.lower()
    
    # Try exact match first (fast path)
    for city in cities:
        if city in text_lower:
            return city.title()
    
    # Try fuzzy matching on individual words
    words = text_lower.split()
    for word in words:
        if len(word) >= config.MIN_WORD_LENGTH_FOR_FUZZY:  # Skip very short words
            match = _fuzzy_match(word, cities, threshold=config.FUZZY_MATCH_THRESHOLD)
            if match:
                city, score = match
                return city.title()
    
    # Try multi-word matching (e.g., "New York", "San Francisco")
    for i in range(len(words) - 1):
        two_words = f"{words[i]} {words[i+1]}"
        match = _fuzzy_match(two_words, cities, threshold=config.FUZZY_MATCH_THRESHOLD)
        if match:
            city, score = match
            return city.title()
    
    return None

def extract_budget(text: str) -> Optional[str]:
    """Extract budget range from text - supports multiple currencies and formats"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Pattern 1: Explicit range keywords ("0-50l", "under 50k", "$200k-$500k")
    range_patterns = [
        r'(?:under|below|less than|upto|up to)\s*(?:[$₹])?\s*(\d+)\s*([kKlLmM]|lakhs?|crores?|thousand|million)?',
        r'(?:[$₹])?\s*(\d+)\s*([kKlLmM]|lakhs?|crores?)?\s*(?:to|-|–)\s*(?:[$₹])?\s*(\d+)\s*([kKlLmM]|lakhs?|crores?|thousand|million)?',
        r'(?:[$₹])?\s*(\d+)\s*([kKlLmM]|lakhs?|crores?|thousand|million)?\s*(?:budget|price|cost)',
    ]
    
    for pattern in range_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return _normalize_budget(match.group(0))
    
    # Pattern 2: Numeric values with currency symbols
    numeric_patterns = [
        r'[$₹]\s*(\d+[,.]?\d*)\s*([kKmMbB]|lakhs?|crores?|thousand|million)?',
        r'(\d+[,.]?\d*)\s*([kKlLmMbB]|lakhs?|crores?|thousand|million)',
    ]
    
    for pattern in numeric_patterns:
        match = re.search(pattern, text_lower)
        if match:
            return _normalize_budget(match.group(0))
    
    return None


def _normalize_budget(budget_str: str) -> str:
    """Normalize budget string to standard ranges"""
    budget_lower = budget_str.lower().replace(',', '').replace('$', '').replace('₹', '').strip()
    
    # Extract numeric value
    num_match = re.search(r'(\d+(?:\.\d+)?)', budget_lower)
    if not num_match:
        return None
    
    value = float(num_match.group(1))
    
    # Determine multiplier using config
    for key, multiplier in config.CURRENCY_MULTIPLIERS.items():
        if key in budget_lower:
            value *= multiplier
            break
    
    # Map to standard ranges from config
    for min_val, max_val, range_label in config.BUDGET_RANGES:
        if min_val <= value < max_val:
            return range_label
    
    # Default to highest range if not found
    return config.BUDGET_RANGES[-1][2]

def extract_bedrooms(text: str) -> Optional[str]:
    """Extract number of bedrooms from text with improved pattern matching"""
    if not text:
        return None
    
    text_lower = text.lower()
    
    # Use patterns from config
    for pattern in config.BEDROOM_PATTERNS:
        match = re.search(pattern, text_lower)
        if match:
            bedrooms = match.group(1)
            # Validate it's a reasonable number using config
            if 1 <= int(bedrooms) <= config.MAX_BEDROOMS:
                return bedrooms
    
    # Check for "studio" or "1br"
    if 'studio' in text_lower:
        return "1"
    
    # Look for written numbers from config
    for word, num in config.NUMBER_WORDS.items():
        if re.search(rf'\b{word}\b.*(?:bedroom|bed|bhk|br)', text_lower):
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

