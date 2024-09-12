import unittest
from retrying import retry


class TestLUNRentScraperReal(unittest.TestCase):
    def setUp(self):
        self.url = "https://lun.ua/uk/search?currency=UAH&geo_id=10009580&has_eoselia=false&is_without_fee=false&price_sqm_currency=UAH&section_id=2&sort=insert_time"

    def validate_scraper_results(self, url, lun_scraper):
        scraper = lun_scraper(url, last_scraped_id=-1)
        results = scraper.scrape()

        self.assertGreater(
            len(results), 0, "No results found"
        )

        first_result = results[0]

        required_fields = ["id", "price", "address", "description", "picture"]
        for field in required_fields:
            self.assertIn(field, first_result)

        print(first_result)

    @retry(wait_fixed=2000, stop_max_attempt_number=3)
    def test_scrape_curl_cffi(self):
        from .scraper import LUNRentScraper

        self.validate_scraper_results(self.url, LUNRentScraper)


if __name__ == "__main__":
    unittest.main()
