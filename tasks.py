from huey import RedisHuey, crontab

huey = RedisHuey('LUN_notifications', host='localhost', port=6379)

