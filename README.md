# Multi-Source Web Scraping & Data Consolidation

## Project overview
This project collects publicly available book and quote records from Books to Scrape and Quotes to Scrape, normalizes them into a common structure, validates and deduplicates them, and writes a final CSV plus JSON summary report.

## Python version
Python 3.12

## Installation and setup
1. Clone or download the project.
2. Create a virtual environment if desired.
3. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
4. Run the scraper:
   ```bash
   python main.py
   ```

## Dependencies
- requests
- beautifulsoup4
- lxml
- pytest

## How to run the scraper
From the project root:

```bash
python main.py
```

The script writes the following files:
- output/final_dataset.csv
- output/summary_report.json
- logs/scraper.log

## How pagination works
- Books to Scrape: pages are fetched from `https://books.toscrape.com/` and `catalogue/page-{n}.html` until no `next` link is present or the configured page limit is reached.
- Quotes to Scrape: pages are fetched from `https://quotes.toscrape.com/` and `/page/{n}/` until no next-page link exists or the configured page limit is reached.

This keeps the scraper reusable and avoids hard-coding individual links.

## Data model
The final dataset uses a standardized schema:

- source
- source_url
- name_or_title
- category
- price
- rating
- author
- tags
- description
- scraped_at

Books keep a category and price, while quotes are represented by the quote text as `name_or_title` and the author name as `author`.

## Cleaning approach
The cleaning pipeline performs the following tasks:
- trims repeated whitespace
- normalizes text casing and spacing
- converts book prices to floats
- maps rating strings like `Three` to numeric ratings
- removes invalid empty values
- normalizes tags into a list
- validates and normalizes URLs

## Validation approach
Records are checked before inclusion in the final dataset. Validation covers:
- presence of source and source URL
- presence of a title/quote text
- valid URL format
- numeric price if present
- rating within the 0–5 range

Bad records are logged and excluded from the final file.

## Deduplication approach
Duplicate detection is based on a normalized key made from:
- source
- normalized title/quote text
- normalized author name

This handles differences in whitespace, case, and punctuation while still avoiding accidental removal of distinct records.

## Error-handling approach
The scraper uses:
- requests retries with exponential backoff
- per-page and per-record exception handling
- logging for failed requests, missing HTML, and invalid values
- continued processing when individual pages fail

## Output description
The final CSV contains the cleaned, validated records in a single consolidated table. The summary JSON includes:
- total raw records collected
- cleaned count
- validation rejects
- duplicate records removed
- final dataset count
- execution time
- per-source totals

## Assumptions
- The public practice websites remain accessible during execution.
- The assignment only requires a subset of pages, not the entire site.
- Books are collected from the first few pagination pages to keep the run time reasonable.

## Known limitations
- The scraper intentionally limits pagination to a configurable page range to avoid long execution times.
- Quote records use the page URL as the source URL because individual quotes do not have unique page URLs.
- The site may occasionally return rate-limited or partially broken pages; the retry and skip logic handles these cases gracefully.

## AI usage summary
This project was developed with GitHub Copilot and reviewed for correctness. The AI assistant was used for initial scraper structure, selector validation, cleaning logic, and documentation drafting. Final code was reviewed and verified manually and with pytest before being kept.
