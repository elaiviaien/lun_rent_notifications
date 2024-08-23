from huey import RedisHuey, crontab

from bot import process_order, send_notifications
from utils import get_orders

huey = RedisHuey('LUN_notifications', host='localhost', port=6379)

@huey.periodic_task(crontab(minute='*/20'))
def periodic_scraping():
    orders = get_orders()
    for order in orders:
        realties=process_order(order)
        send_notifications(order[0], realties)

