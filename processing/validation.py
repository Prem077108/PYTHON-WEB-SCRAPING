from urllib.parse import urlparse


def is_valid_url(value: str) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_record(record: dict):
    issues = []
    if not record.get("source"):
        issues.append("Missing source")
    if not record.get("source_url") or not is_valid_url(record.get("source_url")):
        issues.append("Invalid source_url")
    if not record.get("name_or_title"):
        issues.append("Missing name_or_title")
    if "price" in record and record.get("price") is not None and (not isinstance(record["price"], (int, float)) or record["price"] < 0):
        issues.append("Invalid price")
    if "rating" in record and record.get("rating") is not None and (not isinstance(record["rating"], (int, float)) or not 0 <= float(record["rating"]) <= 5):
        issues.append("Rating out of expected range")
    return not issues, issues
