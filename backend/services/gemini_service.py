"""
Gemini AI service for enhanced chat conversations
"""
import google.generativeai as genai
from typing import Optional, List, Dict
from core.config import settings

# Initialize Gemini client
gemini_client = None

def initialize_gemini():
    """Initialize Gemini client if API key is available"""
    global gemini_client
    if settings.GEMINI_API_KEY:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            gemini_client = genai.GenerativeModel('gemini-2.5-flash')
            return True
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            return False
    return False

def is_gemini_available() -> bool:
    """Check if Gemini is available"""
    global gemini_client
    if not settings.GEMINI_API_KEY:
        return False
    if gemini_client is None:
        return initialize_gemini()
    return True

def generate_chat_response(
    user_message: str,
    context: Optional[Dict] = None,
    properties: Optional[List[Dict]] = None,
    is_property_search: bool = False
) -> str:
    """
    Generate a natural language response using Gemini
    STRICTLY constrained to only reference actual properties in the database
    
    Args:
        user_message: User's message
        context: Optional context (filters, previous conversation, etc.)
        properties: Optional list of properties to reference
        is_property_search: Whether user is searching for properties
    
    Returns:
        Natural language response
    """
    if not is_gemini_available():
        return None
    
    try:
        # Build system prompt with STRICT constraints
        if is_property_search:
            if properties and len(properties) > 0:
                system_prompt = """You are Mira, a friendly and helpful AI real estate assistant.

CRITICAL RULES:
1. You can ONLY talk about properties that are provided to you in the properties list below
2. DO NOT make up, invent, or hallucinate any properties that are not in the list
3. DO NOT mention properties that don't exist in the database
4. If a property is not in the provided list, it does NOT exist - do not reference it
5. Keep responses concise (2-3 sentences max)
6. Be conversational, warm, and professional
7. Use emojis sparingly (max 1-2 per response)

You found properties matching the user's search. Acknowledge this naturally and mention that you're showing them the best options."""
            else:
                # NO PROPERTIES FOUND - be clear about this
                system_prompt = """You are Mira, a friendly and helpful AI real estate assistant.

CRITICAL RULES:
1. NO properties were found matching the user's criteria
2. DO NOT make up or suggest properties that don't exist
3. DO NOT say "I found some properties" or similar - you found ZERO properties
4. Clearly state that no properties match their criteria
5. Suggest they try different filters (location, budget, bedrooms)
6. Be helpful and encouraging, but honest about the lack of results
7. Keep responses concise (2-3 sentences max)
8. Use emojis sparingly

The user searched for properties but NO matches were found in the database."""
        else:
            system_prompt = """You are Mira, a friendly and helpful AI real estate assistant. 
Your role is to help users find their dream properties. Be conversational, warm, and professional.
Keep responses concise (2-3 sentences max) and natural. Use emojis sparingly.

Engage in natural conversation. If the user is asking about properties, help them. If they're just chatting, be friendly and helpful.
Always be encouraging and ready to help with property searches."""

        # Build context information
        context_info = ""
        if context and is_property_search:
            filters = context.get("filters", {})
            if filters and any(filters.values()):
                context_info = "\nUser search preferences:\n"
                if filters.get("location"):
                    context_info += f"- Location: {filters['location']}\n"
                if filters.get("budget"):
                    context_info += f"- Budget: {filters['budget']}\n"
                if filters.get("bedrooms"):
                    context_info += f"- Bedrooms: {filters['bedrooms']}\n"
        
        # Build properties info - ONLY if properties exist
        properties_info = ""
        if is_property_search:
            if properties and len(properties) > 0:
                # List actual properties that exist
                properties_list = []
                for i, prop in enumerate(properties[:5], 1):  # Limit to 5 for context
                    title = prop.get('title', 'Property')
                    location = prop.get('location', 'Unknown')
                    price = prop.get('price', 'N/A')
                    bedrooms = prop.get('bedrooms', 'N/A')
                    properties_list.append(f"{i}. {title} in {location} - {price} ({bedrooms} bedrooms)")
                
                properties_info = f"\n\nACTUAL PROPERTIES FOUND IN DATABASE ({len(properties)} total):\n"
                properties_info += "\n".join(properties_list)
                properties_info += "\n\nIMPORTANT: You can ONLY reference these properties. Do not mention any other properties."
            else:
                properties_info = "\n\nNO PROPERTIES FOUND: The database search returned ZERO results. Do not suggest or mention any properties."
        
        # Build the full prompt
        full_prompt = f"""{system_prompt}
{context_info}{properties_info}

User message: {user_message}

Generate a natural, conversational response (2-3 sentences max) that strictly adheres to the rules above:"""

        # Generate response
        response = gemini_client.generate_content(full_prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return None
            
    except Exception as e:
        print(f"Error generating Gemini response: {e}")
        return None

def enhance_response_with_properties(
    base_response: str,
    properties: List[Dict],
    filters: Optional[Dict] = None
) -> str:
    """
    Enhance a response with property information using Gemini
    
    Args:
        base_response: Base response message
        properties: List of properties found
        filters: Optional filters used
    
    Returns:
        Enhanced response
    """
    if not is_gemini_available() or not properties:
        return base_response
    
    try:
        properties_summary = []
        for prop in properties[:3]:  # Use top 3 for context
            summary = f"{prop.get('title', 'Property')} in {prop.get('location', 'Unknown')} - {prop.get('price', 'N/A')}"
            properties_summary.append(summary)
        
        prompt = f"""You are Mira, a real estate assistant. 
A user asked about properties and I found {len(properties)} matching properties.

Properties found:
{chr(10).join(properties_summary)}

Create a natural, conversational response (2-3 sentences) that:
1. Acknowledges finding properties
2. Mentions key highlights naturally
3. Encourages the user to explore

Keep it warm and helpful. Don't list all properties, just mention naturally."""

        response = gemini_client.generate_content(prompt)
        
        if response and response.text:
            return response.text.strip()
        else:
            return base_response
            
    except Exception as e:
        print(f"Error enhancing response: {e}")
        return base_response

# Initialize on import
if settings.GEMINI_API_KEY:
    initialize_gemini()

