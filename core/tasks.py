from bot import process_order, send_notifications
from .utils import get_orders, save_order

from celery import Celery
from celery.schedules import crontab

app = Celery('tasks', broker='redis://redis:6379/0', backend='redis://redis:6379/0')

app.conf.update(
    result_expires=3600,
)

@app.task
def periodic_scraping():
    orders = get_orders()
    for order in orders:

        realties = process_order(order)[::-1]
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            send_notifications(order[0], realties)

app.conf.beat_schedule = {
    'periodic-scraping-every-5-minutes': {
        'task': 'core.tasks.periodic_scraping',
        'schedule': crontab(minute='*/5'),
    },
}