from __future__ import annotations

"""
מריץ את כל הצנרת (מחיר + טכני + דוח + ניתוח AI) על כל המניות
המוגדרות ב-config.py, ושומר את התוצאות לקובץ JSON יחיד שה-dashboard
(docs/index.html) קורא ומציג.

שימוש מקומי:
    python3 src/run_all.py
"""

import json
import datetime
import traceback

from src.config import COMPANIES
from src.price_technical import get_technical_snapshot
from src.maya_price import get_official_price
from src.reports_scraper import get_latest_report_pdf
from src.pdf_extractor import get_report_text
from src.ai_analyst import analyze

OUTPUT_PATH = "docs/data.json"


def process_ticker(ticker: str, company: dict) -> dict:
    result = {
        "ticker": ticker,
        "name": company["name"],
        "name_he": company["name_he"],
        "official_price": None,
        "technical": None,
        "report_title": None,
        "analysis": None,
        "errors": [],
    }

    if company.get("maya_security_id"):
        try:
            result["official_price"] = get_official_price(
                company["maya_company_id"], company["maya_security_id"]
            )
        except Exception as e:
            result["errors"].append(f"official_price: {e}")

    try:
        result["technical"] = get_technical_snapshot(company["yahoo_symbol"])
    except Exception as e:
        result["errors"].append(f"technical: {e}")

    report_text = ""
    if company.get("maya_company_id"):
        try:
            report = get_latest_report_pdf(company["maya_company_id"])
            if report and report.get("pdf_url"):
                result["report_title"] = report["title"]
                report_text = get_report_text(report["pdf_url"])
        except Exception as e:
            result["errors"].append(f"report: {e}")

    if report_text and result["technical"]:
        try:
            result["analysis"] = analyze(result["technical"], report_text, company["name"])
        except Exception as e:
            result["errors"].append(f"ai_analysis: {e}")

    return result


def main():
    output = {
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "stocks": {},
    }

    for ticker, company in COMPANIES.items():
        print(f"=== מעבד {ticker} ({company['name_he']}) ===")
        try:
            output["stocks"][ticker] = process_ticker(ticker, company)
        except Exception as e:
            print(f"שגיאה כללית ב-{ticker}: {e}")
            traceback.print_exc()
            output["stocks"][ticker] = {"ticker": ticker, "errors": [str(e)]}

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nנשמר ל-{OUTPUT_PATH}")


if __name__ == "__main__":
    main()