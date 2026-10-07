# AI Usage

## AI tools used
- GitHub Copilot / Copilot SDK

## What each tool was used for
- Initial project structure and Python module layout
- Suggesting parsing logic for Books to Scrape and Quotes to Scrape
- Reviewing data cleaning and validation logic
- Drafting README and summary documentation

## Representative prompts
- "Design a Python scraper for Books to Scrape and Quotes to Scrape with pagination, cleaning, validation, and deduplication."
- "Help me build a standardized schema that works for both data sources and keep source URLs intact."
- "Write a resilient requests-based scraper with retry handling and page skipping for missing HTML."

## Which parts of the code were AI-assisted
- Initial scraper architecture
- HTML selector strategy
- Standardized record schema
- Validation and deduplication logic
- Documentation structure

## Important changes made after reviewing AI output
- Added explicit validation around URL and rating ranges
- Tightened duplicate detection to use normalized source + title + author rather than raw strings
- Improved error logging and page retry behavior
- Ensured record cleaning remains separate from scraping logic

## Incorrect or incomplete AI-generated suggestions discovered
- Some initial drafts over-reported duplicate matches when only whitespace differences were present; this was corrected by canonicalizing strings.
- Early ideas to rely on a single raw string comparator were replaced with normalized keys and a more explicit validation layer.

## How the final solution was tested and verified
- Ran the full pipeline using `python main.py` to generate the CSV and summary report
- Executed pytest against the cleaning and deduplication tests
- Verified that records were written to `output/final_dataset.csv` and `output/summary_report.json`
