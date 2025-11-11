"""
NLP Configuration Module
Customize entity extraction patterns and thresholds
"""

# Fuzzy matching threshold (0.0 to 1.0)
# Higher = stricter matching, Lower = more lenient
FUZZY_MATCH_THRESHOLD = 0.75

# Budget ranges configuration (in base currency)
# Adjust these ranges based on your market
BUDGET_RANGES = [
    (0, 50000, "0-50k"),
    (50000, 100000, "50k-100k"),
    (100000, 200000, "100k-200k"),
    (200000, 300000, "200k-300k"),
    (300000, 500000, "300k-500k"),
    (500000, 750000, "500k-750k"),
    (750000, 1000000, "750k-1m"),
    (1000000, float('inf'), "1m+")
]

# Currency multipliers
CURRENCY_MULTIPLIERS = {
    'k': 1000,
    'thousand': 1000,
    'l': 100000,
    'lakh': 100000,
    'lac': 100000,
    'm': 1000000,
    'million': 1000000,
    'cr': 10000000,
    'crore': 10000000,
    'b': 1000000000,
    'billion': 1000000000,
}

# Bedroom extraction patterns
# Add more patterns if needed
BEDROOM_PATTERNS = [
    r'(\d+)\s*(?:bhk|bedroom|bed|br|room)',
    r'(?:bhk|bedroom|bed|br)\s*(\d+)',
    r'(\d+)\s*(?:bed|br)\b',
]

# Number words to numeric mapping
NUMBER_WORDS = {
    "one": "1", "two": "2", "three": "3",
    "four": "4", "five": "5", "six": "6",
    "seven": "7", "eight": "8", "nine": "9",
    "ten": "10"
}

# Minimum word length for fuzzy matching
MIN_WORD_LENGTH_FOR_FUZZY = 3

# Maximum bedrooms (for validation)
MAX_BEDROOMS = 10

# Fallback cities (if property data not available)
FALLBACK_CITIES = [
    "new york", "miami", "los angeles", "austin", "san francisco",
    "chicago", "dallas", "seattle", "boston", "mumbai", "delhi",
    "bangalore", "pune", "hyderabad", "chennai"
]
