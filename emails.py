import os
import re
import csv
import requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
SITES_FILE = os.path.join(HERE, "sites.txt")
OUTPUT_FILE = os.path.join(HERE, "emails_found.csv")

# Extra pages checked on each site's main domain (the URL in sites.txt is always checked too)
PATHS = ["", "/contacto", "/contact"]

WORKERS = 200        # parallel requests
TIMEOUT = (2, 3)     # (connect, read) seconds per request
MAX_BYTES = 300_000  # only read the first 300 KB of each page

SESSION = requests.Session()
adapter = requests.adapters.HTTPAdapter(pool_connections=200, pool_maxsize=200)
SESSION.mount("https://", adapter)
SESSION.mount("http://", adapter)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
IGNORE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".css", ".js")
HEADERS = {"User-Agent": "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 Chrome/120 Mobile Safari/537.36"}


def load_sites():
    if not os.path.exists(SITES_FILE):
        raise SystemExit(f"Cannot find {SITES_FILE}. Put sites.txt in the same folder as emails.py.")
    sites = []
    with open(SITES_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if not line.startswith(("http://", "https://")):
                line = "https://" + line
            if line not in sites:
                sites.append(line)
    return sites


def build_urls(site):
    parsed = urlparse(site)
    base = f"{parsed.scheme}://{parsed.netloc}"
    urls = [site]
    for p in PATHS:
        u = base + p
        if u not in urls and u.rstrip("/") != site.rstrip("/"):
            urls.append(u)
    return urls


def fetch(url):
    try:
        r = SESSION.get(url, headers=HEADERS, timeout=TIMEOUT, stream=True)
        if r.status_code == 200:
            text = r.raw.read(MAX_BYTES, decode_content=True).decode("utf-8", "ignore")
            r.close()
            return {e.lower() for e in EMAIL_RE.findall(text)
                    if not e.lower().endswith(IGNORE_EXT)}
    except Exception:
        pass
    return set()


def main():
    sites = load_sites()
    urls = [u for s in sites for u in build_urls(s)]
    urls = list(dict.fromkeys(urls))
    total = len(urls)
    print(f"{len(sites)} sites loaded from sites.txt, {total} pages to check")

    all_emails = set()
    done = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [pool.submit(fetch, u) for u in urls]
        for fut in as_completed(futures):
            all_emails |= fut.result()
            done += 1
            print(f"\r{done}/{total} pages checked, {len(all_emails)} emails found", end="", flush=True)

    all_emails = sorted(all_emails)
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["email"])
        for email in all_emails:
            writer.writerow([email])

    print(f"\n\n{len(all_emails)} unique emails saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
