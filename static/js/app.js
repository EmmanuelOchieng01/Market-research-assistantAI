// ── State ──────────────────────────────────────────────────
let currentTab  = 'dashboard';
let statsCache  = null;

const COMMODITIES = ['corn','wheat','soybeans','rice','coffee','cotton',
                     'sugar','cocoa','cattle','hogs','gold','oil','copper'];

const darkLayout = {
    paper_bgcolor:'rgba(0,0,0,0)', plot_bgcolor:'rgba(0,0,0,0)',
    font:{color:'#C8D8E8', family:'DM Mono, monospace', size:11},
    xaxis:{gridcolor:'#141E30', color:'#5A7090', linecolor:'#1C2A40'},
    yaxis:{gridcolor:'#141E30', color:'#5A7090', linecolor:'#1C2A40'},
};

// ── Tab navigation ─────────────────────────────────────────
function showTab(name) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    document.querySelectorAll('.nav-btn')[
        ['dashboard','articles','analyse','digest'].indexOf(name)
    ].classList.add('active');
    currentTab = name;
    if (name === 'articles')  loadArticles();
    if (name === 'dashboard') loadStats();
}

// ── Load dashboard stats ───────────────────────────────────
async function loadStats() {
    try {
        const r = await fetch('/api/stats');
        const d = await r.json();
        statsCache = d;

        document.getElementById('hp-total').textContent = d.total + ' articles';
        document.getElementById('kpi-total').textContent = d.total.toLocaleString();

        const pos = d.sentiment.find(s => s.sentiment_label === 'positive');
        const neg = d.sentiment.find(s => s.sentiment_label === 'negative');
        const neu = d.sentiment.find(s => s.sentiment_label === 'neutral');
        document.getElementById('kpi-pos').textContent = pos ? pos.count : 0;
        document.getElementById('kpi-neg').textContent = neg ? neg.count : 0;
        document.getElementById('kpi-neu').textContent = neu ? neu.count : 0;
        document.getElementById('kpi-src').textContent = d.sources.length;

        renderSentimentChart(d.sentiment);
        renderCommodityChart(d.commodities);
        renderCommodityTrends(d.commodities);
        populateFilters(d.sources);
    } catch(e) {
        console.error('Stats error:', e);
    }
}

function renderSentimentChart(data) {
    if (!data || !data.length) return;
    const labels = data.map(d => d.sentiment_label);
    const values = data.map(d => d.count);
    const colors = labels.map(l => l==='positive'?'#00BFA5':l==='negative'?'#E05252':'#C9A84C');
    Plotly.newPlot('chart-sentiment', [{
        labels, values, type:'pie', hole:0.5,
        marker:{colors},
        textfont:{color:'#C8D8E8', size:11}
    }], {
        ...darkLayout,
        margin:{t:10,b:10,l:10,r:10},
        showlegend:true,
        legend:{orientation:'h', y:-0.1, font:{size:10}}
    }, {responsive:true, displayModeBar:false});
}

function renderCommodityChart(data) {
    if (!data || !data.length) return;
    const top = data.slice(0,10);
    Plotly.newPlot('chart-commodities', [{
        x: top.map(d => d.commodity),
        y: top.map(d => d.count),
        type:'bar',
        marker:{
            color: top.map(d => d.trend==='bullish'?'#00BFA5':d.trend==='bearish'?'#E05252':'#C9A84C'),
            line:{width:0}
        },
        text: top.map(d => d.count),
        textposition:'outside',
        textfont:{color:'#C8D8E8', size:10}
    }], {
        ...darkLayout,
        yaxis:{...darkLayout.yaxis, title:'Article Count'},
        margin:{t:10,b:60,l:50,r:10},
        showlegend:false
    }, {responsive:true, displayModeBar:false});
}

function renderCommodityTrends(data) {
    const box = document.getElementById('commodity-trends');
    if (!data || !data.length) {
        box.innerHTML = '<div style="color:var(--dim);font-size:0.82rem;padding:1rem;">No commodity data yet. Fetch news first.</div>';
        return;
    }
    box.innerHTML = data.slice(0,13).map(d => {
        const tc = d.trend==='bullish'?'#00BFA5':d.trend==='bearish'?'#E05252':'#C9A84C';
        const bar = Math.min(Math.abs(d.avg_score)*500, 100);
        return `
        <div style="padding:0.75rem 1rem;border-bottom:1px solid var(--border);">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem;">
            <span style="font-family:'Sora',sans-serif;font-size:0.84rem;color:var(--bright);text-transform:capitalize;">${d.commodity}</span>
            <span style="font-family:'DM Mono',monospace;font-size:0.7rem;color:${tc};">
              ${d.trend.toUpperCase()} &nbsp; ${d.avg_score>=0?'+':''}${d.avg_score.toFixed(3)} &nbsp; (${d.count})
            </span>
          </div>
          <div style="background:var(--border);border-radius:2px;height:3px;">
            <div style="background:${tc};width:${bar}%;height:100%;border-radius:2px;"></div>
          </div>
        </div>`;
    }).join('');
}

function populateFilters(sources) {
    const commSel = document.getElementById('f-commodity');
    commSel.innerHTML = '<option value="all">All Commodities</option>' +
        COMMODITIES.map(c => `<option value="${c}">${c.charAt(0).toUpperCase()+c.slice(1)}</option>`).join('');

    const srcSel = document.getElementById('f-source');
    srcSel.innerHTML = '<option value="all">All Sources</option>' +
        sources.map(s => `<option value="${s}">${s}</option>`).join('');
}

// ── Scrape news ────────────────────────────────────────────
async function scrapeNews() {
    const btn = document.getElementById('btn-scrape');
    btn.disabled = true; btn.textContent = 'Fetching...';
    const bar = document.getElementById('scrape-status');
    bar.style.display = 'block';
    bar.textContent   = 'Connecting to news sources...';
    bar.className     = 'status-bar info';

    try {
        const r = await fetch('/api/scrape', {method:'POST'});
        const d = await r.json();
        bar.textContent = d.message;
        bar.className   = 'status-bar success';
        await loadStats();
        toast(d.message, 'success');
    } catch(e) {
        bar.textContent = 'Error: ' + e.message;
        bar.className   = 'status-bar error';
        toast('Scrape failed: ' + e.message, 'error');
    } finally {
        btn.disabled = false; btn.textContent = 'Fetch Latest News';
    }
}

// ── Load articles ──────────────────────────────────────────
async function loadArticles() {
    const params = new URLSearchParams({
        limit:     document.getElementById('f-limit')?.value || 50,
        sentiment: document.getElementById('f-sentiment')?.value || 'all',
        commodity: document.getElementById('f-commodity')?.value || 'all',
        source:    document.getElementById('f-source')?.value || 'all',
        search:    document.getElementById('f-search')?.value || '',
    });

    try {
        const r = await fetch('/api/articles?' + params);
        const articles = await r.json();
        renderArticles(articles);
    } catch(e) {
        document.getElementById('articles-list').innerHTML =
            '<div style="color:var(--red);padding:1rem;">Error loading articles: ' + e.message + '</div>';
    }
}

function renderArticles(articles) {
    const count = document.getElementById('article-count');
    count.textContent = articles.length + ' articles';

    if (!articles.length) {
        document.getElementById('articles-list').innerHTML =
            '<div class="empty-state">No articles found. Try fetching news from the Dashboard tab.</div>';
        return;
    }

    document.getElementById('articles-list').innerHTML = articles.map(a => {
        const sc = a.sentiment_score || 0;
        const sc_color = sc>=0.2?'#00BFA5':sc<=-0.2?'#E05252':'#C9A84C';
        const label    = (a.sentiment_label||'neutral').toUpperCase();
        const comms    = (a.commodities||[]).slice(0,4).map(c =>
            `<span class="tag">${c}</span>`).join('');
        const kws      = (a.keywords||[]).slice(0,5).map(k =>
            `<span class="tag dim">${k}</span>`).join('');
        return `
        <div class="article-card" style="border-left-color:${sc_color}">
          <div class="article-header">
            <a href="${a.url||'#'}" target="_blank" class="article-title">${a.title||'Untitled'}</a>
            <span class="sentiment-badge" style="color:${sc_color};border-color:${sc_color};">
              ${label} ${sc>=0?'+':''}${sc.toFixed(3)}
            </span>
          </div>
          <div class="article-meta">${a.source||''} &nbsp;·&nbsp; ${(a.published||'').substring(0,10)}</div>
          <div class="article-summary">${a.ai_summary || a.summary || ''}</div>
          <div class="article-tags">${comms}${kws}</div>
        </div>`;
    }).join('');
}

// ── Analyse text ───────────────────────────────────────────
function setExample(text) {
    document.getElementById('analyse-input').value = text;
}

async function analyseText() {
    const text = document.getElementById('analyse-input').value.trim();
    if (!text) { toast('Enter some text to analyse.', 'warn'); return; }

    document.getElementById('analyse-loading').style.display = 'flex';
    document.getElementById('analyse-results').style.display = 'none';

    try {
        const r = await fetch('/api/analyse', {
            method:'POST', headers:{'Content-Type':'application/json'},
            body: JSON.stringify({text})
        });
        const d = await r.json();
        if (d.error) { toast('Error: ' + d.error, 'error'); return; }
        renderAnalysis(d, text);
    } catch(e) {
        toast('Analysis failed: ' + e.message, 'error');
    } finally {
        document.getElementById('analyse-loading').style.display = 'none';
    }
}

function renderAnalysis(d, inputText) {
    const box = document.getElementById('analyse-results');
    box.style.display = 'block';

    const sc = d.sentiment.score;
    const sc_color = sc>=0.2?'#00BFA5':sc<=-0.2?'#E05252':'#C9A84C';
    const trend_color = d.trend.trend==='bullish'?'#00BFA5':d.trend.trend==='bearish'?'#E05252':'#C9A84C';

    const comms = (d.nlp.commodities||[]).map(c =>
        `<span class="tag" style="color:#00BFA5;border-color:rgba(0,191,165,0.3);">${c}</span>`).join('') || '<span style="color:var(--dim);font-size:0.78rem;">None detected</span>';

    const entities = (d.nlp.entities||[]).slice(0,10).map(e =>
        `<span class="tag">${e}</span>`).join('') || '<span style="color:var(--dim);font-size:0.78rem;">None detected</span>';

    const keywords = (d.nlp.keywords||[]).slice(0,10).map(k =>
        `<span class="tag dim">${k}</span>`).join('') || '<span style="color:var(--dim);font-size:0.78rem;">—</span>';

    const related = (d.related||[]).slice(0,3).map(a => `
        <div style="padding:0.6rem 0;border-bottom:1px solid var(--border);">
          <a href="${a.url||'#'}" target="_blank" style="color:var(--text);font-size:0.82rem;text-decoration:none;">${a.title||''}</a>
          <div style="font-size:0.72rem;color:var(--muted);margin-top:0.2rem;">${a.source||''}</div>
        </div>`).join('') || '<div style="color:var(--dim);font-size:0.82rem;">No related articles in database yet.</div>';

    box.innerHTML = `
    <div class="sl">Analysis Results</div>

    <div class="kpi-strip" style="margin-bottom:1.5rem;">
      <div class="kpi">
        <div class="kpi-label">Sentiment</div>
        <div class="kpi-val" style="color:${sc_color};">${d.sentiment.label.toUpperCase()}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Score</div>
        <div class="kpi-val" style="color:${sc_color};">${sc>=0?'+':''}${sc.toFixed(3)}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Market Trend</div>
        <div class="kpi-val" style="color:${trend_color};">${d.trend.trend.toUpperCase()}</div>
      </div>
      <div class="kpi">
        <div class="kpi-label">Word Count</div>
        <div class="kpi-val">${d.input_length}</div>
      </div>
    </div>

    ${d.nlp.note ? `<div style="background:rgba(201,168,76,0.08);border:1px solid rgba(201,168,76,0.2);border-radius:8px;padding:0.75rem 1rem;font-size:0.8rem;color:var(--gold);margin-bottom:1rem;">${d.nlp.note}</div>` : ''}

    ${d.summary && d.summary !== inputText ? `
    <div class="sl">AI Summary</div>
    <div class="chart-box" style="margin-bottom:1rem;">
      <div style="font-size:0.84rem;color:var(--text);line-height:1.7;">${d.summary}</div>
    </div>` : ''}

    <div class="sl">Sentiment Breakdown</div>
    <div class="chart-box" style="margin-bottom:1rem;">
      <div style="display:flex;gap:2rem;font-family:'DM Mono',monospace;font-size:0.78rem;">
        <span style="color:#00BFA5;">Positive: ${d.sentiment.positive.toFixed(3)}</span>
        <span style="color:#E05252;">Negative: ${d.sentiment.negative.toFixed(3)}</span>
        <span style="color:#C9A84C;">Neutral: ${d.sentiment.neutral.toFixed(3)}</span>
      </div>
    </div>

    <div class="sl">Commodities Detected</div>
    <div class="chart-box" style="margin-bottom:1rem;">${comms}</div>

    <div class="sl">Named Entities</div>
    <div class="chart-box" style="margin-bottom:1rem;">${entities}</div>

    <div class="sl">Keywords</div>
    <div class="chart-box" style="margin-bottom:1rem;">${keywords}</div>

    <div class="sl">Related Articles in Database</div>
    <div class="chart-box">${related}</div>
    `;
}

// ── Digest ─────────────────────────────────────────────────
async function generateDigest() {
    const hours = document.getElementById('digest-hours').value;
    document.getElementById('digest-loading').style.display = 'flex';
    document.getElementById('digest-content').style.display  = 'none';

    try {
        const r = await fetch('/api/digest?hours=' + hours);
        const d = await r.json();
        renderDigest(d);
        document.getElementById('digest-content').style.display = 'block';
    } catch(e) {
        toast('Digest error: ' + e.message, 'error');
    } finally {
        document.getElementById('digest-loading').style.display = 'none';
    }
}

function renderDigest(d) {
    const tc = d.overall_trend==='Bullish'?'#00BFA5':d.overall_trend==='Bearish'?'#E05252':'#C9A84C';

    document.getElementById('digest-header').innerHTML = `
    <div style="display:flex;gap:2rem;align-items:center;flex-wrap:wrap;">
      <div><div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);margin-bottom:0.3rem;">GENERATED</div>
           <div style="font-family:'DM Mono',monospace;font-size:0.8rem;color:var(--text);">${d.generated_at}</div></div>
      <div><div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);margin-bottom:0.3rem;">ARTICLES</div>
           <div style="font-family:'Instrument Serif',serif;font-size:1.5rem;color:var(--bright);">${d.total_articles}</div></div>
      <div><div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);margin-bottom:0.3rem;">OVERALL TREND</div>
           <div style="font-family:'Instrument Serif',serif;font-size:1.5rem;color:${tc};">${d.overall_trend}</div></div>
      <div><div style="font-family:'DM Mono',monospace;font-size:0.6rem;color:var(--muted);margin-bottom:0.3rem;">AVG SENTIMENT</div>
           <div style="font-family:'DM Mono',monospace;font-size:1rem;color:${tc};">${d.avg_sentiment>=0?'+':''}${d.avg_sentiment.toFixed(3)}</div></div>
    </div>`;

    document.getElementById('digest-stories').innerHTML = (d.top_stories||[]).map(s => {
        const sc = s.sentiment_score||0;
        const sc_c = sc>=0.2?'#00BFA5':sc<=-0.2?'#E05252':'#C9A84C';
        return `
        <div class="article-card" style="border-left-color:${sc_c};margin-bottom:0.75rem;">
          <a href="${s.url||'#'}" target="_blank" class="article-title">${s.title||''}</a>
          <div class="article-meta">${s.source||''} &nbsp;·&nbsp; ${(s.published||'').substring(0,10)}</div>
          <div class="article-summary">${s.ai_summary||s.summary||''}</div>
          <div style="font-family:'DM Mono',monospace;font-size:0.68rem;color:${sc_c};margin-top:0.4rem;">
            ${(s.sentiment_label||'').toUpperCase()} ${sc>=0?'+':''}${sc.toFixed(3)}
          </div>
        </div>`;
    }).join('') || '<div class="empty-state">No stories available.</div>';

    document.getElementById('digest-commodities').innerHTML = (d.commodity_stats||[]).map(cs => {
        const tc2 = cs.trend==='bullish'?'#00BFA5':cs.trend==='bearish'?'#E05252':'#C9A84C';
        return `
        <div style="display:flex;justify-content:space-between;padding:0.65rem 0;border-bottom:1px solid var(--border);font-family:'DM Mono',monospace;font-size:0.78rem;">
          <span style="color:var(--text);text-transform:capitalize;">${cs.commodity}</span>
          <span style="color:${tc2};">${cs.trend.toUpperCase()} &nbsp; ${cs.avg_score>=0?'+':''}${cs.avg_score.toFixed(3)} &nbsp; (${cs.count})</span>
        </div>`;
    }).join('') || '<div style="color:var(--dim);font-size:0.82rem;">No commodity data.</div>';

    const dist = d.sentiment_dist||{};
    document.getElementById('digest-dist').innerHTML = `
    <div style="display:flex;gap:1rem;flex-wrap:wrap;">
      <div class="kpi green"><div class="kpi-label">Positive</div><div class="kpi-val green">${dist.positive||0}</div></div>
      <div class="kpi red">  <div class="kpi-label">Negative</div><div class="kpi-val red"  >${dist.negative||0}</div></div>
      <div class="kpi gold"> <div class="kpi-label">Neutral</div> <div class="kpi-val gold" >${dist.neutral||0}</div></div>
    </div>`;
}

async function downloadDigest() {
    const hours = document.getElementById('digest-hours').value;
    window.open('/api/digest/html?hours=' + hours, '_blank');
}

// ── Utilities ──────────────────────────────────────────────
function toast(msg, type='info') {
    const c = {success:'#00BFA5', warn:'#C9A84C', error:'#E05252', info:'#3b82f6'};
    const t = document.createElement('div');
    t.style.cssText = `position:fixed;bottom:2rem;right:2rem;background:#0D1220;
        border:1px solid ${c[type]||c.info};color:#E2E8F0;padding:0.9rem 1.4rem;
        border-radius:8px;font-family:'DM Mono',monospace;font-size:0.78rem;
        z-index:9999;box-shadow:0 8px 30px rgba(0,0,0,0.5);max-width:360px;line-height:1.5;`;
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 4000);
}

// ── Boot ───────────────────────────────────────────────────
window.onload = () => {
    loadStats();
};
