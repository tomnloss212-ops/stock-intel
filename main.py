"""
הרצה ראשית: מקבל טיקר, ומריץ את כל הצנרת -
מחיר+טכני -> דוח אחרון ממאיה -> חילוץ טקסט -> ניתוח AI.

שימוש:
    python main.py TSEM
    python main.py LUMI.TA
"""

import sys
import json
import subprocess
import platform
from dotenv import load_dotenv

load_dotenv()

from src.config import get_company
from src.price_technical import get_technical_snapshot
from src.maya_price import get_official_price
from src.reports_scraper import get_latest_report_pdf
from src.pdf_extractor import get_report_text
from src.ai_analyst import analyze


def open_url_in_chrome(url: str) -> None:
    if platform.system() != "Darwin":
        print("פתיחה ב-Google Chrome נתמכת רק על macOS.")
        return

    subprocess.run(["open", "-a", "Google Chrome", url], check=False)


def run(ticker: str):
    company = get_company(ticker)
    print(f"\n=== {company['name_he']} ({ticker}) ===\n")

    if company.get("maya_security_id"):
        print("[1/5] שולף מחיר רשמי ישירות ממאיה (מקור ישראלי מקורי)...")
        official_price = get_official_price(company["maya_company_id"], company["maya_security_id"])
        print(json.dumps(official_price, indent=2, ensure_ascii=False))
    else:
        print("[1/5] אין maya_security_id מוגדר - מדלג על מחיר רשמי ישיר.")

    print("\n[2/5] שולף היסטוריה ואינדיקטורים טכניים (Yahoo, נתוני ת\"א)...")
    technical = get_technical_snapshot(company["yahoo_symbol"])
    print(json.dumps(technical, indent=2, ensure_ascii=False))

    report_text = ""
    if company.get("maya_company_id"):
        print("\n[3/5] מחפש דוח אחרון במאיה...")
        report = get_latest_report_pdf(company["maya_company_id"])
        if report and report.get("pdf_url"):
            print(f"  נמצא: {report['title']}")
            print("  פותח את קישור ה-PDF ב-Google Chrome...")
            open_url_in_chrome(report["pdf_url"])
            print("\n[4/5] מחלץ טקסט מה-PDF...")
            report_text = get_report_text(report["pdf_url"])
        else:
            print("  לא נמצא דוח / לא נמצא קישור PDF.")
    else:
        print("\n[3/5] אין maya_company_id מוגדר לטיקר הזה - מדלג על דוחות.")

    print("\n[5/5] מריץ ניתוח AI...")
    if report_text:
        try:
            analysis = analyze(technical, report_text, company["name"])
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"  שגיאה בקריאה ל-Claude API: {e}")
            print("  בדקו שהגדרתם ANTHROPIC_API_KEY בקובץ .env")
    else:
        print("  אין טקסט דוח - מדלג על ניתוח AI מלא (אפשר להרחיב לניתוח טכני בלבד).")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("שימוש: python main.py <TICKER>")
        sys.exit(1)
    run(sys.argv[1])
