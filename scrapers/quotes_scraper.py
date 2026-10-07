import logging
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class QuotesScraper:
    BASE_URL = "https://quotes.toscrape.com"

    def __init__(self, max_pages: int = 5, timeout: int = 20):
        self.max_pages = max_pages
        self.timeout = timeout
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods={"GET"},
        )
        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update({"User-Agent": "Mozilla/5.0"})

    def _fetch(self, url: str):
        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            self.logger.warning("Failed to fetch %s: %s", url, exc)
            return None

    def _absolute_url(self, path: str | None) -> str:
        if not path:
            return ""
        if path.startswith("http"):
            return path
        return f"{self.BASE_URL.rstrip('/')}/{path.lstrip('/')}"

    def _fetch_author_details(self, author_url: str):
        if not author_url:
            return {"author": "", "description": ""}
        response = self._fetch(author_url)
        if response is None:
            return {"author": "", "description": ""}
        soup = BeautifulSoup(response.text, "html.parser")
        details = soup.select_one("div.author-details")
        if details is None:
            return {"author": "", "description": ""}
        author_name = details.select_one("h3")
        description_lines = []
        paragraphs = details.select("p")
        for paragraph in paragraphs:
            text = paragraph.get_text(" ", strip=True)
            if text:
                description_lines.append(text)
        author = author_name.get_text(strip=True) if author_name else ""
        return {"author": author, "description": " ".join(description_lines)}

    def scrape_all(self):
        records = []
        for page_number in range(1, self.max_pages + 1):
            page_url = self.BASE_URL if page_number == 1 else f"{self.BASE_URL}/page/{page_number}/"
            response = self._fetch(page_url)
            if response is None:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            quotes = soup.select("div.quote")
            if not quotes:
                break

            for quote in quotes:
                quote_text = quote.select_one("span.text")
                author_element = quote.select_one("small.author")
                tag_elements = quote.select("div.tags a.tag")
                author_name = author_element.get_text(strip=True) if author_element else ""
                tag_list = [tag.get_text(strip=True) for tag in tag_elements if tag.get_text(strip=True)]
                author_link = quote.select_one("span > a[href*='/author/']")
                author_url = self._absolute_url(author_link.get("href")) if author_link else ""
                author_details = self._fetch_author_details(author_url)
                description = author_details.get("description", "")
                if not author_name and author_details.get("author"):
                    author_name = author_details["author"]

                record = {
                    "source": "Quotes to Scrape",
                    "source_url": page_url,
                    "base_url": self.BASE_URL,
                    "name_or_title": quote_text.get_text(strip=True) if quote_text else "",
                    "category": "",
                    "price": None,
                    "rating": None,
                    "author": author_name,
                    "tags": tag_list,
                    "description": description,
                    "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
                records.append(record)

            next_link = soup.select_one("li.next a")
            if not next_link:
                break

        self.logger.info("Quotes scraper collected %s records", len(records))
        return records
