"""
הרצה חד-פעמית: פותח דפדפן גלוי כדי שתתחבר בעצמך לחשבון האישי שלך
באתר הבורסה. לאחר ההתחברות, ה-session נשמר לקובץ מקומי, וסקריפטים
אחרים (tase_historical.py) ישתמשו בו כדי לשלוף דאטה היסטורי בלי
שתצטרך להתחבר כל פעם מחדש.

הערה: הסקריפט הזה לא ראה ולא שומר את הסיסמה שלך בשום שלב - אתה
מקליד אותה ידנית בחלון הדפדפן שנפתח, בדיוק כמו בכל גלישה רגילה.

שימוש:
    python login_setup.py
"""

from playwright.sync_api import sync_playwright

AUTH_STATE_FILE = "auth_state.json"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # חלון גלוי
        context = browser.new_context()
        page = context.new_page()

        page.goto("https://market.tase.co.il/he", timeout=30000)

        print("\n" + "=" * 60)
        print("נפתח חלון דפדפן. התחברו לחשבון האישי שלכם בבורסה.")
        print("לאחר שתתחברו בהצלחה ותראו את עצמכם מחוברים,")
        print("חזרו לכאן וגעו Enter בטרמינל כדי לשמור את ה-session.")
        print("=" * 60 + "\n")
        input("לחצו Enter לאחר ההתחברות... ")

        context.storage_state(path=AUTH_STATE_FILE)
        print(f"\nה-session נשמר בקובץ: {AUTH_STATE_FILE}")
        print("אל תשתפו את הקובץ הזה עם אף אחד - הוא מכיל את ה-session המחובר שלכם.")

        browser.close()


if __name__ == "__main__":
    main()
