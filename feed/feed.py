import pandas as pd
from sqlalchemy import create_engine
import time
from operator import itemgetter
import redis
import json
import warnings
warnings.filterwarnings("ignore")


HOST = "39.105.158.30"
USER = "koko"
PASSWORD = "rhkoko123"
DATABASE = "match_v2"


class Preprocess:

    def __init__(self):
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:3306/{}'.format(
                USER, PASSWORD, HOST, DATABASE))

    def videos_profile(self):
        sql = "SELECT v.id, v.user_id, v.addtime, v.circle_id,v.like_count, v.dislike_count," \
              "v.comment_count, l.cat_first, l.cat_second, l.goods_label, l.video_cat, l.video_label " \
              "FROM video v LEFT JOIN video_label l ON v.id=l.video_id" \
              " WHERE v.is_deleted=0  AND v.is_hide=0 AND v.is_review=1"

        df = pd.read_sql_query(sql, self.engine)
        df["video_cat"] = df["video_cat"].map({"种草": 1, "拔草": 1, "开箱": 5, "测评": 10})
        # df.to_csv("./video_profile", index=None)

        recom = {}
        i = 0
        for _, row in df.iterrows():
            video_id, addtime, video_label, like_count, dislike_count, comment_count, video_cat \
                = row["id"], row["addtime"], row["video_label"], row["like_count"], \
                  row["dislike_count"], row["comment_count"], row["video_cat"]
            if not video_label:
                continue
            recom.setdefault(video_label, {})
            time_vec = time.strptime(str(addtime), '%Y-%m-%d %H:%M:%S')
            vec = time.mktime(time_vec)
            time_factor = 1 / ((time.time() - vec) / 3600)
            recom[video_label].setdefault(video_id, like_count + dislike_count + comment_count + video_cat + time_factor)
            i += 1
        for key, vel in recom.items():

            vel = dict(sorted(vel.items(), key=itemgetter(1), reverse=True))
            recom[key] = vel
        print("内容总数:", i)
        return recom


if __name__ == '__main__':
    res = Preprocess().videos_profile()

    with open("./aa.json", "w", encoding="utf-8") as fw:
        json.dump(res, fw, indent=4, ensure_ascii=False)

    # pool = redis.ConnectionPool(host='127.0.0.1', password="kokomachine", port=6379, encoding="gbk")
    # redis_base = redis.Redis(connection_pool=pool)

    # for user, goods_rating in res.items():
    #     for goods, rating in goods_rating.items():
    #         redis_base.hset(name=user, key=goods, value=rating)
    # with open("./log.txt", "a") as fw:
    #     fw.writelines("redis 更新时间：" + time.strftime('%Y-%m-%d %X', time.localtime()))

