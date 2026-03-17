"""
Named entity extraction — wraps nlp_processor for clean API.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.nlp_processor import extract_entities, detect_commodities, extract_keywords

def extract_all(text):
    """
    Returns entities, commodities, and keywords from any text.
    Safe to call with a single word.
    """
    return {
        'entities':    extract_entities(text),
        'commodities': detect_commodities(text),
        'keywords':    extract_keywords(text),
    }
