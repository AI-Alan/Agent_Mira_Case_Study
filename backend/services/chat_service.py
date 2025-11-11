import random
from nlp.extractor import extract_filters
from services.data_service import filter_properties
from services.gemini_service import generate_chat_response, enhance_response_with_properties, is_gemini_available
from typing import Dict, Optional, List

# Random response messages for different scenarios
GREETING_RESPONSES = [
    "Hello! I'm here to help you find your perfect home! 🏡",
    "Hi there! Let's find you the ideal property today!",
    "Welcome! I'm excited to help you with your property search!",
    "Hey! Ready to discover amazing properties? Let's get started!",
]

SEARCH_SUCCESS_RESPONSES = [
    "Great news! I found some amazing properties for you!",
    "Perfect! Here are some properties that match your preferences.",
    "Excellent! I've curated the best options for you.",
    "Wonderful! I found some great matches for your search.",
    "Fantastic! Here are properties that fit your criteria perfectly.",
]

SEARCH_NO_RESULTS_RESPONSES = [
    "I couldn't find properties matching those exact criteria. Would you like to try different filters?",
    "No properties found with those specifications. Let me know if you'd like to adjust your search!",
    "Hmm, no matches found. How about trying a different location or budget range?",
    "Unfortunately, I couldn't find properties with those filters. Want to explore other options?",
]

HELPFUL_RESPONSES = [
    "I can help you search by location, budget, or number of bedrooms. Just let me know what you're looking for!",
    "Feel free to ask me about properties in Mumbai, Delhi, Bangalore, or Pune. I'm here to help!",
    "You can specify your budget (0-50L, 50L-1Cr, 1Cr-2Cr), location, and bedroom preference.",
    "Tell me what you're looking for - I'll find the perfect property for you!",
]

def get_random_response(responses: List[str]) -> str:
    """Get a random response from a list"""
    return random.choice(responses)

def _is_property_search(message: str, filters: Optional[Dict]) -> bool:
    """Check if user is searching for properties"""
    message_lower = message.lower().strip()
    
    # Keywords that indicate property search
    search_keywords = [
        "find", "search", "looking", "want", "need", "show", "list", 
        "property", "properties", "home", "house", "apartment", "flat",
        "buy", "rent", "bedroom", "bedrooms", "bhk", "location", "budget",
        "price", "mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai"
    ]
    
    # Check if message contains search keywords
    has_search_keywords = any(keyword in message_lower for keyword in search_keywords)
    
    # Check if filters are provided
    has_filters = filters and any(filters.values())
    
    return has_search_keywords or has_filters

def handle_chat(message: str, filters: Optional[Dict[str, Optional[str]]] = None) -> Dict:
    """
    Handle chat messages and return properties with response
    Enhanced with Gemini AI for natural conversations
    
    Args:
        message: User's chat message
        filters: Optional filters dict with location, budget, bedrooms
    
    Returns:
        Dict with response message and properties
    """
    message_lower = message.lower().strip()
    use_gemini = is_gemini_available()
    
    # Determine if this is a property search
    is_property_search = _is_property_search(message, filters)
    
    # Use provided filters or extract from message
    if not filters:
        try:
            extracted = extract_filters(message)
            filters = {
                "location": extracted.get("location"),
                "budget": extracted.get("budget"),
                "bedrooms": extracted.get("bedrooms")
            }
        except Exception as e:
            print(f"Error extracting filters: {e}")
            filters = {}
    
    # Only filter properties if user is searching for properties
    results = []
    if is_property_search:
        location = filters.get("location") if filters else None
        budget = filters.get("budget") if filters else None
        bedrooms = filters.get("bedrooms") if filters else None
        
        results = filter_properties(
            location=location,
            budget=budget,
            bedrooms=bedrooms
        )
    
    # Generate response message using Gemini if available, otherwise use fallback
    if use_gemini:
        try:
            # Try to generate a natural response with Gemini
            context = {
                "filters": filters if is_property_search else {},
                "has_properties": len(results) > 0,
                "property_count": len(results)
            }
            
            gemini_response = generate_chat_response(
                user_message=message,
                context=context,
                properties=results[:3] if results else None,
                is_property_search=is_property_search
            )
            
            if gemini_response:
                reply = gemini_response
            else:
                # Fallback to traditional responses
                reply = _generate_fallback_response(results, filters, message_lower, is_property_search)
        except Exception as e:
            print(f"Error using Gemini, falling back to traditional responses: {e}")
            reply = _generate_fallback_response(results, filters, message_lower, is_property_search)
    else:
        # Use traditional response system
        reply = _generate_fallback_response(results, filters, message_lower, is_property_search)
    
    # Format properties for frontend
    properties = []
    for prop in results[:6]:  # Limit to 6 properties
        # Format price based on location (USD for US, INR for India)
        price = prop.get("price", 0)
        prop_location = prop.get("location", "")
        
        # Check if it's an Indian city
        from services.data_service import is_indian_city
        is_india = is_indian_city(prop_location)
        
        if isinstance(price, (int, float)):
            if is_india:
                # Format in Indian currency (INR)
                if price >= 10000000:
                    price_str = f"₹{price/10000000:.1f}Cr"
                elif price >= 100000:
                    price_str = f"₹{price/100000:.1f}L"
                else:
                    price_str = f"₹{price:,}"
            else:
                # Format in US currency (USD)
                price_str = f"${price:,.0f}"
        else:
            price_str = str(price)
        
        # Get bedrooms
        bedrooms_count = prop.get("bedrooms") or prop.get("bedrooms_count") or prop.get("bhk") or 0
        if isinstance(bedrooms_count, str):
            import re
            match = re.search(r'(\d+)', bedrooms_count)
            if match:
                bedrooms_count = int(match.group(1))
        
        properties.append({
            "id": str(prop.get("id", "")),
            "title": prop.get("title", "Property"),
            "price": price_str,
            "location": prop.get("location", "Unknown"),
            "bedrooms": int(bedrooms_count) if bedrooms_count else 0,
            "image": prop.get("image_url") or prop.get("image")
        })
    
    return {
        "response": reply,
        "properties": properties,
        "filters": filters or {}
    }

def _generate_fallback_response(results: List[Dict], filters: Dict, message_lower: str = "", is_property_search: bool = False) -> str:
    """Generate fallback response when Gemini is not available"""
    # Handle greetings (only if not searching)
    if not is_property_search:
        if any(word in message_lower for word in ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]):
            return get_random_response(GREETING_RESPONSES)
        
        # Handle help requests
        if any(word in message_lower for word in ["help", "what can you do", "how", "guide", "assist"]):
            return get_random_response(HELPFUL_RESPONSES)
        
        # General conversation fallback
        return "I'm here to help you find your dream property! You can search by location, budget, or number of bedrooms. What are you looking for?"
    
    # Property search responses
    if len(results) > 0:
        reply = get_random_response(SEARCH_SUCCESS_RESPONSES)
        
        # Add specific details
        details = []
        location = filters.get("location") if filters else None
        budget = filters.get("budget") if filters else None
        bedrooms = filters.get("bedrooms") if filters else None
        
        if location:
            details.append(f"in {location}")
        if bedrooms:
            try:
                bedrooms_int = int(bedrooms)
                details.append(f"with {bedrooms_int} bedroom{'s' if bedrooms_int > 1 else ''}")
            except:
                details.append(f"with {bedrooms} bedroom(s)")
        if budget:
            details.append(f"within your budget of {budget}")
        
        if details:
            reply += " " + " ".join(details) + "."
        return reply
    else:
        return get_random_response(SEARCH_NO_RESULTS_RESPONSES)
