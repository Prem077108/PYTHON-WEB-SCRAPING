import re
from typing import Any
from urllib.parse import urljoin, urlparse


def normalize_whitespace(value: Any) -> str:
    if value is None:
        return ""
    cleaned = re.sub(r"\s+", " ", str(value)).strip()
    return cleaned


def normalize_text(value: Any) -> str:
    return normalize_whitespace(value)


def convert_price(value: Any) -> float | None:
    if value is None:
        return None
    text = normalize_text(value)
    if not text:
        return None
    normalized = re.sub(r"[^0-9.\-]", "", text)
    if not normalized or normalized in {"-", ".", "-."}:
        return None
    try:
        number = float(normalized)
        return round(number, 2)
    except ValueError:
        return None


def normalize_rating(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        numeric = float(value)
        return numeric if 0 <= numeric <= 5 else None
    text = normalize_text(value)
    if not text:
        return None
    mapping = {
        "one": 1,
        "two": 2,
        "three": 3,
        "four": 4,
        "five": 5,
    }
    if text.lower() in mapping:
        return float(mapping[text.lower()])
    match = re.search(r"(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    rating = float(match.group(1))
    return rating if 0 <= rating <= 5 else None


def normalize_url(value: Any, base_url: str | None = None) -> str:
    if value is None:
        return ""
    text = normalize_text(value)
    if not text:
        return ""
    if base_url and not text.startswith("http"):
        text = urljoin(base_url, text)
    parsed = urlparse(text)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return text


def normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        tags = [normalize_text(item) for item in value]
    else:
        tags = [normalize_text(item) for item in str(value).split(",")]
    return [tag for tag in tags if tag]


def clean_record(record: dict) -> dict:
    cleaned = dict(record)
    cleaned["source"] = normalize_text(record.get("source"))
    cleaned["source_url"] = normalize_url(record.get("source_url"), base_url=record.get("base_url"))
    cleaned["name_or_title"] = normalize_text(record.get("name_or_title"))
    cleaned["category"] = normalize_text(record.get("category"))
    cleaned["price"] = convert_price(record.get("price"))
    cleaned["rating"] = normalize_rating(record.get("rating"))
    cleaned["author"] = normalize_text(record.get("author"))
    cleaned["tags"] = normalize_tags(record.get("tags"))
    cleaned["description"] = normalize_text(record.get("description"))
    cleaned["scraped_at"] = normalize_text(record.get("scraped_at"))
    if not cleaned["scraped_at"]:
        cleaned["scraped_at"] = ""
    return cleaned
