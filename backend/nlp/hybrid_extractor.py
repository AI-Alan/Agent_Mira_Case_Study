"""
Hybrid NLP Extractor - Combines rule-based and LLM extraction
Uses rules for fast, reliable extraction and LLM for complex cases
"""

from typing import Dict, Optional, List
from nlp.extractor import extract_filters as rule_based_extract
from nlp.llm_extractor import (
    extract_entities_with_llm,
    classify_intent_with_llm,
    extract_preferences_with_llm,
    is_llm_available
)


def extract_with_hybrid(text: str, use_llm: bool = True) -> Dict:
    """
    Extract entities using hybrid approach: rules first, LLM as fallback/enhancement
    
    Strategy:
    1. Try rule-based extraction (fast, reliable for common patterns)
    2. If rules miss entities and LLM available, use LLM
    3. Merge results, preferring rule-based for structured fields
    4. Add LLM-only fields (preferences, intent)
    
    Args:
        text: User's natural language query
        use_llm: Whether to use LLM (default True if available)
    
    Returns:
        Dict with all extracted information
    """
    result = {
        "location": None,
        "budget": None,
        "bedrooms": None,
        "property_type": None,
        "amenities": None,
        "intent": None,
        "preferences": {},
        "extraction_method": "rule-based"
    }
    
    # Step 1: Rule-based extraction (always try first - it's fast)
    rule_results = rule_based_extract(text)
    
    if rule_results:
        result["location"] = rule_results.get("location")
        result["budget"] = rule_results.get("budget")
        result["bedrooms"] = rule_results.get("bedrooms")
    
    # Count how many entities were found by rules
    entities_found = sum(1 for v in [result["location"], result["budget"], result["bedrooms"]] if v)
    
    if entities_found > 0:
        print(f"📋 Rule-based extraction found {entities_found} entities: {rule_results}")
    
    # Step 2: LLM extraction (if enabled and available)
    llm_is_available = is_llm_available()
    
    if use_llm and llm_is_available:
        # Use LLM if:
        # a) Rules found nothing or only 1 entity (might be complex query)
        # b) Always extract additional info (intent, preferences)
        
        if entities_found <= 1:
            print(f"💡 Using LLM to enhance extraction (only {entities_found} entity found by rules)")
            # Try LLM extraction for basic entities
            llm_results = extract_entities_with_llm(text)
            
            if llm_results:
                # Merge results: use LLM values only if rule-based didn't find them
                if not result["location"] and llm_results.get("location"):
                    result["location"] = llm_results["location"]
                    result["extraction_method"] = "hybrid"
                
                if not result["budget"] and llm_results.get("budget"):
                    result["budget"] = llm_results["budget"]
                    result["extraction_method"] = "hybrid"
                
                if not result["bedrooms"] and llm_results.get("bedrooms"):
                    result["bedrooms"] = llm_results["bedrooms"]
                    result["extraction_method"] = "hybrid"
                
                # LLM-only fields
                result["property_type"] = llm_results.get("property_type")
                result["amenities"] = llm_results.get("amenities")
        
        # Step 3: Intent classification (always do this with LLM)
        intent_result = classify_intent_with_llm(text)
        result["intent"] = intent_result.get("intent")
        result["intent_confidence"] = intent_result.get("confidence")
        
        # Step 4: Extract detailed preferences (if it looks like a property search)
        if result["intent"] in ["property_search", "general_inquiry"]:
            preferences = extract_preferences_with_llm(text)
            if preferences:
                result["preferences"] = preferences
                result["extraction_method"] = "hybrid"
    elif use_llm and not llm_is_available:
        print("⚠️  LLM requested but not available - using rule-based only")
    
    # Log final result
    if entities_found > 0 or result.get("intent"):
        method = result.get("extraction_method", "rule-based")
        print(f"✨ Extraction complete using: {method}")
    
    return result


def should_use_llm_for_query(text: str, rule_results: Dict) -> bool:
    """
    Decide if LLM should be used based on query complexity
    
    Args:
        text: User's query
        rule_results: Results from rule-based extraction
    
    Returns:
        Boolean indicating if LLM should be used
    """
    # Use LLM if:
    # 1. Query is long and conversational (> 15 words)
    word_count = len(text.split())
    if word_count > 15:
        return True
    
    # 2. Contains uncertainty or questions
    uncertainty_markers = ["maybe", "perhaps", "not sure", "?", "looking for", "need help"]
    if any(marker in text.lower() for marker in uncertainty_markers):
        return True
    
    # 3. Rules found nothing
    entities_found = sum(1 for v in rule_results.values() if v)
    if entities_found == 0:
        return True
    
    # 4. Contains complex preferences
    preference_keywords = [
        "must have", "prefer", "need", "require", "would like",
        "important", "essential", "nice to have", "work from home",
        "pets", "family", "kids", "style", "modern", "luxury"
    ]
    if any(keyword in text.lower() for keyword in preference_keywords):
        return True
    
    return False


def get_search_summary(extraction_result: Dict) -> str:
    """
    Generate a human-readable summary of extracted information
    
    Args:
        extraction_result: Result from extract_with_hybrid
    
    Returns:
        Human-readable summary string
    """
    parts = []
    
    if extraction_result.get("bedrooms"):
        parts.append(f"{extraction_result['bedrooms']} bedroom")
    
    if extraction_result.get("property_type"):
        parts.append(extraction_result["property_type"])
    else:
        parts.append("property")
    
    if extraction_result.get("location"):
        parts.append(f"in {extraction_result['location']}")
    
    if extraction_result.get("budget"):
        parts.append(f"(budget: {extraction_result['budget']})")
    
    if not parts:
        return "property search"
    
    return " ".join(parts)


# Convenience function for backward compatibility
def extract_filters(text: str, use_llm: bool = True) -> Dict[str, Optional[str]]:
    """
    Extract basic filters (location, budget, bedrooms) using hybrid approach
    Returns format compatible with existing code
    
    Args:
        text: User's query
        use_llm: Whether to use LLM enhancement
    
    Returns:
        Dict with location, budget, bedrooms
    """
    result = extract_with_hybrid(text, use_llm=use_llm)
    
    return {
        "location": result.get("location"),
        "budget": result.get("budget"),
        "bedrooms": result.get("bedrooms")
    }
