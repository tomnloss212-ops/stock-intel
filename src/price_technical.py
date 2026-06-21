from __future__ import annotations

"""
שליפת מחיר + היסטוריה מ-Yahoo Finance (unofficial endpoint) וחישוב אינדיקטורים טכניים.

הערה: זה לא API רשמי/מתועד של Yahoo. עובד מצוין לשימוש אישי בקנה מידה קטן,
אבל אין הסכם רמת שירות - אם Yahoo ישנו משהו, ייתכן שיידרש תיקון.
"""

import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_price_history(yahoo_symbol: str, range_: str = "6mo", interval: str = "1d") -> dict:
    """מחזיר דאטה גולמי: תאריכים, מחירי סגירה, נפחים."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{yahoo_symbol}"
    params = {"range": range_, "interval": interval}
    resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    result = data["chart"]["result"][0]
    meta = result["meta"]
    timestamps = result["timestamp"]
    quote = result["indicators"]["quote"][0]

    closes = quote["close"]
    volumes = quote["volume"]

    # לעיתים יש None בערכים האחרונים (יום מסחר לא שלם) - מסננים
    clean = [(t, c, v) for t, c, v in zip(timestamps, closes, volumes) if c is not None]

    currency = meta.get("currency")
    # מניות ת"א מוצגות ב-Yahoo באגורות (ILA) - מומרים לשקלים שלמים לנוחות קריאה
    divisor = 100 if currency == "ILA" else 1
    display_currency = "ILS" if currency == "ILA" else currency

    return {
        "symbol": meta.get("symbol"),
        "currency": display_currency,
        "exchange": meta.get("fullExchangeName"),
        "current_price": meta.get("regularMarketPrice") / divisor if meta.get("regularMarketPrice") else None,
        "fifty_two_week_high": meta.get("fiftyTwoWeekHigh") / divisor if meta.get("fiftyTwoWeekHigh") else None,
        "fifty_two_week_low": meta.get("fiftyTwoWeekLow") / divisor if meta.get("fiftyTwoWeekLow") else None,
        "timestamps": [c[0] for c in clean],
        "closes": [c[1] / divisor for c in clean],
        "volumes": [c[2] for c in clean],
    }


def calc_ema(values: list, period: int) -> list:
    """ממוצע נע מעריכי (EMA)."""
    if len(values) < period:
        return []
    k = 2 / (period + 1)
    ema = [sum(values[:period]) / period]  # SMA כנקודת התחלה
    for price in values[period:]:
        ema.append(price * k + ema[-1] * (1 - k))
    return ema


def calc_rsi(values: list, period: int = 14) -> float | None:
    """RSI - Relative Strength Index, מחזיר את הערך האחרון."""
    if len(values) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        change = values[i] - values[i - 1]
        gains.append(max(change, 0))
        losses.append(max(-change, 0))

    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 2)


def calc_macd(values: list, fast: int = 12, slow: int = 26, signal: int = 9) -> dict | None:
    """MACD - מחזיר את הקו, קו האיתות, וההיסטוגרם (הערכים האחרונים)."""
    if len(values) < slow + signal:
        return None
    ema_fast = calc_ema(values, fast)
    ema_slow = calc_ema(values, slow)
    # מאזנים את האורכים (ema_fast מתחיל מוקדם יותר)
    offset = len(ema_fast) - len(ema_slow)
    macd_line = [f - s for f, s in zip(ema_fast[offset:], ema_slow)]
    signal_line = calc_ema(macd_line, signal)
    if not signal_line:
        return None
    histogram = macd_line[-1] - signal_line[-1]
    return {
        "macd": round(macd_line[-1], 4),
        "signal": round(signal_line[-1], 4),
        "histogram": round(histogram, 4),
    }


def get_technical_snapshot(yahoo_symbol: str) -> dict:
    """פונקציית-על: שולפת היסטוריה ומחזירה תמונת מצב טכנית מלאה."""
    history = fetch_price_history(yahoo_symbol)
    closes = history["closes"]

    ema_20 = calc_ema(closes, 20)
    ema_50 = calc_ema(closes, 50)

    return {
        "symbol": history["symbol"],
        "currency": history["currency"],
        "exchange": history["exchange"],
        "current_price": history["current_price"],
        "52w_high": history["fifty_two_week_high"],
        "52w_low": history["fifty_two_week_low"],
        "rsi_14": calc_rsi(closes, 14),
        "ema_20": round(ema_20[-1], 2) if ema_20 else None,
        "ema_50": round(ema_50[-1], 2) if ema_50 else None,
        "macd": calc_macd(closes),
        "data_points_used": len(closes),
        "recent_closes": [round(c, 2) for c in closes[-30:]],
    }


if __name__ == "__main__":
    import sys
    import json

    symbol = sys.argv[1] if len(sys.argv) > 1 else "TSEM"
    snapshot = get_technical_snapshot(symbol)
    print(json.dumps(snapshot, indent=2, ensure_ascii=False))
