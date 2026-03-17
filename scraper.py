"""
Multi-source RSS scraper for commodity and agriculture news.
Uses only public feeds — no API keys required.
"""
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import SCRAPING_CONFIG

# Public RSS feeds — tested and working
RSS_FEEDS = {
    'Yahoo Finance - Commodities': 'https://finance.yahoo.com/rss/headline?s=GC=F,CL=F,ZC=F,ZW=F,ZS=F',
    'Reuters - Markets':           'https://feeds.reuters.com/reuters/businessNews',
    'CNBC - Economy':              'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258',
    'Investing.com - Commodities': 'https://www.investing.com/rss/news_14.rss',
    'AgWeb - Agriculture':         'https://www.agweb.com/rss/news',
    'Farm Journal':                'https://www.farmprogress.com/rss.xml',
    'Nasdaq - Commodities':        'https://www.nasdaq.com/feed/rssoutbound?category=Commodities',
    'MarketWatch - Commodities':   'https://feeds.marketwatch.com/marketwatch/topstories/',
}

def _parse_date(entry):
    for attr in ['published_parsed','updated_parsed']:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6]).isoformat()
            except:
                pass
    return datetime.utcnow().isoformat()

def _clean_html(text):
    if not text:
        return ''
    try:
        return BeautifulSoup(text, 'lxml').get_text(separator=' ').strip()
    except:
        return BeautifulSoup(text, 'html.parser').get_text(separator=' ').strip()

def scrape_feed(name, url, max_articles=50):
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_articles]:
            title   = _clean_html(getattr(entry, 'title', ''))
            summary = _clean_html(getattr(entry, 'summary', getattr(entry, 'description', '')))
            link    = getattr(entry, 'link', '')
            if not title or not link:
                continue
            articles.append({
                'title':     title,
                'summary':   summary[:500],
                'url':       link,
                'source':    name,
                'published': _parse_date(entry),
            })
            time.sleep(0.1)
    except Exception as e:
        print(f"  Feed error [{name}]: {e}")
    return articles

def scrape_all(progress_callback=None):
    all_articles = []
    total = len(RSS_FEEDS)
    for i, (name, url) in enumerate(RSS_FEEDS.items()):
        if progress_callback:
            progress_callback(i+1, total, name)
        articles = scrape_feed(name, url, SCRAPING_CONFIG['max_articles_per_source'])
        all_articles.extend(articles)
        time.sleep(SCRAPING_CONFIG['request_delay'])
    return all_articles
