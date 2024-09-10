import unittest
from selenium_scraper import LUNRentScraperSelenium


class TestLUNRentScraperSeleniumReal(unittest.TestCase):

    def test_scrape_real_page(self):
        url = 'https://lun.ua/uk/search?currency=UAH&geo_id=10009580&has_eoselia=false&is_without_fee=false&price_sqm_currency=UAH&section_id=2&sort=insert_time'

        scraper = LUNRentScraperSelenium(url, last_scraped_id=-1)

        results = scraper.scrape()

        self.assertGreater(len(results), 0, "No realties were scraped from the real page.")

        first_result = results[0]

        self.assertIn('id', first_result)
        self.assertIn('price', first_result)
        self.assertIn('address', first_result)
        self.assertIn('description', first_result)
        self.assertIn('picture', first_result)

        print(first_result)


if __name__ == '__main__':
    unittest.main()
