from processing.cleaning import convert_price, normalize_rating, normalize_whitespace
from processing.deduplication import deduplicate_records


def test_normalize_whitespace_removes_extra_spaces():
    assert normalize_whitespace("  Example   Title  ") == "Example Title"


def test_convert_price_handles_money_symbols_and_commas():
    assert convert_price("£51.77") == 51.77
    assert convert_price("$1,200.50") == 1200.5


def test_normalize_rating_converts_text_stars():
    assert normalize_rating("Three") == 3.0
    assert normalize_rating("5") == 5.0


def test_deduplicate_records_detects_equivalent_rows():
    records = [
        {"source": "Books to Scrape", "name_or_title": "Example Book", "author": "Author A"},
        {"source": "Books to Scrape", "name_or_title": " EXAMPLE BOOK ", "author": "author a"},
        {"source": "Quotes to Scrape", "name_or_title": "A different quote", "author": "Author B"},
    ]
    unique, duplicates = deduplicate_records(records)
    assert len(unique) == 2
    assert len(duplicates) == 1
