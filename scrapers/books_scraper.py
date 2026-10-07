import logging
from datetime import datetime, timezone
from typing import Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class BooksScraper:
    BASE_URL = "https://books.toscrape.com/"

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
        normalized_path = path.lstrip("/")
        if not normalized_path.startswith("catalogue/"):
            normalized_path = f"catalogue/{normalized_path}"
        return f"{self.BASE_URL.rstrip('/')}/{normalized_path}"

    def _extract_rating(self, article: Any) -> float | None:
        star_element = article.select_one("p.star-rating")
        if not star_element:
            return None
        classes = star_element.get("class", [])
        if len(classes) < 2:
            return None
        mapping = {
            "One": 1,
            "Two": 2,
            "Three": 3,
            "Four": 4,
            "Five": 5,
        }
        value = classes[1]
        return mapping.get(value)

    def _scrape_detail_page(self, detail_url: str):
        response = self._fetch(detail_url)
        if response is None:
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.select_one("div.product_main h1")
        price = soup.select_one("p.price_color")
        description = soup.select_one("article.product_page > p")
        breadcrumbs = soup.select("ul.breadcrumb li")
        category = breadcrumbs[-2].get_text(strip=True) if len(breadcrumbs) >= 3 else ""
        rating = self._extract_rating(soup)

        if title is None:
            return None

        record = {
            "source": "Books to Scrape",
            "source_url": detail_url,
            "base_url": self.BASE_URL,
            "name_or_title": title.get_text(strip=True),
            "category": category,
            "price": price.get_text(strip=True) if price else "",
            "rating": rating,
            "author": "",
            "tags": [],
            "description": description.get_text(" ", strip=True) if description else "",
            "scraped_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        return record

    def scrape_all(self):
        records = []
        for page_number in range(1, self.max_pages + 1):
            page_url = self.BASE_URL if page_number == 1 else f"{self.BASE_URL}catalogue/page-{page_number}.html"
            response = self._fetch(page_url)
            if response is None:
                break

            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.select("article.product_pod")
            if not articles:
                break

            for article in articles:
                title_link = article.select_one("h3 a")
                if title_link is None:
                    continue
                detail_path = title_link.get("href")
                detail_url = self._absolute_url(detail_path)
                detail_record = self._scrape_detail_page(detail_url)
                if detail_record:
                    records.append(detail_record)

            next_link = soup.select_one("li.next a")
            if not next_link:
                break

        self.logger.info("Books scraper collected %s records", len(records))
        return records
