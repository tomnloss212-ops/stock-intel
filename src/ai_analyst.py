"""
שכבת ניתוח AI - מקבלת דאטה גולמי (טכני + טקסט מהדוח) ומחזירה ניתוח בסטייל אנליסט.

הפרומפט מתמקד בכוונה רק ב-5-6 הדברים שאנליסטים אמיתיים בודקים ראשונים,
ולא מנסה "לחלץ הכל" - זה חוסך עלות וזמן עיבוד, ונותן תוצר ממוקד.
"""

import os
import json
from anthropic import Anthropic

ANALYST_SYSTEM_PROMPT = """\
אתה אנליסט פיננסי מנוסה. תקבל דאטה טכני (מחיר, RSI, EMA, MACD) וטקסט מדוח כספי.
המשימה שלך: לחלץ ולנתח בדיוק את הדברים שאנליסט מקצועי בודק ראשון, לא יותר.

החזר תשובה בפורמט JSON בלבד (בלי טקסט נוסף, בלי ```json), במבנה הזה:
{
  "revenue_yoy_growth": "תיאור קצר של הצמיחה שנה-על-שנה, עם המספרים",
  "margin_trend": "האם השוליים (גולמי/תפעולי) משתפרים או מתכווצים, עם מספרים",
  "guidance": "מה ההנהלה אומרת על הרבעון/שנה הקרובה",
  "cash_flow_and_debt": "מצב תזרים מזומנים והתחייבויות, אם מוזכר בטקסט",
  "technical_summary": "פירוש קצר של המצב הטכני (RSI/EMA/MACD) - האם תומך/מנוגד לתמונה הפנדומנטלית",
  "overall_summary": "שני-שלושה משפטים שמסכמים את התמונה הכוללת, בעברית, בטון מקצועי וזהיר (לא המלצת השקעה)"
}

אם מידע מסוים לא קיים בטקסט שקיבלת, כתוב "לא צוין בדוח" בשדה הרלוונטי - אל תמציא מספרים.
"""


def analyze(technical_snapshot: dict, report_text: str, company_name: str) -> dict:
    """שולח את הדאטה ל-Claude API ומחזיר ניתוח מבני."""
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_content = f"""\
חברה: {company_name}

=== דאטה טכני ===
{json.dumps(technical_snapshot, ensure_ascii=False, indent=2)}

=== טקסט מהדוח הכספי (חלק) ===
{report_text[:8000]}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=ANALYST_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_content}],
    )

    raw_text = response.content[0].text
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        # אם המודל בכל זאת הוסיף טקסט סביב ה-JSON, ננסה לחלץ אותו
        cleaned = raw_text.strip().strip("```json").strip("```")
        return json.loads(cleaned)


if __name__ == "__main__":
    # בדיקה ידנית מהירה
    dummy_technical = {"rsi_14": 55, "ema_20": 100, "ema_50": 95}
    dummy_text = "Revenue grew 15% year over year to $414 million..."
    result = analyze(dummy_technical, dummy_text, "Test Company")
    print(json.dumps(result, indent=2, ensure_ascii=False))
