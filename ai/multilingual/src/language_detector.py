# ai/multilingual/src/language_detector.py
# Simple language detection stub
# This is a placeholder until actual language detection models are integrated

import re


LANGUAGE_NAMES = {
    "en": "English",
    "am": "Amharic",
    "or": "Afaan Oromo",
    "ti": "Tigrinya",
    "unknown": "Unknown"
}


def detect_language(text: str) -> str:
    """
    Detect the language of the text.
    
    This is a stub implementation using simple heuristics.
    Replace with actual language detection (langdetect or fasttext) when available.
    """
    if not text or len(text.strip()) == 0:
        return "unknown"
    
    text = text.lower().strip()
    
    # Simple heuristics based on character patterns
    # Amharic script
    if re.search(r'[\u1200-\u137F]', text):
        return "am"
    
    # Check for common English words
    english_words = ['the', 'is', 'are', 'was', 'were', 'have', 'has', 'had', 
                     'road', 'damage', 'water', 'broken', 'problem']
    word_count = sum(1 for word in english_words if word in text)
    if word_count >= 2:
        return "en"
    
    # Check for Latin alphabet
    if re.search(r'[a-z]', text):
        return "en"  # Default to English for Latin script
    
    return "unknown"


def get_language_name(lang_code: str) -> str:
    """Get the full name of a language from its code."""
    return LANGUAGE_NAMES.get(lang_code, "Unknown")
