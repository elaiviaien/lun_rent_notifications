from curl_cffi import requests
from bs4 import BeautifulSoup, ResultSet, Tag


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
    def get_full_html_page(self)->str:
        response = requests.get(self.search_url, impersonate="chrome")
        content = response.text
        return content

    def _validate_url(self) -> None:
        # remove page argument from url
        url_parts = self.search_url.split('&')
        url_parts = [part for part in url_parts if not part.startswith('page=')]
        url = '&'.join(url_parts)
        self.search_url = url

    def get_page_realties(self, url: str) -> ResultSet[Tag]:
        response = requests.get(url)
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
                    result[key] = realty['id']
                else:
                    try:
                        result[key] = realty.select_one(xpath).text
                    except AttributeError:
                        result[key] = None
            results.append(result)
        return results

    def scrape(self) -> list[dict]:
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

        return results


