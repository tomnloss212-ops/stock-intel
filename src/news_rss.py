from __future__ import annotations

"""
שלד בסיסי לשליפת חדשות מ-RSS (Globes/Calcalist). לא מחובר עדיין ל-main.py.

להרחבה עתידית: לסנן לפי שם חברה/טיקר, להוסיף NewsAPI לחדשות גלובליות.
"""

import feedparser  # יש להוסיף ל-requirements.txt אם משתמשים בזה: pip install feedparser

RSS_FEEDS = {
    "globes": "https://www.globes.co.il/webservice/rss/rssfeeder.asmx/FeederNode?iID=2",
    # יש לאתר ולעדכן כתובות RSS מדויקות נוספות (Calcalist וכו') בהתאם לצורך
}


def get_latest_news(feed_key: str = "globes", limit: int = 10) -> list[dict]:
    feed_url = RSS_FEEDS.get(feed_key)
    if not feed_url:
        raise ValueError(f"Feed '{feed_key}' not configured")

    parsed = feedparser.parse(feed_url)
    return [
        {"title": entry.title, "link": entry.link, "published": entry.get("published", "")}
        for entry in parsed.entries[:limit]
    ]


if __name__ == "__main__":
    for item in get_latest_news():
        print(item["title"], "-", item["link"])
