"""
מיפוי טיקרים <-> מזהי חברה במאיה (TASE).

המערכת משתמשת בשני מקורות בכוונה:
- מחיר נוכחי: נקרא ישירות מהעמוד הרשמי של מאיה (src/maya_price.py) -
  מקור ישראלי מקורי, בלי תיווך, בלי המרת מטבע.
- היסטוריה לאינדיקטורים טכניים (RSI/EMA/MACD): Yahoo עם סיומת .TA -
  זה עדיין נתוני מסחר תל אביב בשקלים, לא מסחר אמריקאי. הסיבה
  שמשתמשים ב-Yahoo כאן ולא במאיה: לא נמצא ב-Maya endpoint היסטורי
  שמותר לפי robots.txt (הדאטה ההיסטורי שלהם חוסה תחת /api/ החסום).

איך מוצאים companyId ו-securityId חדשים:
1. חפשו את החברה בגוגל: "<שם חברה> מאיה תאז"
2. בכתובת ה-URL תראו משהו כמו
   maya.tase.co.il/he/companies/2028?securityId=1138494
   2028 = companyId, 1138494 = securityId
"""

COMPANIES = {
    "TSEM": {
        "name": "Tower Semiconductor",
        "name_he": "טאואר סמיקונדקטור",
        "yahoo_symbol": "TSEM.TA",    # להיסטוריה/אינדיקטורים בלבד - ראו הערה למעלה
        "maya_company_id": 2028,
        "maya_security_id": 1138494,  # למחיר הנוכחי המקורי - מהעמוד הרשמי במאיה
    },
    "LUMI": {
        "name": "Bank Leumi",
        "name_he": "בנק לאומי",
        "yahoo_symbol": "LUMI.TA",
        "maya_company_id": 604,       # לאמת/לעדכן בהתאם לחיפוש
        "maya_security_id": None,     # להשלים - לחפש ב-maya.tase.co.il ולמצוא ב-URL
    },
    "TEVA": {
        "name": "Teva Pharmaceutical",
        "name_he": "טבע",
        "yahoo_symbol": "TEVA.TA",
        "maya_company_id": None,
        "maya_security_id": None,
    },
    "DORL": {
        "name": "Doral Renewable Energy",
        "name_he": "דוראל אנרגיה",
        "yahoo_symbol": "DORL.TA",
        "maya_company_id": 1801,
        "maya_security_id": 1166768,
    },
    "NOFR": {
        "name": "Nofar Energy",
        "name_he": "נופר אנרג'י",
        "yahoo_symbol": "NOFR.TA",
        "maya_company_id": 1831,
        "maya_security_id": 1170877,
    },
}


def get_company(ticker: str) -> dict:
    ticker = ticker.upper()
    if ticker not in COMPANIES:
        raise ValueError(
            f"'{ticker}' לא מוגדר ב-config.py. הוסיפו אותו ידנית ל-COMPANIES."
        )
    return COMPANIES[ticker]
