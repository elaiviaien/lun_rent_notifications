from huey import RedisHuey, crontab

from bot import process_order, send_notifications
from utils import get_orders, save_order

huey = RedisHuey("LUN_notifications", host="redis", port=6379)


@huey.periodic_task(crontab(minute="*/5"))
def periodic_scraping():
    orders = get_orders()
    for order in orders:

        realties = process_order(order)[::-1]
        if realties:
            save_order(int(order[0]), order[1], int(realties[-1]["id"]))
            send_notifications(order[0], realties)
