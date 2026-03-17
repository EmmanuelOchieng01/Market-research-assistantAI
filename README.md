# AI Market Research Assistant

An automated intelligence system that collects, structures, and summarises global commodity and agriculture news using NLP and sentiment analysis. Converts unstructured news data into organised market insights that support strategic decision-making.

---

## What it does

The system scrapes articles from multiple public RSS feeds, runs every article through a full NLP pipeline, and presents the results in an interactive dashboard. A loan officer, commodity trader, or agribusiness analyst can open it and immediately understand market sentiment across 13 commodities — without reading a single article manually.

**Built to demonstrate:** Automated research workflows, NLP in business intelligence, full-stack development, and practical AI application in financial and agricultural contexts.

---

## Core capabilities

**News Scraper** — Fetches articles from Reuters, Yahoo Finance, CNBC, AgWeb, Farm Journal, Nasdaq, MarketWatch, and Investing.com. No API keys required. All public RSS feeds.

**NLP Pipeline** — Extracts keywords, detects commodity mentions, identifies named entities (companies, people, locations), and generates extractive summaries. Works on any input length — a single word, a phrase, or a full article.

**Sentiment Analysis** — VADER-based scoring. Every article is classified as positive, negative, or neutral with a confidence score. Commodity-level sentiment trends show whether market mood is bullish, bearish, or neutral.

**Analyse Any Text** — Paste anything into the analysis panel. A single word like "corn" returns commodity detection. A phrase like "wheat prices falling" returns sentiment and keywords. A full article returns summary, entities, sentiment breakdown, and related articles from the database.

**Market Digest** — One-click executive report covering the last 24 hours, 48 hours, or 7 days. Shows top stories, overall market trend, commodity sentiment breakdown, and source distribution. Downloadable as a standalone HTML file you can send to a client or manager.

**SQLite Database** — All articles stored locally. Filterable by sentiment, commodity, source, and keyword search.

---

## Commodities tracked

Corn, Wheat, Soybeans, Rice, Coffee, Cotton, Sugar, Cocoa, Cattle, Hogs, Gold, Oil, Copper

---

## Launch Procedure

Requirements: Python 3.8+

```bash
git clone https://github.com/EmmanuelOchieng01/Market-research-assistantAI
cd Market-research-assistantAI
pip install -r requirements.txt
python setup.py
python app.py
```

Open your browser at **http://localhost:5000**

First launch: `setup.py` downloads NLTK language models and initialises the database. Takes about 30 seconds. Run it only once.

---

## How to use it

1. Open the **Dashboard** tab
2. Click **Fetch Latest News** — the scraper pulls articles from all sources
3. Watch the sentiment charts and commodity trend bars populate automatically
4. Go to **Articles** to browse, filter, and search all fetched articles
5. Go to **Analyse Text** — type or paste anything and click Run Analysis
6. Go to **Market Digest** — click Generate Digest for an executive summary report, then Download HTML to save it

---

## Project structure

```
├── app.py                      # Flask server and all API endpoints
├── setup.py                    # One-time NLTK download and DB init
├── config.py                   # RSS feeds, commodities, NLP settings
├── requirements.txt
├── src/
│   ├── database.py             # SQLite operations
│   ├── scraper.py              # RSS feed fetcher
│   ├── nlp_processor.py        # Keywords, entities, commodity detection
│   ├── summarizer.py           # Extractive summarization
│   ├── sentiment.py            # VADER sentiment analysis
│   ├── entity_extractor.py     # Entity extraction wrapper
│   └── digest_generator.py     # Market digest report builder
├── templates/
│   └── index.html              # Full dashboard
├── static/
│   ├── css/style.css
│   └── js/app.js
└── data/
    └── articles.db             # Auto-created on first run
```

---

## Tech stack

**Backend** — Python, Flask, NLTK, VADER Sentiment, BeautifulSoup4, Feedparser

**Frontend** — HTML, CSS, JavaScript, Plotly.js

**Database** — SQLite

**NLP** — VADER (sentiment), NLTK (tokenization, POS tagging, NER), extractive summarization

---

## Author

**Emmanuel Ochieng**
GitHub: https://github.com/EmmanuelOchieng01

---

*For educational and portfolio purposes. Not investment advice.*
