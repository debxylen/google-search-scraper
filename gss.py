__all__ = ["get_nid", "get_results", "get_ai"]

import re
import time
import requests as requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, quote

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

def get_nid(chrome_version=None, wait_s=3):
    import undetected_chromedriver as uc

    _original_del = uc.Chrome.__del__
    def _shut_del(self):
        try: _original_del(self)
        except Exception: pass
    uc.Chrome.__del__ = _shut_del

    driver = uc.Chrome(version_main=chrome_version, headless=False)

    try:
        driver.get("https://www.google.com/search?q=test")
        time.sleep(wait_s)

        cookie = driver.get_cookie("NID")
        return cookie["value"] if cookie else None

    finally:
        driver.quit()

def extract_results(children):
    results = []

    for root in children:
        link = root.select_one("a:has(h3)")

        if not link:
            results.extend(extract_videos(root))
            continue

        title_el = link.select_one("h3")
        title = title_el.get_text(strip=True) if title_el else None

        url = link.get("href")
        snippet = "\n".join(line for line in root.get_text("\n").split("\n") if line.strip() != "Web results")

        results.append({"type": "normal", "title": title, "url": url, "snippet": snippet})

    return results

def extract_videos(root):
    links = root.select('a[href*="youtube.com/watch"], a[href*="youtu.be/"]')

    seen = set()
    videos = []

    for link in links:
        href = link.get("href")
        if not href: continue

        parsed = urlparse(href)
        video_id = parse_qs(parsed.query).get("v", [None])[0]

        if not video_id: continue
        if video_id in seen: continue
        seen.add(video_id)

        heading = link.select_one('[role="heading"]')
        title = (heading.get_text(strip=True) if heading else link.get_text(strip=True))

        container = link.find_parent(attrs={"data-vid": True})
        overview = None

        if container:
            for el in container.select('[aria-label]'):
                label = (el.get('aria-label') or '').strip()
                text = el.get_text(strip=True)
                if label and text and label == text: overview = label; break

        video = {"type": "video", "title": title, "url": f"https://www.youtube.com/watch?v={video_id}"}
        if overview: video["overview"] = overview

        videos.append(video)

    return videos

def get_results(query, nid):
    r = requests.get(f"https://www.google.com/search?q={quote(query)}", headers={"User-Agent": UA}, cookies={"NID": nid})

    soup = BeautifulSoup(r.text, "html.parser")

    def is_empty(el):
        if el.name != "div": return False
        if el.get_text(strip=True): return False
        return all(is_empty(child) for child in el.find_all(recursive=False))

    children = [child for child in soup.select_one("[data-async-context]").find_all(recursive=False) if not is_empty(child)]

    results = extract_results(children)

    m = re.search(r"/async/folsrch\?[^']+", r.text)
    if m: results.insert(0, {"type": "ai", "title": "AI Overview", "url": "https://www.google.com" + m.group(0).encode().decode("unicode_escape")})

    return results

def get_ai(url, nid, timeout = None):
    r = requests.get(url, headers={"User-Agent": UA}, cookies={"NID": nid}, timeout=timeout, stream=True)
    html = b"".join(list(r.iter_content(8192))).decode("utf-8", errors="ignore")

    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one('section')

    ft = el.select_one('[data-target-container-id="footer-placeholder"]')
    if ft: ft.decompose()

    text = "\n".join(el.stripped_strings)

    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r' {2,}', ' ', text)

    return text
