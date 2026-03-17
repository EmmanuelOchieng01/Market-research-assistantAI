"""
SQLite database operations for article storage and retrieval.
"""
import sqlite3
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path("data/articles.db")

def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS articles (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            summary     TEXT,
            url         TEXT UNIQUE,
            source      TEXT,
            published   TEXT,
            fetched_at  TEXT,
            sentiment_score  REAL DEFAULT 0,
            sentiment_label  TEXT DEFAULT 'neutral',
            keywords    TEXT,
            commodities TEXT,
            entities    TEXT,
            ai_summary  TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_published   ON articles(published);
        CREATE INDEX IF NOT EXISTS idx_sentiment   ON articles(sentiment_label);
        CREATE INDEX IF NOT EXISTS idx_source      ON articles(source);
    """)
    conn.commit()
    conn.close()

def save_article(article: dict) -> bool:
    conn = get_conn()
    try:
        conn.execute("""
            INSERT OR IGNORE INTO articles
            (title, summary, url, source, published, fetched_at,
             sentiment_score, sentiment_label, keywords, commodities, entities, ai_summary)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            article.get('title',''),
            article.get('summary',''),
            article.get('url',''),
            article.get('source',''),
            article.get('published',''),
            datetime.utcnow().isoformat(),
            article.get('sentiment_score', 0),
            article.get('sentiment_label', 'neutral'),
            json.dumps(article.get('keywords', [])),
            json.dumps(article.get('commodities', [])),
            json.dumps(article.get('entities', [])),
            article.get('ai_summary',''),
        ))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def get_articles(limit=100, sentiment=None, commodity=None, source=None, search=None):
    conn = get_conn()
    q  = "SELECT * FROM articles WHERE 1=1"
    p  = []
    if sentiment and sentiment != 'all':
        q += " AND sentiment_label=?"; p.append(sentiment)
    if commodity and commodity != 'all':
        q += " AND commodities LIKE ?"; p.append(f'%"{commodity}"%')
    if source and source != 'all':
        q += " AND source=?"; p.append(source)
    if search:
        q += " AND (title LIKE ? OR summary LIKE ? OR ai_summary LIKE ?)"
        p += [f'%{search}%', f'%{search}%', f'%{search}%']
    q += " ORDER BY fetched_at DESC LIMIT ?"
    p.append(limit)
    rows = conn.execute(q, p).fetchall()
    conn.close()
    result = []
    for r in rows:
        d = dict(r)
        for f in ['keywords','commodities','entities']:
            try:    d[f] = json.loads(d[f] or '[]')
            except: d[f] = []
        result.append(d)
    return result

def get_sentiment_stats():
    conn = get_conn()
    rows = conn.execute("""
        SELECT sentiment_label, COUNT(*) as count,
               AVG(sentiment_score) as avg_score
        FROM articles GROUP BY sentiment_label
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_commodity_stats():
    conn = get_conn()
    rows = conn.execute("SELECT commodities, sentiment_score FROM articles").fetchall()
    conn.close()
    stats = {}
    for r in rows:
        try:
            comms = json.loads(r['commodities'] or '[]')
        except:
            comms = []
        for c in comms:
            if c not in stats:
                stats[c] = {'count':0,'score_sum':0}
            stats[c]['count']     += 1
            stats[c]['score_sum'] += r['sentiment_score']
    result = []
    for c, v in sorted(stats.items(), key=lambda x: -x[1]['count']):
        avg = v['score_sum']/v['count'] if v['count'] else 0
        result.append({
            'commodity': c,
            'count':     v['count'],
            'avg_score': round(avg,3),
            'trend':     'bullish' if avg>=0.2 else ('bearish' if avg<=-0.2 else 'neutral')
        })
    return result

def get_total_count():
    conn = get_conn()
    n = conn.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
    conn.close()
    return n

def get_sources():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT source FROM articles ORDER BY source").fetchall()
    conn.close()
    return [r['source'] for r in rows]
