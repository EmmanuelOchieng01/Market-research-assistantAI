"""
One-time setup — downloads NLTK models and initialises the database.
Run this once before starting the app.
"""
import sys
print("AI Market Research Assistant — Setup")
print("─" * 40)

# NLTK models
print("\n[1/2] Downloading NLP models...")
import nltk
models = ['punkt','punkt_tab','stopwords','averaged_perceptron_tagger',
          'maxent_ne_chunker','words','wordnet']
for m in models:
    try:
        nltk.download(m, quiet=True)
        print(f"  ✓ {m}")
    except Exception as e:
        print(f"  ! {m} — {e}")

# Database
print("\n[2/2] Initialising database...")
sys.path.insert(0, '.')
from src.database import init_db
init_db()
print("  ✓ Database ready at data/articles.db")

print("\nSetup complete. Run: python app.py")
