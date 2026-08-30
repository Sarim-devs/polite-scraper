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

from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def discover_catalogue_pages():
    base_url = "https://books.toscrape.com/catalogue/page-1.html"
    all_book_urls = []
    current_url = base_url
    page_num = 1
    MAX_PAGES = 3

    while current_url and page_num <= MAX_PAGES:
        cache_filename = f"catalogue-page-{page_num}.html"
        was_cached = os.path.exists(os.path.join(CACHE_DIR, cache_filename))

        html = fetch_page(current_url, cache_filename)
        soup = BeautifulSoup(html, "html.parser")

        for link in soup.select("article.product_pod h3 a"):
            book_url = urljoin(current_url, link["href"])
            all_book_urls.append(book_url)

        next_link = soup.select_one("li.next a")
        if next_link and page_num < MAX_PAGES:
            current_url = urljoin(current_url, next_link["href"])
            page_num += 1
            if not was_cached:
                time.sleep(0.5)
        else:
            current_url = None

    unique_urls = list(dict.fromkeys(all_book_urls))
    return page_num, unique_urls

if __name__ == "__main__":
    pages, urls = discover_catalogue_pages()
    print(f"catalogue_pages={pages}")
    print(f"discovered={len(urls)}")
    print(f"unique_urls={len(urls)}")