from selenium.webdriver.chrome.options import Options
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LUNRentScraperSelenium:

    def __init__(self, url: str, last_scraped_id: int = -1):
        self.search_url = url
        self._validate_url()
        self.last_scraped_id = last_scraped_id
        self.xpaths = {
            'root': 'article.realty-preview',
            'id': 'article.realty-preview',
            'price': 'div.realty-preview-price--main',
            'address': 'button.realty-link-button.realty-preview-title__link',
            'description': 'p.realty-preview-description__text',
            'picture': 'picture img'
        }
        self.driver = self._init_driver()

    def _init_driver(self):
        """Initialize Selenium WebDriver (e.g., ChromeDriver)"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        driver = Chrome(version_main=128, options=chrome_options)
        return driver

    def _validate_url(self) -> None:
        # remove page argument from url
        url_parts = self.search_url.split('&')
        url_parts = [part for part in url_parts if not part.startswith('page=')]
        url = '&'.join(url_parts)
        self.search_url = url

    def get_page_realties(self, url: str):
        """Load the webpage and return the realty elements"""
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, self.xpaths['root'])))
        realties = self.driver.find_elements(By.CSS_SELECTOR, self.xpaths['root'])
        return realties

    def parse(self, realties) -> list[dict]:
        """Parse realty elements and extract data"""
        results = []
        for realty in realties:
            result = {}
            try:
                # Extract realty ID
                result['id'] = realty.get_attribute('id')
                # Extract price
                result['price'] = realty.find_element(By.CSS_SELECTOR, self.xpaths['price']).text
                # Extract address
                result['address'] = realty.find_element(By.CSS_SELECTOR, self.xpaths['address']).text
                # Extract description
                result['description'] = realty.find_element(By.CSS_SELECTOR, self.xpaths['description']).text
                # Extract image URL
                result['picture'] = realty.find_element(By.CSS_SELECTOR, self.xpaths['picture']).get_attribute('src')
            except Exception as e:
                # Handle exceptions in case any field is missing
                print(f"Error parsing realty: {e}")
            results.append(result)
        return results

    def scrape(self) -> list[dict]:
        """Main scraping loop"""
        page = 1
        results = []
        ids = set()

        while True:
            url = f'{self.search_url}&page={page}'
            soup_realties = self.get_page_realties(url)

            if not soup_realties:
                break

            page_results = self.parse(soup_realties)
            results.extend(page_results)

            current_ids = {realty['id'] for realty in page_results}

            if self.last_scraped_id == -1 or self.last_scraped_id in ids:
                break

            page += 1
            ids.update(current_ids)

        self.driver.quit()
        return results

