import os
from curl_cffi import requests
from bs4 import BeautifulSoup

from .base_scraper import LUNRentScraper


class LUNRentScraperCurl(LUNRentScraper):
    def __init__(self, url: str, last_scraped_id: int = -1):
        super().__init__(url, last_scraped_id)
        self.session = requests.Session()
        self.proxies = {
            "http": os.getenv("PROXY_URL"),
            "https": os.getenv("PROXY_URL")
        }

    def get_full_html_page(self, url: str = None) -> str:
        url = url or self.search_url
        response = self.session.get(url, proxies=self.proxies, impersonate="chrome")
        return response.text

    def get_page_realties(self, url: str):
        html_content = self.get_full_html_page(url)
        soup = BeautifulSoup(html_content, "lxml")
        return soup.select(self.xpaths["root"])
