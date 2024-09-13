import logging

from billiard.exceptions import SoftTimeLimitExceeded, TimeLimitExceeded

from bot import send_notifications
from .curl_cffi_scraper import LUNRentScraperCurl
from .selenium_scraper import LUNRentScraperSelenium
from .utils import get_orders, save_order

from celery import Celery, chain
from celery.schedules import crontab

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

@app.task(time_limit=120, soft_time_limit=60)
def curl_scraping():
    orders = get_orders()
    for order in orders:
        _, search_url, last_scraped_id = order
        scraper = LUNRentScraperCurl(search_url, int(last_scraped_id))
        realties = scraper.scrape()
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            send_notifications(order[0], realties)


@app.task
def selenium_scraping():
    orders = get_orders()
    for order in orders:
        _, search_url, last_scraped_id = order
        scraper = LUNRentScraperSelenium(search_url, int(last_scraped_id))
        realties = scraper.scrape()
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            send_notifications(order[0], realties)

@app.task
def handle_curl_failure(exc, task_id, args, kwargs, einfo):
    logging.info(f"Curl scraping failed or exceeded time limit: {exc}")

    selenium_scraping.delay()


@app.task
def periodic_scraping():
    """Runs curl scraping and if it fails, runs selenium scraping."""
    try:
        curl_scraping.apply_async(link_error=handle_curl_failure.s())
    except (Exception, SoftTimeLimitExceeded, TimeLimitExceeded) as e:
        print(f"Curl scraping failed or exceeded time limit: {e}")
        selenium_scraping.delay()

app.conf.beat_schedule = {
    'periodic-scraping-every-5-minutes': {
        'task': 'core.tasks.periodic_scraping',
        'schedule': crontab(minute='*/5'),
    },
}