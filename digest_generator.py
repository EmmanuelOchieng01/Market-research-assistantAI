"""
Generates market digest reports — HTML and plain text.
Summarises all articles from the last 24 hours into an executive report.
"""
from datetime import datetime, timedelta
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

def generate_digest(articles, commodity_stats, sentiment_stats, period_hours=24):
    """
    Build a structured digest from recent articles.
    Returns both a plain dict and an HTML string.
    """
    if not articles:
        return {'sections': [], 'html': '<p>No articles found in the selected period.</p>'}

    cutoff = datetime.utcnow() - timedelta(hours=period_hours)

    # Filter recent
    recent = []
    for a in articles:
        try:
            pub = datetime.fromisoformat(a.get('fetched_at','') or a.get('published',''))
            if pub >= cutoff:
                recent.append(a)
        except:
            recent.append(a)

    if not recent:
        recent = articles[:20]

    # Overall sentiment
    scores = [a.get('sentiment_score',0) for a in recent]
    avg_score = sum(scores)/len(scores) if scores else 0
    overall = 'Bullish' if avg_score >= 0.2 else ('Bearish' if avg_score <= -0.2 else 'Neutral')

    # Top stories — highest absolute sentiment score
    top_stories = sorted(recent, key=lambda x: abs(x.get('sentiment_score',0)), reverse=True)[:5]

    # Most mentioned commodities
    comm_count = {}
    for a in recent:
        for c in (a.get('commodities') or []):
            comm_count[c] = comm_count.get(c, 0) + 1
    top_commodities = sorted(comm_count.items(), key=lambda x: -x[1])[:5]

    # Sources breakdown
    source_count = {}
    for a in recent:
        s = a.get('source','Unknown')
        source_count[s] = source_count.get(s, 0) + 1

    # Sentiment distribution
    dist = {'positive':0,'negative':0,'neutral':0}
    for a in recent:
        lbl = a.get('sentiment_label','neutral')
        dist[lbl] = dist.get(lbl, 0) + 1

    digest = {
        'generated_at':   datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
        'period_hours':   period_hours,
        'total_articles': len(recent),
        'overall_trend':  overall,
        'avg_sentiment':  round(avg_score, 3),
        'top_stories':    top_stories,
        'top_commodities':top_commodities,
        'source_breakdown':source_count,
        'sentiment_dist': dist,
        'commodity_stats':commodity_stats[:8],
    }

    digest['html'] = _build_html(digest)
    return digest

def _build_html(d):
    ts = d['generated_at']
    trend_color = '#00BFA5' if d['overall_trend']=='Bullish' else ('#E05252' if d['overall_trend']=='Bearish' else '#C9A84C')

    stories_html = ''
    for s in d['top_stories']:
        sc = s.get('sentiment_score',0)
        sc_color = '#00BFA5' if sc>=0.2 else ('#E05252' if sc<=-0.2 else '#C9A84C')
        url  = s.get('url','#')
        stories_html += f"""
        <div style="background:#0D1220;border:1px solid #1C2A40;border-left:3px solid {sc_color};
                    border-radius:8px;padding:1rem 1.2rem;margin-bottom:0.75rem;">
            <div style="font-size:0.95rem;color:#EAF0F8;font-weight:600;margin-bottom:0.4rem;">
                <a href="{url}" style="color:#EAF0F8;text-decoration:none;" target="_blank">{s.get('title','')}</a>
            </div>
            <div style="font-size:0.8rem;color:#5A7090;margin-bottom:0.4rem;">{s.get('source','')} &nbsp;·&nbsp; {s.get('published','')[:10]}</div>
            <div style="font-size:0.82rem;color:#C8D8E8;">{s.get('ai_summary') or s.get('summary','')[:200]}</div>
            <div style="margin-top:0.5rem;font-size:0.72rem;font-family:monospace;color:{sc_color};">
                Sentiment: {s.get('sentiment_label','neutral').upper()} ({sc:+.3f})
            </div>
        </div>"""

    comms_html = ''.join(
        f'<span style="background:#1C2A40;color:#C9A84C;padding:0.3rem 0.75rem;border-radius:4px;'
        f'font-size:0.78rem;font-family:monospace;">{c} ({n})</span> '
        for c, n in d['top_commodities']
    )

    comm_stats_html = ''
    for cs in d.get('commodity_stats',[]):
        tc = '#00BFA5' if cs['trend']=='bullish' else ('#E05252' if cs['trend']=='bearish' else '#C9A84C')
        comm_stats_html += f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 0;border-bottom:1px solid #0F1923;font-size:0.82rem;">
            <span style="color:#C8D8E8;text-transform:capitalize;">{cs['commodity']}</span>
            <span style="color:{tc};font-family:monospace;">{cs['trend'].upper()} &nbsp; {cs['avg_score']:+.3f} &nbsp; ({cs['count']} articles)</span>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Market Digest — {ts}</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Instrument+Serif&family=DM+Mono:wght@400;500&family=Sora:wght@400;600&display=swap');
  body{{background:#05080F;color:#C8D8E8;font-family:'Sora',sans-serif;padding:2rem;max-width:860px;margin:0 auto;}}
  h1{{font-family:'Instrument Serif',serif;font-size:2rem;color:#EAF0F8;}}
  h2{{font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.2em;text-transform:uppercase;color:#C9A84C;margin:2rem 0 1rem 0;border-bottom:1px solid #141E30;padding-bottom:0.5rem;}}
  .meta{{font-family:'DM Mono',monospace;font-size:0.65rem;color:#3A4A60;margin-bottom:2rem;}}
  .badge{{display:inline-block;padding:0.3rem 0.9rem;border-radius:4px;font-family:'DM Mono',monospace;font-size:0.72rem;font-weight:600;}}
</style>
</head>
<body>
<h1>Market Intelligence Digest</h1>
<div class="meta">Generated: {ts} &nbsp;·&nbsp; Period: Last {d['period_hours']} hours &nbsp;·&nbsp; Articles analysed: {d['total_articles']}</div>

<h2>Overall Market Sentiment</h2>
<span class="badge" style="background:rgba(201,168,76,0.1);color:{trend_color};border:1px solid {trend_color};">
    {d['overall_trend'].upper()} &nbsp; {d['avg_sentiment']:+.3f}
</span>
&nbsp;
<span style="font-size:0.82rem;color:#5A7090;margin-left:1rem;">
    {d['sentiment_dist'].get('positive',0)} positive &nbsp;·&nbsp;
    {d['sentiment_dist'].get('negative',0)} negative &nbsp;·&nbsp;
    {d['sentiment_dist'].get('neutral',0)} neutral
</span>

<h2>Top Stories</h2>
{stories_html}

<h2>Most Mentioned Commodities</h2>
<div style="display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:1rem;">{comms_html}</div>

<h2>Commodity Sentiment Breakdown</h2>
{comm_stats_html}

<div style="margin-top:3rem;border-top:1px solid #141E30;padding-top:1rem;
            font-family:'DM Mono',monospace;font-size:0.6rem;color:#1C2A40;">
    AI Market Research Assistant &nbsp;·&nbsp; For informational purposes only &nbsp;·&nbsp; Not investment advice
</div>
</body></html>"""
