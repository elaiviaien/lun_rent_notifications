import os

from curl_cffi import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from dotenv import load_dotenv

load_dotenv()

class LUNRentScraper:

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
            'picture': 'picture  img'
        }

        self.proxies = {
            'http': os.getenv("PROXY_URL"),
            'https': os.getenv("PROXY_URL")}

    def get_full_html_page(self)->str:
        response = requests.get(self.search_url, proxies=self.proxies, impersonate="chrome")
        content = response.text
        return content

    def _validate_url(self) -> None:
        # remove page argument from url
        url_parts = self.search_url.split('&')
        url_parts = [part for part in url_parts if not part.startswith('page=') and not part.startswith('sort=')]
        url = '&'.join(url_parts)
        url += '&sort=insert_time'
        self.search_url = url

    def get_page_realties(self, url: str) -> ResultSet[Tag]:
        response = requests.get(url, proxies=self.proxies, impersonate="chrome")
        soup = BeautifulSoup(response.text, 'lxml')
        soup_realties = soup.select(self.xpaths['root'])
        return soup_realties

    def parse(self, soup_realties: ResultSet[Tag]) -> list[dict]:
        results = []
        for realty in soup_realties:
            result = {}
            for key, xpath in self.xpaths.items():
                if key == 'picture':
                    result[key] = realty.select_one(xpath)['src']
                elif key == 'id':
                    result[key] = int(realty['id'])
                else:
                    try:
                        result[key] = realty.select_one(xpath).text
                    except AttributeError:
                        result[key] = None
            results.append(result)
        return results

    def scrape(self) -> list[dict]:
        page = 1
        new_realties = []
        all_realties = []
        ids = set()

        while True:
            url = f'{self.search_url}&page={page}'
            soup_realties = self.get_page_realties(url)

            if not soup_realties:
                break

            page_results = self.parse(soup_realties)
            all_realties.extend(page_results)

            current_ids = {realty['id'] for realty in page_results}

            if self.last_scraped_id == -1 or self.last_scraped_id in current_ids:
                for realty in all_realties:
                    if realty['id'] == self.last_scraped_id:
                        break
                    new_realties.append(realty)
                break

            page += 1
            ids.update(current_ids)


        return new_realties




