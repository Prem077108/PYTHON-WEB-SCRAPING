import re


def canonicalize(value):
    if value is None:
        return ""
    text = str(value).lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def deduplicate_records(records):
    seen = {}
    unique = []
    duplicates = []

    for record in records:
        title = canonicalize(record.get("name_or_title"))
        author = canonicalize(record.get("author"))
        source = canonicalize(record.get("source"))
        key = (source, title, author)
        if key in seen:
            duplicates.append(record)
            continue
        seen[key] = record
        unique.append(record)

    return unique, duplicates
