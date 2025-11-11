"""
LLM-based entity extraction using Google Gemini
Fallback/enhancement for rule-based extraction
"""

import json
import re
from typing import Dict, Optional, List
from core.config import settings
import google.generativeai as genai

# Initialize Gemini
_gemini_model = None

def _initialize_gemini():
    """Initialize Gemini model if API key available"""
    global _gemini_model
    if settings.GEMINI_API_KEY and _gemini_model is None:
        try:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            _gemini_model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini LLM initialized for hybrid NLP extraction")
            return True
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize Gemini for NLP: {e}")
            return False
    return _gemini_model is not None


def is_llm_available() -> bool:
    """Check if LLM is available for extraction"""
    if _gemini_model is None:
        return _initialize_gemini()
    return True


def extract_entities_with_llm(text: str) -> Dict[str, Optional[str]]:
    """
    Extract real estate entities using Gemini LLM
    
    Args:
        text: User's natural language query
    
    Returns:
        Dict with location, budget, bedrooms, and additional preferences
    """
    if not is_llm_available():
        return {}
    
    print(f"🤖 Using Gemini LLM for entity extraction...")
    
    try:
        prompt = f"""You are an AI assistant specialized in extracting real estate search parameters from natural language queries.

Extract the following information from the user's message:
1. **location**: City or area name (e.g., "Mumbai", "New York", "San Francisco")
2. **budget**: Budget range or amount (normalize to ranges like "0-50k", "100k-200k", "300k-500k", "500k-750k", "750k-1m", "1m+")
3. **bedrooms**: Number of bedrooms (e.g., "2", "3", "4")
4. **property_type**: Type of property (e.g., "apartment", "house", "villa", "condo")
5. **amenities**: List of desired amenities (e.g., ["parking", "gym", "pool"])
6. **urgency**: How urgent is the search (e.g., "immediate", "1-3 months", "just browsing")

User query: "{text}"

Return ONLY a valid JSON object with these fields. Use null for missing information.
Example format:
{{
  "location": "Mumbai",
  "budget": "300k-500k",
  "bedrooms": "2",
  "property_type": "apartment",
  "amenities": ["parking", "gym"],
  "urgency": "1-3 months"
}}

JSON response:"""

        response = _gemini_model.generate_content(prompt)
        
        if response and response.text:
            # Extract JSON from response
            text_response = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                entities = json.loads(json_str)
                
                # Clean up the extracted entities
                return {
                    "location": entities.get("location"),
                    "budget": entities.get("budget"),
                    "bedrooms": str(entities.get("bedrooms")) if entities.get("bedrooms") else None,
                    "property_type": entities.get("property_type"),
                    "amenities": entities.get("amenities") if isinstance(entities.get("amenities"), list) else None,
                    "urgency": entities.get("urgency")
                }
    
    except Exception as e:
        print(f"Error in LLM extraction: {e}")
    
    return {}


def classify_intent_with_llm(text: str) -> Dict[str, any]:
    """
    Classify user intent using Gemini LLM
    
    Args:
        text: User's message
    
    Returns:
        Dict with intent type and confidence
    """
    if not is_llm_available():
        return {"intent": "unknown", "confidence": 0.0}
    
    print(f"🎯 Classifying intent with Gemini LLM...")
    
    try:
        prompt = f"""You are an AI assistant that classifies user intents in a real estate chatbot context.

Classify the following user message into ONE of these intents:
1. **property_search**: User is searching for properties with specific criteria
2. **general_inquiry**: User is asking general questions about real estate
3. **greeting**: User is greeting or introducing themselves
4. **save_property**: User wants to save/bookmark a property
5. **view_saved**: User wants to see their saved properties
6. **smalltalk**: Casual conversation not related to real estate
7. **complaint**: User is expressing dissatisfaction
8. **unclear**: Message is unclear or ambiguous

User message: "{text}"

Return ONLY a valid JSON object with:
- "intent": one of the above intent types
- "confidence": a number between 0.0 and 1.0
- "reasoning": brief explanation (optional)

Example:
{{
  "intent": "property_search",
  "confidence": 0.95,
  "reasoning": "User is explicitly looking for 2 bedroom apartments"
}}

JSON response:"""

        response = _gemini_model.generate_content(prompt)
        
        if response and response.text:
            text_response = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
                return {
                    "intent": result.get("intent", "unknown"),
                    "confidence": float(result.get("confidence", 0.0)),
                    "reasoning": result.get("reasoning")
                }
    
    except Exception as e:
        print(f"Error in intent classification: {e}")
    
    return {"intent": "unknown", "confidence": 0.0}


def extract_preferences_with_llm(text: str) -> Dict[str, any]:
    """
    Extract additional user preferences beyond basic filters
    
    Args:
        text: User's message
    
    Returns:
        Dict with preferences like style, move_in_date, must_haves, etc.
    """
    if not is_llm_available():
        return {}
    
    try:
        prompt = f"""You are an AI assistant extracting detailed real estate preferences from user messages.

Extract the following detailed preferences:
1. **style**: Property style (e.g., "modern", "traditional", "minimalist", "luxury")
2. **move_in_date**: Desired move-in date or timeframe
3. **must_haves**: List of essential features (e.g., ["parking", "balcony", "natural light"])
4. **nice_to_haves**: List of preferred but not essential features
5. **deal_breakers**: Things the user definitely doesn't want
6. **family_size**: Information about household size
7. **work_from_home**: Whether user works from home (true/false)
8. **pets**: Whether user has pets

User message: "{text}"

Return ONLY a valid JSON object. Use null for missing information.
Example:
{{
  "style": "modern",
  "move_in_date": "immediate",
  "must_haves": ["parking", "gym"],
  "nice_to_haves": ["pool", "garden"],
  "deal_breakers": ["ground floor"],
  "family_size": 4,
  "work_from_home": true,
  "pets": false
}}

JSON response:"""

        response = _gemini_model.generate_content(prompt)
        
        if response and response.text:
            text_response = response.text.strip()
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', text_response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                preferences = json.loads(json_str)
                return preferences
    
    except Exception as e:
        print(f"Error in preference extraction: {e}")
    
    return {}


# Initialize on import
_initialize_gemini()
