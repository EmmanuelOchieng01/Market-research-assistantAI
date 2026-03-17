"""
NLP pipeline — keywords, entity extraction, commodity detection.
Works on a single word, a phrase, or a full article.
"""
import re
import string
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import COMMODITIES, NLP_CONFIG

import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

# Commodity aliases — maps variations to canonical name
COMMODITY_ALIASES = {
    'corn': ['corn','maize','cornmeal','grain corn'],
    'wheat': ['wheat','durum','hard wheat','soft wheat'],
    'soybeans': ['soybean','soybeans','soy','soya'],
    'rice': ['rice','paddy','brown rice'],
    'coffee': ['coffee','arabica','robusta'],
    'cotton': ['cotton','fibre','fiber'],
    'sugar': ['sugar','sucrose','cane sugar'],
    'cocoa': ['cocoa','cacao','chocolate'],
    'cattle': ['cattle','beef','cow','bovine','livestock'],
    'hogs': ['hog','hogs','pork','swine','pig'],
    'gold': ['gold','bullion','xau'],
    'oil': ['oil','crude','petroleum','brent','wti','barrel'],
    'copper': ['copper','cu','metal'],
}

# Flatten alias map for fast lookup
ALIAS_MAP = {}
for canonical, aliases in COMMODITY_ALIASES.items():
    for a in aliases:
        ALIAS_MAP[a.lower()] = canonical

# Common business/financial entities (fallback when NLTK NER is not available)
ORG_HINTS = ['ltd','inc','corp','company','group','bank','fund','exchange',
             'association','ministry','usda','fao','who','opec','imf']

def _ensure_nltk():
    for pkg in ['punkt','stopwords','averaged_perceptron_tagger',
                'maxent_ne_chunker','words','wordnet','punkt_tab']:
        try:
            nltk.data.find(f'tokenizers/{pkg}')
        except:
            try:
                nltk.download(pkg, quiet=True)
            except:
                pass

_ensure_nltk()
_lemmatizer  = WordNetLemmatizer()
try:
    _stopwords = set(stopwords.words('english'))
except:
    _stopwords = set()

_stopwords.update(['said','says','would','could','also','one','two','new',
                   'year','years','month','week','day','time','today',
                   'according','percent','per','us','u.s','reuters','bloomberg'])

def extract_keywords(text, top_n=None):
    if not text or not text.strip():
        return []
    top_n = top_n or NLP_CONFIG['top_keywords']
    try:
        tokens = word_tokenize(text.lower())
    except:
        tokens = text.lower().split()
    words = [
        _lemmatizer.lemmatize(t) for t in tokens
        if t.isalpha() and len(t) > 2
        and t not in _stopwords
        and t not in string.punctuation
    ]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]

def detect_commodities(text):
    if not text:
        return []
    lower = text.lower()
    found = set()
    for alias, canonical in ALIAS_MAP.items():
        pattern = r'\b' + re.escape(alias) + r'\b'
        if re.search(pattern, lower):
            found.add(canonical)
    return sorted(found)

def extract_entities(text):
    """
    Extract named entities. Uses NLTK NE chunker when available,
    falls back to capitalised word heuristic — works on any system.
    """
    if not text or not text.strip():
        return []
    entities = set()
    # Method 1: NLTK NE chunker
    try:
        tokens = word_tokenize(text)
        tagged = nltk.pos_tag(tokens)
        chunks = nltk.ne_chunk(tagged)
        for chunk in chunks:
            if hasattr(chunk, 'label') and chunk.label() in ('PERSON','ORGANIZATION','GPE','FACILITY'):
                name = ' '.join(c[0] for c in chunk)
                if len(name) > 2:
                    entities.add(name)
    except:
        pass
    # Method 2: Capitalised words heuristic (fallback)
    words = text.split()
    for i, w in enumerate(words):
        clean = w.strip('.,;:()[]"\'')
        if (len(clean) > 2 and clean[0].isupper() and clean.lower() not in _stopwords
                and i > 0):  # skip first word of sentence
            entities.add(clean)
    # Remove commodity names and common words from entities
    comm_words = set(ALIAS_MAP.keys())
    entities = {e for e in entities if e.lower() not in comm_words and len(e) > 2}
    return sorted(entities)[:15]

def process_text(text):
    """
    Full NLP pipeline on any input — word, phrase, or full article.
    Always returns something useful regardless of input length.
    """
    if not text:
        text = ''
    text = text.strip()

    # Handle very short input
    if len(text.split()) <= 3:
        commodities = detect_commodities(text)
        keywords    = [w.lower() for w in text.split() if len(w) > 2]
        return {
            'keywords':    keywords,
            'commodities': commodities,
            'entities':    [],
            'word_count':  len(text.split()),
            'sentences':   1,
            'note':        'Short input — commodity detection and keyword extraction applied.'
        }

    keywords    = extract_keywords(text)
    commodities = detect_commodities(text)
    entities    = extract_entities(text)

    try:
        sentences = len(sent_tokenize(text))
    except:
        sentences = text.count('.') + 1

    return {
        'keywords':    keywords,
        'commodities': commodities,
        'entities':    entities,
        'word_count':  len(text.split()),
        'sentences':   sentences,
        'note':        ''
    }
