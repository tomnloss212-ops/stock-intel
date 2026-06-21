# Stock Intel — מנוע מידע למניות

מערכת אישית לאיסוף וניתוח מידע על מניות: מחיר + טכני, דוחות כספיים, וניתוח AI בסטייל אנליסט.

## מבנה הפרויקט

```
stock-intel/
├── README.md
├── requirements.txt
├── .env.example          # העתק ל-.env והכנס שם מפתח Anthropic API
├── main.py                # הרצה ראשית - מקבל טיקר ומריץ את כל הצנרת
└── src/
    ├── config.py          # מיפוי טיקרים <-> מזהי חברה במאיה
    ├── price_technical.py # מחיר + אינדיקטורים טכניים (Yahoo unofficial)
    ├── reports_scraper.py # שליפת רשימת דוחות + PDF אחרון ממאיה (Playwright)
    ├── pdf_extractor.py   # חילוץ טקסט מה-PDF שהורד
    ├── ai_analyst.py       # שליחה ל-Claude API עם פרומפט בסטייל אנליסט
    └── news_rss.py         # שלד לשליפת חדשות RSS (Globes/Calcalist) - להרחבה
```

## התקנה

```bash
pip install -r requirements.txt --break-system-packages
playwright install chromium
cp .env.example .env
# ערוך את .env והכנס ANTHROPIC_API_KEY=sk-ant-...
```

## הרצה

```bash
python main.py TSEM        # טאואר סמיקונדקטור
python main.py LUMI.TA     # בנק לאומי (רק טכני - אין דוחות ב-NASDAQ format)
```

## מצב נוכחי (POC)

- ✅ מחיר נוכחי + 52 שבועות (Maya, מקור רשמי ישראלי - `maya_price.py`)
- ✅ שליפת הדוח הכספי האחרון ממאיה (Playwright + חילוץ PDF)
- ✅ ניתוח AI בסטייל אנליסט (צמיחה, שוליים, guidance, תזרים, חוב)
- ⏳ היסטוריה ל-RSI/EMA/MACD מ-Yahoo (`price_technical.py`) — **בתהליך הסרה**, ראו "היסטוריה מקור ישראלי" למטה
- ⏳ חדשות RSS — שלד בסיסי, לא מחובר עדיין לצנרת הראשית
- ⏳ מניות ת"א טהורות (לא dual-listed) — צריך להרחיב את `config.py` עם מזהי החברה במאיה

## היסטוריה ממקור ישראלי בלבד (במקום Yahoo)

נמצא שדאטה היסטורי רשמי קיים באתר הבורסה (`market.tase.co.il/.../historical_data`),
אבל דורש **משתמש מחובר** (חשבון אישי חינמי, נפרד מ-TASE Data Hub המוסדי בתשלום).

**שלבים:**

1. הירשמו לחשבון אישי ב-`account.tase.co.il` / `tase.co.il` בעצמכם.
2. הריצו פעם אחת: `python src/login_setup.py` — ייפתח חלון דפדפן, תתחברו
   בעצמכם (הקוד לא רואה את הסיסמה שלכם), ותלחצו Enter בטרמינל.
   זה ישמור session לקובץ `auth_state.json`.
3. הריצו `python src/tase_historical.py 1138494` (במקום 1138494 שימו
   securityId של המניה שלכם, מהכתובת ב-maya.tase.co.il) במצב DEBUG -
   זה יראה לכם בדפדפן גלוי אם הדאטה ההיסטורי באמת נטען, וידפיס
   את הקריאות ל-API שנתפסו.

**הערה כנה:** לא הצלחתי לבדוק את `tase_historical.py` במצב מחובר בפועל,
כי זה דורש חשבון אישי שאין לי. כשתריצו את זה אצלכם עם DEBUG=True,
תעבירו לי את הפלט (אילו קריאות API נראו, ואיזה מבנה JSON חזר) ונדייק
יחד את הקוד כדי שיחלץ את השדות הנכונים (תאריך, פתיחה/גבוה/נמוך/סגירה).

לאחר שזה יעבוד, נחבר אותו ל-`price_technical.py` במקום Yahoo (או נמיר
את הפונקציות שם להשתמש בדאטה הזה).

## הערות חשובות

1. **Yahoo unofficial endpoint**: לא API רשמי/מתועד. עובד מצוין לכמות שימוש אישית קטנה, אבל יכול להישבר אם Yahoo ישנו משהו — אין הסכם רמת שירות.
2. **Maya scraper**: תלוי במבנה ה-HTML הנוכחי של האתר. אם מאיה משנים עיצוב, ה-scraper עלול להזדקק לתיקון.
3. **robots.txt**: ה-scraper גולש בעמודים הציבוריים בלבד (כמו דפדפן רגיל), ולא פונה ל-`/api/` הפנימי של מאיה שמסומן Disallow.
4. **קצב בקשות**: אל תרוץ את זה בלופים מהירים על הרבה מניות בבת אחת — תוסיף השהיה בין בקשות (כבר יש בקוד `time.sleep`).
