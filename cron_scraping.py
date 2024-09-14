import traceback

from core.curl_cffi_scraper import LUNRentScraperCurl
from core.selenium_scraper import LUNRentScraperSelenium
from core.utils import get_orders, save_order, save_only_new_realties
from core.logger import logger


def curl_scraping():
    logger.info("Running curl scraping")
    orders = get_orders()
    for order in orders:
        _, search_url, last_scraped_id = order
        scraper = LUNRentScraperCurl(search_url, int(last_scraped_id))
        realties = scraper.scrape()
        logger.info(f"Scraped {len(realties)} realties")
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            save_only_new_realties(realties, int(order[0]))
    logger.info("Curl scraping finished")


def selenium_scraping():
    logger.info("Running selenium scraping")
    orders = get_orders()
    for order in orders:
        _, search_url, last_scraped_id = order
        scraper = LUNRentScraperSelenium(search_url, int(last_scraped_id))
        realties = scraper.scrape()
        logger.info(f"Scraped {len(realties)} realties")
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            save_only_new_realties(realties, int(order[0]))
    logger.info("Selenium scraping finished")


def scrape():
    """Runs curl scraping and if it fails, runs selenium scraping."""
    try:
        curl_scraping()
    except (Exception) as e:
        logger.error(f"Curl scraping failed or exceeded time limit: {e}, {traceback.format_exc()}")
        selenium_scraping()

if __name__ == "__main__":
    scrape()