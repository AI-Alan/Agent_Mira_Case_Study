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
            gemini_client = genai.GenerativeModel('gemini-pro')
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
        # Build system prompt
        if is_property_search and properties:
            system_prompt = """You are Mira, a friendly and helpful AI real estate assistant. 
Your role is to help users find their dream properties. Be conversational, warm, and professional.
Keep responses concise (2-3 sentences max) and natural. Use emojis sparingly.

I found properties matching the user's search. Acknowledge this naturally and mention that you're showing them the best options.
Be enthusiastic but professional."""
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
        
        properties_info = ""
        if properties and len(properties) > 0:
            count = len(properties)
            properties_info = f"\n\nI found {count} property/properties matching the user's criteria. "
            properties_info += "Acknowledge this naturally and mention that you're showing them the best options below."
        elif is_property_search and (not properties or len(properties) == 0):
            properties_info = "\n\nNo properties were found matching the user's criteria. "
            properties_info += "Apologize naturally and suggest they try different filters or criteria."
        
        # Build the full prompt
        full_prompt = f"""{system_prompt}
{context_info}{properties_info}

User message: {user_message}

Generate a natural, conversational response (2-3 sentences max):"""

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

