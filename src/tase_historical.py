from __future__ import annotations

"""
שליפת הטבלה ההיסטורית על ידי קריאת הטקסט המוצג בעמוד (לא ה-API),
לאחר שהמניה נמצאת ב"אחזקות שלי" ב-TASE Plus (וה-session מחובר).
"""

from playwright.sync_api import sync_playwright

AUTH_STATE_FILE = "auth_state.json"


def fetch_historical_visible(security_id: int, period_label: str = "חצי שנה") -> str:
    url = f"https://market.tase.co.il/he/market_data/security/{security_id}/historical_data/eod"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state=AUTH_STATE_FILE)
        page = context.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_timeout(4000)

        try:
            page.get_by_text(period_label, exact=True).first.click(timeout=5000)
            page.wait_for_timeout(4000)
        except Exception as e:
            print(f"[DEBUG] לא נמצא/נלחץ כפתור '{period_label}': {e}")

        text = page.inner_text("body")

        input("\n[DEBUG] בדקו את חלון הדפדפן - יש דאטה בטבלה? לחצו Enter להמשיך... ")
        browser.close()

    return text


if __name__ == "__main__":
    import sys

    security_id = int(sys.argv[1]) if len(sys.argv) > 1 else 1138494
    text = fetch_historical_visible(security_id)
    idx = text.find("תאריך")
    print(text[idx:idx + 2000] if idx != -1 else text[:2000])