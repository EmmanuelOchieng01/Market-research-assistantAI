"""
Extractive article summarizer.
Scores sentences by keyword frequency and position — no API needed.
Works on any length of text from a phrase to a full article.
"""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import NLP_CONFIG

try:
    from nltk.tokenize import sent_tokenize, word_tokenize
    from nltk.corpus import stopwords
    _USE_NLTK = True
except:
    _USE_NLTK = False

def _get_stopwords():
    if _USE_NLTK:
        try:
            from nltk.corpus import stopwords
            return set(stopwords.words('english'))
        except:
            pass
    return {'the','a','an','and','or','but','in','on','at','to','for',
            'of','with','by','from','is','are','was','were','be','been'}

def summarize(text, max_sentences=3):
    """
    Summarize any text. Returns the most informative sentences.
    Falls back gracefully for short inputs.
    """
    if not text or not text.strip():
        return ''

    text = text.strip()
    words = text.split()

    # Too short to summarize — return as is
    if len(words) < 20:
        return text

    # Tokenize sentences
    if _USE_NLTK:
        try:
            sentences = sent_tokenize(text)
        except:
            sentences = re.split(r'(?<=[.!?])\s+', text)
    else:
        sentences = re.split(r'(?<=[.!?])\s+', text)

    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

    if len(sentences) <= max_sentences:
        return ' '.join(sentences)

    # Score sentences
    stop = _get_stopwords()
    word_freq = {}
    for sent in sentences:
        for w in sent.lower().split():
            w = re.sub(r'[^a-z]', '', w)
            if w and w not in stop and len(w) > 2:
                word_freq[w] = word_freq.get(w, 0) + 1

    scores = []
    for i, sent in enumerate(sentences):
        score = 0
        for w in sent.lower().split():
            w = re.sub(r'[^a-z]', '', w)
            score += word_freq.get(w, 0)
        # Boost first and last sentences
        if i == 0:
            score *= 1.5
        if i == len(sentences) - 1:
            score *= 1.2
        scores.append((score, i, sent))

    # Pick top sentences, preserve original order
    top = sorted(scores, reverse=True)[:max_sentences]
    top = sorted(top, key=lambda x: x[1])
    return ' '.join(s[2] for s in top)
