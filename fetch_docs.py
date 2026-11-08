import time
from pathlib import Path
from urllib.parse import urljoin, urldefrag
import requests
from bs4 import BeautifulSoup

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)
for old in RAW_DIR.glob("*.txt"):  
    old.unlink()

BASE = "https://pydicom.github.io/pynetdicom/stable/"
HEADERS = {"User-Agent": "dicom-rag-learning-project"}
SKIP_WORDS = ["release", "changelog", "genindex", "search", "_modules", "py-modindex"]
MAX_PAGES = 60

def get(url):
    return requests.get(url, headers=HEADERS, timeout=30)

# 1. Collect page links from a page we know works
start = BASE + "user/ae.html"
soup = BeautifulSoup(get(start).text, "html.parser")
urls = {start}
for a in soup.find_all("a", href=True):
    link, _ = urldefrag(urljoin(start, a["href"]))
    if link.startswith(BASE) and link.endswith(".html"):
        if not any(word in link for word in SKIP_WORDS):
            urls.add(link)
urls = sorted(urls)[:MAX_PAGES]
print(f"Found {len(urls)} pages to download")

# 2. Download each page, keep only the main article text
for url in urls:
    resp = get(url)
    if resp.status_code != 200:
        print(f"FAILED {resp.status_code}: {url}")
        continue
    page = BeautifulSoup(resp.text, "html.parser")
    for tag in page(["nav", "script", "style", "footer", "header"]):
        tag.decompose()
    main = page.find("article") or page.find("main") or page.body
    text = main.get_text(separator="\n")
    name = url.replace(BASE, "").replace("/", "__").replace(".html", "")
    (RAW_DIR / f"{name}.txt").write_text(text, encoding="utf-8")
    print(f"OK {name}: {len(text.split())} words")
    time.sleep(0.5)  