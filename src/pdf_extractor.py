from __future__ import annotations

"""
הורדת PDF וחילוץ טקסט ממנו.
"""

import re
import subprocess
import tempfile
import requests

HEADERS = {"User-Agent": "Mozilla/5.0"}


def download_pdf(pdf_url: str) -> str:
    """מוריד PDF לקובץ זמני, מחזיר את הנתיב."""
    resp = requests.get(pdf_url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)
    tmp.write(resp.content)
    tmp.close()
    return tmp.name


def extract_text(pdf_path: str, max_pages: int | None = 30) -> str:
    """מחלץ טקסט מה-PDF באמצעות pdftotext (poppler-utils)."""
    cmd = ["pdftotext", "-layout"]
    if max_pages:
        cmd += ["-f", "1", "-l", str(max_pages)]
    cmd += [pdf_path, "-"]

    result = subprocess.run(cmd, capture_output=True, text=True)
    text = result.stdout
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def get_report_text(pdf_url: str, max_pages: int | None = 30) -> str:
    """פונקציית-על: מוריד ומחלץ טקסט בקריאה אחת."""
    path = download_pdf(pdf_url)
    return extract_text(path, max_pages=max_pages)


if __name__ == "__main__":
    import sys

    url = sys.argv[1]
    print(get_report_text(url)[:3000])