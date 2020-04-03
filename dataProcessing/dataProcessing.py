import pandas as pd
from sqlalchemy import create_engine
from functools import reduce
import json
import time

from dataProcessing.TextSimilarity import Keywords
import config

import warnings
warnings.filterwarnings("ignore")


class Preprocess:
    """
    user_profile() 用户画像
    rating_data() user-item-rating
    videos_profile() 内容画像
    follow_data() 关注推荐
    circle_data() 圈子推荐
    """

    def __init__(self):
        self.engine = create_engine('mysql+pymysql://{}:{}@{}:3306/{}'.format(
                config.USER, config.PASSWORD, config.HOST, config.DATABASE))
        self.engine_old = create_engine('mysql+pymysql://{}:{}@{}:3306/match_shihe'.format(
            config.USER, config.PASSWORD, config.HOST))

    @staticmethod
    def time_factor(string):
        time_vec = time.strptime(string, '%Y-%m-%d %H:%M:%S')
        vec = time.mktime(time_vec)
        time_factor = (time.time() - vec) / 3600
        return round(time_factor)

    @staticmethod
    def constellation(birthday):
        if birthday:
            birthday = str(birthday)
            month, day = int(birthday[-4: -2]), int(birthday[-2:])
            n = (u'摩羯座', u'水瓶座', u'双鱼座', u'白羊座', u'金牛座', u'双子座', u'巨蟹座', u'狮子座', u'处女座', u'天秤座', u'天蝎座', u'射手座')
            d = [(1, 20), (2, 19), (3, 21), (4, 21), (5, 21), (6, 22), (7, 23), (8, 23), (9, 23), (10, 23), (11, 23),
                 (12, 23)]
            c = [x for x in d if x <= (month, day)]
            return n[len(c) % 12]
        else:
            return 0

    def user_profile(self):
        """ 用户个人信息 """
        # 东北/华北/华中/华东/西北/西南/华南/境外
        sql_label = "SELECT user_id,  labels FROM user_label "
        df_label = pd.read_sql_query(sql_label, self.engine)

        sql_info = "SELECT id as user_id, gender, age, birthday, city FROM sh_user"
        df_info = pd.read_sql_query(sql_info, self.engine_old, coerce_float=False)
        df = df_info.merge(df_label, how="outer", on="user_id")
        df["constellation"] = df_info["birthday"].map(self.constellation)
        df.fillna(0).to_csv(config.DATA_PATH.format("data/user_profile"), index=None)

    def rating_data(self):
        """
        种草user_like， 拔草user_dislike， 想买user_want_buy， 评论comment, 分享video_share_log, 不感兴趣video_dislike_log
        下单order,
        完播率video_view_log
        """

        # 过滤隐藏的视频
        sql_hide = "SELECT id FROM video as v WHERE  v.is_deleted=1 OR v.is_hide=1 OR is_review=0"
        df_hide = pd.read_sql_query(sql_hide, self.engine)
        hide_list = tuple(df_hide["id"].tolist())

        sql_like = "SELECT user_id, video_id, COUNT(id) as like_count " \
                   "FROM user_like WHERE is_deleted=0 AND video_id NOT IN {} GROUP BY user_id, video_id".format(hide_list)
        df_like = pd.read_sql_query(sql_like, self.engine)

        sql_dislike = "SELECT user_id, video_id, COUNT(id) as dislike_count " \
                      "FROM user_dislike WHERE is_deleted=0 AND video_id NOT IN {} GROUP BY user_id, video_id".format(hide_list)
        df_dislike = pd.read_sql_query(sql_dislike, self.engine)
        """ 想买 """
        # sql_want_buy = "SELECT user_id, goods_id, COUNT(id) as want_buy_count " \
        #                "FROM user_want_buy WHERE is_deleted=0 GROUP BY user_id, goods_id"
        # df_want_buy = pd.read_sql_query(sql_want_buy, self.engine)

        sql_comment = "SELECT user_id, video_id, COUNT(id) as comment_count " \
                      "FROM comment WHERE is_deleted=0 AND video_id NOT IN {} GROUP BY user_id, video_id".format(hide_list)
        df_comment = pd.read_sql_query(sql_comment, self.engine)
        """ 订单 """
        # sql_order = "SELECT user_id, goods_id, goods_sku_id, COUNT(id) as order_count " \
        #             "FROM order WHERE refund_status=0 GROUP BY user_id, goods_id"
        # df_order = pd.read_sql_query(sql_order, self.engine)
        """ 分享 """
        sql_share = "SELECT user_id, video_id, COUNT(id) as share_count " \
                    "FROM video_share_log WHERE video_id NOT IN {} GROUP BY user_id, video_id".format(hide_list)
        df_share = pd.read_sql_query(sql_share, self.engine)
        """ 不感兴趣 """
        sql_video_dislike = "SELECT user_id, video_id FROM video_dislike_log " \
                            "WHERE video_id NOT IN {}".format(hide_list)
        df_video_dislike = pd.read_sql_query(sql_video_dislike, self.engine)
        df_video_dislike["video_dislike"] = 1
        # 不感兴趣记录
        dislike = {}
        for _, row in df_video_dislike.iterrows():
            user, video = row["user_id"], row["video_id"]
            sql_dislike = "select id from video where user_id=(select user_id FROM video where id={})".format(video)
            user_dislike = pd.read_sql_query(sql_dislike, self.engine)
            dislike.setdefault(str(user), [])
            user_dislike["id"] = user_dislike[["id"]].applymap(str)
            dislike[str(user)] = list(set(dislike[str(user)]) | set(user_dislike["id"].values.tolist()))
        with open(config.DATA_PATH.format("data/dislike"), "w") as fw:
            json.dump(dislike, fw, indent=4, ensure_ascii=False)

        """ 完播率 """
        sql_view_log = "SELECT user_id, video_id, view_long FROM video_view_log " \
                       "WHERE video_id NOT IN {} AND view_long!=0".format(hide_list)
        # sql_view_log = "SELECT user_id, video_id, view_long FROM video_view_log as l " \
        #                "LEFT JOIN video ON video.id=l.video_id " \
        #                "WHERE v.is_deleted=1 OR v.is_hide=1 OR is_review=0 AND view_long!=0"

        df_view_log = pd.read_sql_query(sql_view_log, self.engine)
        df_view = df_view_log.groupby(by=['user_id', "video_id"])[['view_long']].max().reset_index()

        df_list = [df_like, df_dislike, df_comment, df_share, df_video_dislike, df_view]
        df = reduce(lambda left, right: pd.merge(left, right, on=["user_id", "video_id"], how="outer"), df_list)
        df = df.fillna(0)

        # like_count, dislike_count, comment_count, share_count, video_dislike, view_long
        df["rating"] = df["like_count"] * 5 + df["dislike_count"] * (-4) + df["comment_count"] * 5 + \
                       df["share_count"] * 8 + df["video_dislike"] * (-10) + df["view_long"] * 0.1

        rating = df[['user_id', "video_id", "rating"]]
        rating.to_csv(config.DATA_PATH.format("data/rating"), index=None)
        rat = {}
        for _, row in rating.iterrows():
            user_id, video_id = row["user_id"], row["video_id"]
            rat.setdefault(user_id, [])
            rat[user_id].append(video_id)
        return rat

    def videos_profile(self):

        sql = "SELECT v.id as video_id, v.video_des, v.user_id as video_user, v.addtime, v.circle_id, " \
              "v.like_count, v.dislike_count, v.comment_count, l.cat_second, l.video_cat, l.video_label " \
              "FROM video v LEFT JOIN video_label l ON v.id=l.video_id " \
              "WHERE v.is_deleted=0 AND v.is_hide=0 AND v.is_review=1"
        # 文案提取关键词
        df = pd.read_sql_query(sql, self.engine, coerce_float=False)
        df["des_keywords"] = df["video_des"].map(Keywords.content2keywords)
        for kw in df["des_keywords"]:
            if not kw:
                df["des_keywords"] = df["video_des"].map(Keywords.content2words)
        # 时间差
        df["time_factor"] = df["addtime"].map(str).map(self.time_factor)
        # 视频热度
        df["hot_number"] = df["like_count"] + df["dislike_count"] + df["comment_count"]
        # 视频分类映射
        df["cat"] = df["video_cat"].map({"种草": 1, "拔草": 2, "开箱": 3, "测评": 4})
        # print(df.columns.values.tolist())
        df = df[["video_id", "video_user", "des_keywords", "time_factor", "hot_number",
                "circle_id", "cat_second", "video_label", "cat"]].fillna(0)
        df[["circle_id", "cat_second"]] = df[["circle_id", "cat_second"]].applymap(int)
        df.to_csv(config.DATA_PATH.format("data/video_profile"), index=None)

        # df[["video_id", ""]].to_csv(config.DATA_PATH.format(r"data\cb_video_profile"), index=None)
        return df

    def follow_circle(self):
        """ 用户关注信息 """
        sql = "SELECT u.user_id, v.user_id as follow_user, v.id " \
              "FROM video as v " \
              "LEFT JOIN user_relation as u " \
              "ON u.follow_user_id=v.user_id WHERE u.is_delete=0 AND v.is_deleted=0 AND v.is_review=1 AND v.is_hide=0"
        df = pd.read_sql_query(sql, self.engine)

        # 待过滤的推荐
        rat = self.rating_data()
        error_user = set()
        follow_recommend = {}
        for _, row in df.iterrows():
            user_id, video_id = row["user_id"], row["id"]
            follow_recommend.setdefault(str(user_id), [])
            try:
                if video_id not in rat[user_id]:
                    follow_recommend[str(user_id)].append(str(video_id))
            except KeyError:
                follow_recommend[str(user_id)].append(str(video_id))
                error_user.add(user_id)
        # print("有关注用户却没有视频行为交互的用户id：", error_user)
        with open(config.DATA_PATH.format("recall/follow_recommend"), "w") as fw:
            json.dump(follow_recommend, fw, indent=4, ensure_ascii=False)
        # 列表为空的情况： 关注的用户并未发布过内容

        """ 圈子关注信息 """
        # 用户关注的圈子
        sql = "SELECT user_id, circle_id FROM circle_user  WHERE is_deleted=0 "
        df = pd.read_sql_query(sql, self.engine)

        # 圈子内容
        circle = {}
        video_profile = self.videos_profile()
        for _, row in video_profile.iterrows():
            video_id, circle_id = str(row["video_id"]), row["circle_id"]
            circle.setdefault(circle_id, [])
            circle[circle_id].append(video_id)

        # 圈子推荐
        error_user = set()
        circle_recommend = {}
        for _, row in df.iterrows():
            user_id, circle_id = row["user_id"], row["circle_id"]
            circle_recommend.setdefault(str(user_id), [])
            for video_id in circle[circle_id]:
                try:
                    if video_id not in rat[user_id]:
                        circle_recommend[str(user_id)].append(video_id)
                except KeyError:
                    error_user.add(user_id)
                    circle_recommend[str(user_id)].append(video_id)
        # print("加入了圈子却没有视频行为交互的用户id：", error_user)
        with open(config.DATA_PATH.format("recall/circle_recommend"), "w") as fw:
            json.dump(circle_recommend, fw, indent=4, ensure_ascii=False)
        return follow_recommend, circle_recommend

