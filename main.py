import csv
import json
import logging
import time
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import deduplicate_records
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"

STANDARD_FIELDS = [
    "source",
    "source_url",
    "name_or_title",
    "category",
    "price",
    "rating",
    "author",
    "tags",
    "description",
    "scraped_at",
]


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(exist_ok=True)
    log_path = LOG_DIR / "scraper.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_path, mode="w", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def write_csv(records, path: Path):
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=STANDARD_FIELDS)
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, "") for field in STANDARD_FIELDS}
            if isinstance(row.get("tags"), list):
                row["tags"] = "; ".join(row["tags"])
            writer.writerow(row)


def summarize_records(raw_records, cleaned_records, invalid_records, deduped_records, duplicate_records, start_time):
    by_source = {}
    for record in raw_records:
        source = record.get("source", "Unknown")
        by_source.setdefault(source, {"records_collected": 0, "records_after_cleaning": 0, "rejected": 0, "duplicates": 0})
        by_source[source]["records_collected"] += 1

    for record in cleaned_records:
        source = record.get("source", "Unknown")
        by_source.setdefault(source, {"records_collected": 0, "records_after_cleaning": 0, "rejected": 0, "duplicates": 0})
        by_source[source]["records_after_cleaning"] += 1

    for item in invalid_records:
        source = item["record"].get("source", "Unknown")
        by_source.setdefault(source, {"records_collected": 0, "records_after_cleaning": 0, "rejected": 0, "duplicates": 0})
        by_source[source]["rejected"] += 1

    for item in duplicate_records:
        source = item.get("source", "Unknown")
        by_source.setdefault(source, {"records_collected": 0, "records_after_cleaning": 0, "rejected": 0, "duplicates": 0})
        by_source[source]["duplicates"] += 1

    summary = {
        "total_records_collected": len(raw_records),
        "total_records_after_cleaning": len(cleaned_records),
        "records_rejected_during_validation": len(invalid_records),
        "duplicate_records_detected": len(duplicate_records),
        "final_record_count": len(deduped_records),
        "execution_time_seconds": round(time.time() - start_time, 2),
        "sources": by_source,
    }
    return summary


def main():
    start_time = time.time()
    logger = configure_logging()
    logger.info("Starting scraper pipeline")
    OUTPUT_DIR.mkdir(exist_ok=True)

    books_scraper = BooksScraper(max_pages=5)
    quotes_scraper = QuotesScraper(max_pages=5)

    books_records = books_scraper.scrape_all()
    quotes_records = quotes_scraper.scrape_all()
    raw_records = books_records + quotes_records
    logger.info("Collected %s raw records", len(raw_records))

    cleaned_records = [clean_record(record) for record in raw_records]
    valid_records = []
    invalid_records = []
    for record in cleaned_records:
        is_valid, issues = validate_record(record)
        if is_valid:
            valid_records.append(record)
        else:
            invalid_records.append({"record": record, "issues": issues})

    logger.info("Valid records: %s | rejected: %s", len(valid_records), len(invalid_records))
    deduped_records, duplicate_records = deduplicate_records(valid_records)
    logger.info("Final deduplicated records: %s | duplicates removed: %s", len(deduped_records), len(duplicate_records))

    write_csv(deduped_records, OUTPUT_DIR / "final_dataset.csv")
    summary = summarize_records(raw_records, cleaned_records, invalid_records, deduped_records, duplicate_records, start_time)
    with (OUTPUT_DIR / "summary_report.json").open("w", encoding="utf-8") as fp:
        json.dump(summary, fp, indent=2)

    logger.info("Scraper pipeline completed successfully")
    print(f"Created {len(deduped_records)} final records in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
