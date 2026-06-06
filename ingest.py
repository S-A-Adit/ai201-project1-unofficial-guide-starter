"""Milestone 3 — Ingestion.

Loads every document in the corpus and saves the RAW text to documents/raw/
in a consistent format, before any cleaning. Two inputs:

  1. URL sources  -> fetched with requests, saved as documents/raw/<id>.html
  2. Manual files -> documents/manual/<id>.txt (e.g. Reddit threads you saved by
                     hand), copied to documents/raw/<id>.txt unchanged

Run:  python ingest.py
"""

import os
import time

import requests

from sources import SOURCES

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "documents", "raw")
MANUAL_DIR = os.path.join(HERE, "documents", "manual")

# A real browser User-Agent — some sites 403 the default python-requests UA.
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch(url):
    """Return decoded page text. Raises on HTTP error (caller logs, continues)."""
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    # Decode the raw bytes ourselves: some pages declare UTF-8 but actually
    # send Windows-1252 smart quotes (or vice-versa), which produces mojibake
    # (the U+FFFD replacement char). Try encodings in order and accept the
    # first that decodes cleanly with no replacement chars; cp1252 is the
    # common culprit and decodes those smart quotes correctly.
    raw = resp.content
    for enc in (resp.encoding, resp.apparent_encoding, "utf-8", "cp1252"):
        if not enc:
            continue
        try:
            text = raw.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
        if "�" not in text:
            return text
    return raw.decode("utf-8", errors="replace")


def main():
    os.makedirs(RAW_DIR, exist_ok=True)
    os.makedirs(MANUAL_DIR, exist_ok=True)

    fetched, manual, failed = 0, 0, 0

    for src in SOURCES:
        sid, url = src["id"], src["url"]

        # Manual sources: copy the hand-saved .txt into raw/ if present.
        if url is None:
            manual_path = os.path.join(MANUAL_DIR, f"{sid}.txt")
            if os.path.exists(manual_path):
                with open(manual_path, "r", encoding="utf-8") as f:
                    text = f.read()
                with open(os.path.join(RAW_DIR, f"{sid}.txt"), "w", encoding="utf-8") as f:
                    f.write(text)
                manual += 1
                print(f"  manual   {sid}: {len(text):,} chars")
            else:
                print(f"  SKIP     {sid}: no documents/manual/{sid}.txt yet "
                      f"(collect this one in your browser)")
            continue

        # URL sources: fetch and save raw HTML.
        try:
            html = fetch(url)
        except Exception as e:  # noqa: BLE001 - log and keep going
            failed += 1
            print(f"  FAILED   {sid}: {e}")
            continue

        with open(os.path.join(RAW_DIR, f"{sid}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        fetched += 1
        print(f"  fetched  {sid}: {len(html):,} chars  <- {url}")
        time.sleep(1)  # be polite between requests

    print(f"\nDone. fetched={fetched}  manual={manual}  failed={failed}")
    print(f"Raw text saved to {RAW_DIR}")


if __name__ == "__main__":
    main()
