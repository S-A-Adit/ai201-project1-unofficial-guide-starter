"""Milestone 3 — Cleaning.

Turns the raw HTML in documents/raw/ into clean, substantive plain text in
documents/clean/. Removes scripts, styles, nav menus, headers/footers, cookie
banners, ads, share/social widgets, and other boilerplate; keeps the article /
thread body. Raw .txt files (manual Reddit saves) are passed through with only
whitespace normalization.

Run:  python clean.py            (cleans everything, prints a summary)
      python clean.py --show     (also prints one full cleaned doc to inspect)
"""

import html
import os
import re
import sys

from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(HERE, "documents", "raw")
CLEAN_DIR = os.path.join(HERE, "documents", "clean")

# Whole tags that never contain substantive content.
STRIP_TAGS = [
    "script", "style", "nav", "footer", "header", "aside", "form",
    "button", "svg", "noscript", "iframe", "figure", "img",
]

# class/id substrings that mark boilerplate (cookie bars, ads, sharing, etc.).
BOILERPLATE = re.compile(
    r"cookie|consent|banner|advert|sponsor|share|social|related|recommend|"
    r"newsletter|subscribe|sidebar|breadcrumb|menu|navbar|nav-|footer|header|"
    r"comment-count|popup|modal|promo|cta|skip-link",
    re.IGNORECASE,
)


def clean_html(raw_html):
    soup = BeautifulSoup(raw_html, "html.parser")

    # 1. Drop non-content tags entirely.
    for tag in soup(STRIP_TAGS):
        tag.decompose()

    # 2. Drop elements whose class/id looks like boilerplate — but ONLY small
    #    ones. Layout wrappers reuse words like "sidebar" in their class
    #    (e.g. <div class="row-primary sidebar-right"> wrapping the whole
    #    article), so removing every match would delete real content. We read
    #    attributes in one pass first (decomposing a parent detaches children,
    #    making their attrs unreadable), then remove only widgets that don't
    #    hold substantial text.
    to_remove = []
    for el in soup.find_all(True):
        blob = " ".join(el.get("class") or []) + " " + (el.get("id") or "")
        if BOILERPLATE.search(blob):
            to_remove.append(el)
    for el in to_remove:
        if el.decomposed:
            continue
        if len(el.get_text(strip=True)) > 200 and len(el.find_all("p")) >= 2:
            continue  # this is a content wrapper, not a widget — keep it
        el.decompose()

    # 3. Pull the real content blocks. Articles and forum posts both put their
    #    substance in <p>/<li>/heading/blockquote tags; collecting those is far
    #    more reliable than trusting a single <article>/<main> wrapper (some
    #    wrappers hold only the headline). Falls back to all body text.
    container = soup.body or soup
    blocks = container.find_all(["p", "li", "h1", "h2", "h3", "h4", "blockquote"])
    if blocks:
        text = "\n".join(b.get_text(" ", strip=True) for b in blocks)
    else:
        text = container.get_text(separator="\n")

    return normalize(text)


# Whole lines that are leftover UI/boilerplate after block extraction.
JUNK_LINE = re.compile(
    r"^(related posts?|join the conversation|powered by|read more|"
    r"share this|share on|advertisement|trending|most read|you may also like|"
    r"sign up|log ?in|subscribe|follow us|comments?|\d+ coins?|"
    r"\d+ comments?|leave a (reply|comment))\b",
    re.IGNORECASE,
)


def normalize(text):
    """Unescape entities, drop nav-like fragments and junk lines, collapse whitespace."""
    text = html.unescape(text)
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if len(line) < 3:            # stray bullets / single chars
            continue
        if not re.search(r"[a-zA-Z]", line):  # pure punctuation / numbers-only nav
            continue
        if JUNK_LINE.match(line):    # leftover UI chrome
            continue
        lines.append(line)
    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)   # collapse blank-line runs
    text = re.sub(r"[ \t]{2,}", " ", text)   # collapse runs of spaces/tabs
    return text.strip()


def main():
    os.makedirs(CLEAN_DIR, exist_ok=True)
    show = "--show" in sys.argv

    if not os.path.isdir(RAW_DIR):
        print(f"No raw documents at {RAW_DIR}. Run ingest.py first.")
        return

    first_clean_path = None
    count = 0
    for fname in sorted(os.listdir(RAW_DIR)):
        path = os.path.join(RAW_DIR, fname)
        sid, ext = os.path.splitext(fname)
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()

        cleaned = clean_html(raw) if ext == ".html" else normalize(raw)

        out_path = os.path.join(CLEAN_DIR, f"{sid}.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(cleaned)
        count += 1
        first_clean_path = first_clean_path or out_path
        warn = "  <-- THIN, likely JS-rendered; collect manually" if len(cleaned) < 300 else ""
        print(f"  cleaned {sid}: {len(raw):,} -> {len(cleaned):,} chars{warn}")

    print(f"\nCleaned {count} documents -> {CLEAN_DIR}")

    # Print one document so we can read it and confirm cleaning worked.
    if show and first_clean_path:
        print("\n" + "=" * 70)
        print(f"INSPECT: {os.path.basename(first_clean_path)}")
        print("=" * 70)
        with open(first_clean_path, "r", encoding="utf-8") as f:
            print(f.read()[:4000])


if __name__ == "__main__":
    main()
