import json
import redis
import time

import config


def run():
    recall_name = config.DATA_PATH.format(r"recall\master.json")
    pool = redis.ConnectionPool(host='127.0.0.1', password="kokomachine", port=6379, db=1)
    redis_base = redis.Redis(connection_pool=pool)

    list_keys = redis_base.keys()
    for key in list_keys:
        redis_base.delete(key)

    with open(recall_name, 'rb') as f:
        dic = json.load(f)
    for user, goods_rating in dic.items():
        # redis_base.delete(user)
        if redis_base.hlen(user) >= 100:
            continue
        for goods, rating in goods_rating.items():
            redis_base.hset(name=user, key=goods, value=rating)
    with open(config.DATA_PATH.format("log.txt"), "a") as fw:
        fw.writelines("redis 更新时间：" + time.strftime('%Y-%m-%d %X', time.localtime()))
