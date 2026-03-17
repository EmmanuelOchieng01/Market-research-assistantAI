# AI Market Research Assistant

An automated intelligence system that collects, structures, and summarises global commodity and agriculture news using NLP and sentiment analysis. Converts unstructured news data into organised market insights that support strategic decision-making and competitive analysis.

Built to demonstrate practical application of AI tools in business intelligence workflows — automated research, real-time sentiment tracking, and executive report generation.

---

## What it does

The system fetches articles from multiple public news RSS feeds, runs every article through a full NLP pipeline, and presents results in an interactive dashboard. A commodity trader, loan officer, or agribusiness analyst can open it and immediately understand market sentiment across 13 commodities — without reading a single article manually.

---

## Core features

**News Scraper** — Fetches articles from Reuters, Yahoo Finance, CNBC, AgWeb, Farm Journal, Nasdaq, MarketWatch, and Investing.com. No API keys required. All public feeds.

**NLP Pipeline** — Extracts keywords, detects commodity mentions, identifies named entities (companies, people, locations), and generates extractive article summaries automatically.

**Sentiment Analysis** — Every article is scored using VADER sentiment analysis and classified as positive, negative, or neutral. Commodity-level trend indicators show whether market mood is bullish, bearish, or neutral.

**Analyse Any Text** — The analysis panel accepts anything from a single word to a full pasted article. A word like "corn" returns commodity detection and related articles. A phrase like "wheat prices falling" returns sentiment scoring and keywords. A full article returns a complete NLP report — summary, entities, sentiment breakdown, and related articles from the database.

**Market Digest** — One-click executive report covering the last 24 hours, 48 hours, or 7 days. Shows top stories ranked by sentiment intensity, overall market trend, commodity sentiment breakdown, and source distribution. Downloadable as a standalone HTML report you can send to a client or manager.

**Article Browser** — Filterable by sentiment, commodity, source, and keyword search. Every article shows its AI-generated summary, sentiment score, detected commodities, and extracted keywords.

**SQLite Database** — All articles stored locally. No external database required.

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

`setup.py` runs once — it downloads the NLTK language models and creates the database. Takes about 30 seconds. After that, only `python app.py` is needed on subsequent runs.

---

## How to use it

1. Open the **Dashboard** tab — this shows sentiment charts and commodity trends
2. Click **Fetch Latest News** to pull articles from all sources
3. Watch the sentiment distribution and commodity trend bars populate in real time
4. Go to **Articles** to browse, filter by sentiment or commodity, and search by keyword
5. Go to **Analyse Text** — type or paste anything and click Run Analysis
6. Go to **Market Digest** — click Generate Digest for an executive summary, then Download HTML to save and share it

---

## Project structure

```
├── app.py                      # Flask server and all API endpoints
├── setup.py                    # One-time NLTK download and database init
├── config.py                   # RSS feed URLs, commodities list, NLP settings
├── requirements.txt
├── src/
│   ├── database.py             # SQLite article storage and retrieval
│   ├── scraper.py              # Multi-source RSS feed fetcher
│   ├── nlp_processor.py        # Keywords, entities, commodity detection
│   ├── summarizer.py           # Extractive article summarization
│   ├── sentiment.py            # VADER sentiment analysis
│   ├── entity_extractor.py     # Entity extraction wrapper
│   └── digest_generator.py     # Market digest report builder
├── templates/
│   └── index.html              # Full dashboard — 4 tabs
├── static/
│   ├── css/style.css
│   └── js/app.js
└── data/
    └── articles.db             # Auto-created on first run
```

---

## Tech stack

**Backend** — Python, Flask, NLTK, VADER Sentiment, BeautifulSoup4, Feedparser, SQLite

**Frontend** — HTML, CSS, Vanilla JavaScript, Plotly.js

**NLP** — VADER (sentiment scoring), NLTK (tokenization, POS tagging, named entity recognition), extractive summarization

---

## Skills demonstrated

Automated data collection and structuring · Natural language processing · Sentiment analysis · Named entity recognition · Business intelligence dashboard · Full-stack web development · SQLite database design · Extractive summarization · REST API design

---

## Author

**Emmanuel Ochieng**
GitHub: https://github.com/EmmanuelOchieng01

---

*For educational and portfolio purposes. Not investment advice.*
