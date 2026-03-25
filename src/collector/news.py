"""
Collector berita per ticker dari Google News RSS.

Menggunakan Google News RSS dengan query: "{TICKER} IDX saham"
Hasilnya berita terbaru yang relevan dengan emiten tersebut.

Tidak butuh auth.
"""

import time
import re
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional
import httpx
import config
from src.database.connection import get_connection

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=id&gl=ID&ceid=ID:id"
NEWS_HEADERS    = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def _clean(text: str) -> str:
    """Hapus CDATA dan HTML tags sederhana."""
    if not text:
        return ""
    text = re.sub(r'<!\[CDATA\[(.*?)\]\]>', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()


def _parse_rss_date(date_str: str) -> Optional[str]:
    """Parse RFC 2822 date dari RSS → 'YYYY-MM-DD HH:MM:SS'."""
    if not date_str:
        return None
    try:
        dt = parsedate_to_datetime(date_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def _parse_rss(xml_text: str) -> list:
    """Parse XML RSS feed → list of article dicts."""
    articles = []
    items = re.findall(r'<item>(.*?)<\/item>', xml_text, re.DOTALL)
    for item in items:
        def _tag(tag):
            m = re.search(rf'<{tag}[^>]*>(.*?)<\/{tag}>', item, re.DOTALL)
            return _clean(m.group(1)) if m else ""

        title     = _tag("title")
        link      = _tag("link")
        pub_date  = _tag("pubDate")
        source    = _tag("source")
        desc      = _tag("description")
        guid      = _tag("guid") or link

        if not title or not guid:
            continue

        articles.append({
            "news_id":      guid[:150],
            "title":        title[:500],
            "summary":      desc[:1000] if desc else None,
            "url":          link[:500] if link else None,
            "image_url":    None,
            "published_at": _parse_rss_date(pub_date),
            "source":       source[:100] if source else None,
        })

    return articles


def fetch_news(ticker: str, company_name: str = None, limit: int = 15) -> list:
    """
    Fetch berita terbaru untuk ticker dari Google News RSS.
    Gunakan company_name jika tersedia untuk hasil lebih akurat.
    """
    queries = [
        f"{ticker} saham IDX",
    ]
    if company_name:
        queries.insert(0, company_name)

    all_articles = []
    seen_ids = set()

    for query in queries:
        encoded = query.replace(" ", "+")
        url = GOOGLE_NEWS_RSS.format(query=encoded)

        try:
            resp = httpx.get(url, headers=NEWS_HEADERS, timeout=20, follow_redirects=True)
            if resp.status_code != 200:
                print(f"[news] HTTP {resp.status_code} untuk query '{query}'")
                continue

            articles = _parse_rss(resp.text)
            for a in articles:
                if a["news_id"] not in seen_ids:
                    seen_ids.add(a["news_id"])
                    all_articles.append(a)

            print(f"[news] {len(articles)} artikel untuk query '{query}'")

        except Exception as e:
            print(f"[news] Error query '{query}': {e}")

        if len(all_articles) >= limit:
            break

        time.sleep(0.5)

    result = all_articles[:limit]
    print(f"[news] Total {len(result)} artikel untuk {ticker}")
    return result


def save_news(symbol: str, articles: list):
    """Simpan berita ke DB (INSERT IGNORE by news_id)."""
    if not articles:
        return
    conn = get_connection()
    saved = 0
    try:
        cur = conn.cursor()
        for a in articles:
            cur.execute(
                """
                INSERT IGNORE INTO news
                    (symbol, news_id, title, summary, url, image_url, published_at, source)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (symbol, a["news_id"], a["title"], a.get("summary"),
                 a.get("url"), a.get("image_url"), a.get("published_at"), a.get("source")),
            )
            saved += cur.rowcount
        conn.commit()
        print(f"[news] {saved} artikel baru tersimpan untuk {symbol}.")
    finally:
        conn.close()


def get_news_rows(symbol: str, limit: int = 10) -> list:
    """Ambil berita terbaru dari DB."""
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT news_id, title, source, published_at, url "
            "FROM news WHERE symbol = %s "
            "ORDER BY published_at DESC LIMIT %s",
            (symbol, limit),
        )
        return cur.fetchall()
    finally:
        conn.close()
