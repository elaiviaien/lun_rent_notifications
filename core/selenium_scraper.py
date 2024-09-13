from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_scraper  import LUNRentScraper


class LUNRentScraperSelenium(LUNRentScraper):
    def __init__(self, url: str, last_scraped_id: int = -1):
        super().__init__(url, last_scraped_id)
        self.driver = self._init_driver()

    def _init_driver(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = Chrome(version_main=128, options=chrome_options)
        return driver

    def get_full_html_page(self, url: str=None) -> str:
        url = url or self.search_url
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.xpaths["root"])))
        return self.driver.page_source

    def get_page_realties(self, url: str):
        html_content = self.get_full_html_page(url)
        soup = BeautifulSoup(html_content, "lxml")
        return soup.select(self.xpaths["root"])


    def __del__(self):
        if self.driver:
            self.driver.quit()
