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

    headers = {"User-Agent": USER_AGENT}
    attempts = 0
    max_attempts = 2

    while attempts < max_attempts:
        attempts += 1
        print(f"FETCH: {url} (attempt {attempts})")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.encoding = "utf-8"
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if attempts < max_attempts:
                time.sleep(1)
                continue
            raise Exception(f"Failed to fetch {url} after {max_attempts} attempts: {e}")

        print(f"Status: {response.status_code}, Size: {len(response.text)} bytes")

        if response.status_code == 200:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            return response.text
        elif response.status_code == 404:
            raise Exception(f"Page not found (404): {url}")
        elif response.status_code == 403:
            raise Exception(f"Access forbidden (403): {url}")
        elif response.status_code >= 500 and attempts < max_attempts:
            print(f"Server error {response.status_code}, retrying...")
            time.sleep(1)
            continue
        else:
            raise Exception(f"Failed to fetch {url}: status {response.status_code}")

    raise Exception(f"Failed to fetch {url} after {max_attempts} attempts")
 
    
from datetime import datetime, timezone

def extract_book(book_url, source_page):
    cache_filename = "book-" + book_url.rstrip("/").split("/")[-2] + ".html"
    was_cached = os.path.exists(os.path.join(CACHE_DIR, cache_filename))

    html = fetch_page(book_url, cache_filename)
    soup = BeautifulSoup(html, "html.parser")

    title = soup.select_one("div.product_main h1").get_text(strip=True)
    price_text = soup.select_one("p.price_color").get_text(strip=True)
    availability_text = soup.select_one("p.availability").get_text(strip=True)

    rating_tag = soup.select_one("p.star-rating")
    rating_text = rating_tag["class"][1] if rating_tag else None

    desc_tag = soup.select_one("#product_description ~ p")
    description = desc_tag.get_text(strip=True) if desc_tag else None

    if not was_cached:
        time.sleep(0.5)

    return {
        "title": title,
        "product_url": book_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }
    
from pydantic import BaseModel, ValidationError
import re
import json

class Book(BaseModel):
    title: str
    product_url: str
    price_gbp: float
    price_text: str
    availability_text: str
    rating_text: str | None
    description: str | None
    source_page: str
    fetched_at: str

def clean_price(price_text):
    match = re.search(r"[\d.]+", price_text)
    if not match:
        raise ValueError(f"Could not parse price from: {price_text}")
    return float(match.group())

def normalize_and_validate(raw_book):
    price_gbp = clean_price(raw_book["price_text"])
    record = {**raw_book, "price_gbp": price_gbp}
    validated = Book(**record)
    return validated.model_dump()

    
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
    start_time = datetime.now(timezone.utc)

    pages, urls = discover_catalogue_pages()
    print(f"catalogue_pages={pages}")
    print(f"unique_urls={len(urls)}")

    # Deliberately broken URL to prove the run survives one bad page
    urls.append("https://books.toscrape.com/catalogue/this-book-does-not-exist_9999/index.html")

    valid_books = []
    errors = []
    failed_pages = []
    cache_hits = 0
    pages_fetched = 0

    for i, url in enumerate(urls):
        source_page = f"https://books.toscrape.com/catalogue/page-{(i // 20) + 1}.html"
        try:
            raw_book = extract_book(url, source_page)
            clean_book = normalize_and_validate(raw_book)
            valid_books.append(clean_book)
        except (ValidationError, ValueError) as e:
            errors.append({"url": url, "reason": str(e)})
        except Exception as e:
            print(f"FAILED PAGE: {url} - {e}")
            failed_pages.append({"url": url, "reason": str(e)})

    os.makedirs("output", exist_ok=True)
    with open("output/books.json", "w", encoding="utf-8") as f:
        json.dump(valid_books, f, indent=2, ensure_ascii=False)

    with open("output/errors.json", "w", encoding="utf-8") as f:
        json.dump(errors, f, indent=2, ensure_ascii=False)

    end_time = datetime.now(timezone.utc)
    report = {
        "start_time": start_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
        "catalogue_pages": pages,
        "valid_records": len(valid_books),
        "invalid_records": len(errors),
        "failed_pages": len(failed_pages),
        "failed_page_details": failed_pages
    }
    with open("output/run-report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"valid_records={len(valid_books)}")
    print(f"invalid_records={len(errors)}")
    print(f"failed_pages={len(failed_pages)}")
    

   