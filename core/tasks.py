from huey import RedisHuey, crontab
from bot import send_notifications
from core.utils import get_orders, get_unread_realties, update_realties_with_read

huey = RedisHuey('tasks', host='redis', port=6379)

@huey.task()
def send_new_realties():
    orders = get_orders()
    realties_n = 0
    for order in orders:
        user_id, search_url, last_scraped_id = order
        realties = get_unread_realties(int(user_id))
        if realties:
            realties_n += len(realties)
            send_notifications(user_id, realties)
            update_realties_with_read(realties, int(user_id))
    return "Sent notifications to users with new realties. Total realties sent: " + str(realties_n)

@huey.periodic_task(crontab(minute='*'))
def send_new_realties_periodic():
    send_new_realties()