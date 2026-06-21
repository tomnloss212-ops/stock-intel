"""
שליפת המחיר הנוכחי *ישירות* מהעמוד הרשמי של מאיה (אתר הבורסה) -
בלי שום תיווך, בלי שום אגרגטור זר, בלי המרת מטבע.

איך זה עובד: נכנסים לעמוד החברה הציבורי (מותר לפי robots.txt - לא
פונים בעצמנו ל-/api/ הפנימי שלהם), ופשוט קוראים את הטקסט המוצג
על המסך - בדיוק כמו שמשתמש אנושי היה עושה.

חשוב: המחיר ב"שער אחרון" מוצג באגורות, עם עיכוב של ~15 דקות
(הצהרה רשמית של הבורסה - זה הסטנדרט לנתונים ציבוריים חינמיים).
"""

import re
from playwright.sync_api import sync_playwright


def get_official_price(maya_company_id: int, security_id: int) -> dict:
    """קורא את המחיר המוצג בעמוד הרשמי של מאיה לחברה נתונה."""
    url = f"https://maya.tase.co.il/he/companies/{maya_company_id}?securityId={security_id}"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_timeout(7000)
        text = page.inner_text("body")
        browser.close()

    idx = text.find("שער אחרון")
    if idx == -1:
        return {"error": "לא נמצא שדה 'שער אחרון' בעמוד - ייתכן שהאתר השתנה"}

    snippet = text[idx:idx + 200]

    price_match = re.search(r"([\d,]+\.?\d*)\s*אג", snippet)
    change_match = re.search(r"([+-]?\d+\.?\d*)%", snippet)
    time_match = re.search(r"נכון ל\s*-\s*([\d/]+\s+[\d:]+)", snippet)

    price_agorot = float(price_match.group(1).replace(",", "")) if price_match else None

    return {
        "price_ils": round(price_agorot / 100, 2) if price_agorot else None,
        "change_percent": float(change_match.group(1)) if change_match else None,
        "as_of": time_match.group(1) if time_match else None,
        "source": "maya.tase.co.il (official TASE disclosure system)",
        "delayed_minutes": 15,
    }


if __name__ == "__main__":
    import sys
    import json

    company_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2028
    security_id = int(sys.argv[2]) if len(sys.argv) > 2 else 1138494
    print(json.dumps(get_official_price(company_id, security_id), indent=2, ensure_ascii=False))
