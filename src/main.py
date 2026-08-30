import os
import requests

USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Sarim-devs/polite-scraper)"
CACHE_DIR = "cache"

def fetch_page(url, cache_filename):
    os.makedirs(CACHE_DIR, exist_ok=True)
    cache_path = os.path.join(CACHE_DIR, cache_filename)

    if os.path.exists(cache_path):
        print(f"CACHE HIT: {cache_filename}")
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    print(f"FETCH: {url}")
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(url, headers=headers, timeout=10)
    print(f"Status: {response.status_code}, Size: {len(response.text)} bytes")

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(response.text)

    return response.text

if __name__ == "__main__":
    html = fetch_page("https://books.toscrape.com/catalogue/page-1.html", "catalogue-page-1.html")
    print(f"Got {len(html)} characters of HTML")