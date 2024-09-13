from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By


class LUNRentScraper(ABC):
    def __init__(self, url: str, last_scraped_id: int = -1):
        self.search_url = url
        self._validate_url()
        self.last_scraped_id = last_scraped_id
        self.xpaths = {
            "root": "article.realty-preview",
            "id": "article.realty-preview",
            "price": "div.realty-preview-price--main",
            "address": "button.realty-link-button.realty-preview-title__link",
            "description": "p.realty-preview-description__text",
            "picture": "picture img",
        }

    @abstractmethod
    def get_page_realties(self, url: str):
        """Fetch the page content and return the realty elements."""
        pass

    @abstractmethod
    def get_full_html_page(self, url: str) -> str:
        """Fetch the full HTML content of the page."""
        pass

    def _validate_url(self) -> None:
        """Clean up and validate the URL."""
        url_parts = self.search_url.split("&")
        url_parts = [
            part for part in url_parts
            if not part.startswith("page=") and not part.startswith("sort=")
        ]
        url = "&".join(url_parts)
        url += "&sort=insert_time"
        self.search_url = url

    def parse(self, realties) -> list[dict]:
        """Parse realty elements and extract data."""
        results = []
        for realty in realties:
            result = {}
            if not realty.get("id"):
                continue

            def get_text_attr(selector):
                element = realty.select_one(selector) if hasattr(realty, 'select_one') else realty.find_element(
                    By.CSS_SELECTOR, selector)
                return element.text.strip() if element else ""

            result["id"] = int(realty.get("id", -1))  # Handle cases where 'id' might be missing
            result["price"] = get_text_attr(self.xpaths["price"])
            result["address"] = get_text_attr(self.xpaths["address"])
            result["description"] = get_text_attr(self.xpaths["description"])
            picture = realty.select_one(self.xpaths["picture"]) if hasattr(realty,
                                                                           'select_one') else realty.find_element(
                By.CSS_SELECTOR, self.xpaths["picture"])
            result["picture"] = picture.get("src") if picture else None

            results.append(result)
        return results

    def scrape(self) -> list[dict]:
        """Main scraping loop."""
        page = 1
        new_realties = []
        all_realties = []
        ids = set()

        while True:
            url = f"{self.search_url}&page={page}"
            page_realties = self.get_page_realties(url)

            if not page_realties:
                break

            page_results = self.parse(page_realties)
            all_realties.extend(page_results)

            current_ids = {realty["id"] for realty in page_results}

            if self.last_scraped_id == -1 or self.last_scraped_id in current_ids:
                for realty in all_realties:
                    if realty["id"] == self.last_scraped_id:
                        break
                    new_realties.append(realty)
                break

            page += 1
            ids.update(current_ids)

        return new_realties
