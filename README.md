## Target classification

**Target:** books.toscrape.com
**Why:** a public sandbox site explicitly built for practicing web scraping (per toscrape.com's own description).
**Scope:** the first 3 catalogue pages only, following the site's own "next" links.
**Data collected:** book title, price, availability, rating, description, and product URL — all publicly visible on the page.
**robots.txt:** requested at /robots.txt — returned 404 Not Found (no robots file exists). A missing file is not the same as permission, but the site's own stated purpose as a scraping sandbox is.

I will not reuse this code on another site without checking its rules and terms first.

## How to run

1. Clone the repo
2. Create a virtual environment: `python -m venv venv`
3. Activate it: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `python src/main.py`
6. Output appears in `output/books.json`, `output/errors.json`, `output/run-report.json`

## Record schema

Each validated book record contains:

| Field | Type | Notes |
|-------|------|-------|
| title | string | |
| product_url | string | canonical/absolute URL |
| price_gbp | float | parsed from price_text |
| price_text | string | original text, e.g. "£51.77" |
| availability_text | string | |
| rating_text | string or null | e.g. "Three" |
| description | string or null | null if page has none |
| source_page | string | which catalogue page it came from |
| fetched_at | string | ISO timestamp |

## Politeness rules

- Identifies itself with a real User-Agent naming this project
- 10-second timeout on every request
- 0.5 second delay between real requests (never when reading from cache)
- Checks status code before trusting a response
- Caches every page after first fetch — re-running during development never re-hits the site
- Retries once on timeout/5xx server errors; never retries 404 or 403

## Failure handling

One deliberately broken book URL is included in every run to prove the pipeline survives a bad page without crashing. See `output/run-report.json` — `failed_pages` will always show at least 1 because of this intentional test.

## Sample run report

See [`output/run-report.json`](./output/run-report.json) for a real run's output.