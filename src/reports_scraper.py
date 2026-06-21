from __future__ import annotations

"""
שליפת רשימת הדוחות האחרונים + קישור ה-PDF הישיר ממאיה (TASE), באמצעות Playwright.

חשוב:
- גולשים רק בעמודים הציבוריים (כמו דפדפן רגיל), לא פונים ל-/api/ הפנימי
  שמוגדר Disallow ב-robots.txt של מאיה.
- האתר הוא Single Page Application - הקישור האמיתי ל-PDF מתגלה רק
  על ידי מעקב אחרי בקשות הרשת בזמן שהדפדפן טוען את העמוד.
"""

import re
import time
import subprocess
import platform
from playwright.sync_api import sync_playwright

BASE_URL = "https://maya.tase.co.il/he"


def open_url_in_chrome(url: str) -> None:
    if platform.system() != "Darwin":
        print("פתיחה ב-Google Chrome נתמכת רק על macOS.")
        return

    subprocess.run(["open", "-a", "Google Chrome", url], check=False)


def get_recent_reports(company_id: int, limit: int = 10) -> list[dict]:
    """מחזיר רשימת דוחות אחרונים: כותרת + מזהה דוח."""
    url = f"{BASE_URL}/companies/{company_id}/reports?eventsFamilyIds%5B%5D=100"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, timeout=30000)
        page.wait_for_timeout(5000)
        content = page.content()
        browser.close()

    matches = re.findall(r'href="(/he/reports/\d+)"[^>]*><!----> ([^<]+)</a>', content)
    reports = [
        {"report_id": int(href.split("/")[-1]), "title": title.strip()}
        for href, title in matches[:limit]
    ]
    return reports


def get_report_pdf_url(report_id: int) -> str | None:
    """נכנס לעמוד הדוח, ומלכד את קישור ה-PDF האמיתי ממעקב הרשת."""
    found_urls = []

    def handle_response(response):
        if "mayafiles" in response.url and response.url.lower().endswith(".pdf"):
            found_urls.append(response.url)

    url = f"{BASE_URL}/reports/{report_id}?attachmentType=pdf1"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.on("response", handle_response)
        page.goto(url, timeout=30000)
        page.wait_for_timeout(6000)
        browser.close()

    return found_urls[0] if found_urls else None


def get_latest_report_pdf(company_id: int) -> dict | None:
    """פונקציית-על: מוצא את הדוח האחרון ומחזיר את הכותרת + קישור ה-PDF שלו."""
    reports = get_recent_reports(company_id, limit=5)
    if not reports:
        return None

    latest = reports[0]
    time.sleep(1)  # נימוס - לא לקפוץ מבקשה לבקשה בלי השהיה
    pdf_url = get_report_pdf_url(latest["report_id"])

    return {
        "title": latest["title"],
        "report_id": latest["report_id"],
        "pdf_url": pdf_url,
    }


if __name__ == "__main__":
    import sys
    import json

    company_id = int(sys.argv[1]) if len(sys.argv) > 1 else 2028  # default: Tower
    result = get_latest_report_pdf(company_id)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result and result.get("pdf_url"):
        print("פותח את קישור ה-PDF ב-Google Chrome...")
        open_url_in_chrome(result["pdf_url"])
