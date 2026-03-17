"""
Flask application — AI Market Research Assistant
"""
from flask import Flask, render_template, request, jsonify, Response
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.database        import init_db, save_article, get_articles, get_sentiment_stats, get_commodity_stats, get_total_count, get_sources
from src.scraper         import scrape_all
from src.nlp_processor   import process_text
from src.summarizer      import summarize
from src.sentiment       import SentimentAnalyzer
from src.digest_generator import generate_digest

app      = Flask(__name__)
analyzer = SentimentAnalyzer()
init_db()

def process_article(article):
    """Run full NLP pipeline on a single article."""
    text = f"{article.get('title','')} {article.get('summary','')}"
    nlp  = process_text(text)
    sent = analyzer.analyze(text)
    summ = summarize(article.get('summary','') or article.get('title',''))
    article.update({
        'sentiment_score':  sent['score'],
        'sentiment_label':  sent['label'],
        'keywords':         nlp['keywords'],
        'commodities':      nlp['commodities'],
        'entities':         nlp['entities'],
        'ai_summary':       summ,
    })
    return article

# ── Routes ─────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def stats():
    return jsonify({
        'total':      get_total_count(),
        'sentiment':  get_sentiment_stats(),
        'commodities':get_commodity_stats(),
        'sources':    get_sources(),
    })

@app.route('/api/articles')
def articles():
    limit     = int(request.args.get('limit', 50))
    sentiment = request.args.get('sentiment', 'all')
    commodity = request.args.get('commodity', 'all')
    source    = request.args.get('source', 'all')
    search    = request.args.get('search', '')
    rows = get_articles(limit=limit, sentiment=sentiment,
                        commodity=commodity, source=source,
                        search=search if search else None)
    return jsonify(rows)

@app.route('/api/scrape', methods=['POST'])
def scrape():
    """Fetch articles from all RSS feeds and process them."""
    scraped = scrape_all()
    saved = 0
    for article in scraped:
        article = process_article(article)
        if save_article(article):
            saved += 1
    return jsonify({
        'scraped': len(scraped),
        'saved':   saved,
        'message': f'Fetched {len(scraped)} articles, saved {saved} new.'
    })

@app.route('/api/analyse', methods=['POST'])
def analyse():
    """
    Analyse any text — word, phrase, or full article.
    Returns full NLP + sentiment results.
    """
    data = request.json or {}
    text = (data.get('text') or '').strip()
    if not text:
        return jsonify({'error': 'No text provided'}), 400

    nlp  = process_text(text)
    sent = analyzer.analyze(text)
    trend= analyzer.get_sentiment_trend([sent])
    summ = summarize(text) if len(text.split()) > 20 else text

    # Find related articles in DB
    related = []
    if nlp['commodities']:
        related = get_articles(limit=5, commodity=nlp['commodities'][0])
    if not related and nlp['keywords']:
        related = get_articles(limit=5, search=nlp['keywords'][0])

    return jsonify({
        'input_length': len(text.split()),
        'sentiment':    sent,
        'trend':        trend,
        'nlp':          nlp,
        'summary':      summ,
        'related':      related,
        'note':         nlp.get('note',''),
    })

@app.route('/api/digest')
def digest():
    hours = int(request.args.get('hours', 24))
    articles_data   = get_articles(limit=200)
    commodity_stats = get_commodity_stats()
    sentiment_stats = get_sentiment_stats()
    result = generate_digest(articles_data, commodity_stats, sentiment_stats, period_hours=hours)
    return jsonify({k:v for k,v in result.items() if k != 'html'})

@app.route('/api/digest/html')
def digest_html():
    hours = int(request.args.get('hours', 24))
    articles_data   = get_articles(limit=200)
    commodity_stats = get_commodity_stats()
    sentiment_stats = get_sentiment_stats()
    result = generate_digest(articles_data, commodity_stats, sentiment_stats, period_hours=hours)
    return Response(result['html'], mimetype='text/html',
                    headers={'Content-Disposition':'attachment;filename=market_digest.html'})

if __name__ == '__main__':
    print("Starting AI Market Research Assistant...")
    print("Server ready at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
