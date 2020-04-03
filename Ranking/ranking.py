from operator import itemgetter
import json
import random
import pandas as pd

import config


def fuse(icf, ucf, lfm):
    """
    模型召回权重融合
    """
    recommend = {}
    for user, recall in icf.items():
        recommend[user] = dict()
        for video, rating in icf[user].items():
            recommend[user].setdefault(video, rating * 0.1 + random.uniform(0, 10))

        for video, rating in ucf[user].items():
            try:
                recommend[user][video] += rating
            except KeyError:
                recommend[user][video] = rating + random.uniform(0, 10)

        for video, rating in lfm[user].items():
            try:
                recommend[user][video] += rating * 10
            except KeyError:
                recommend[user][video] = rating + random.uniform(0, 10)
    return recommend


def ranking(recommend, fr, cr):
    """
    :param recommend: 召回
    :param fr: follow_recommend
    :param cr: circle_recommend
    :return: 加入和标签的影响
    """
    rating = pd.read_csv(config.DATA_PATH.format("data/rating"), dtype={"user_id": str, "video_id": str})
    video_profile = pd.read_csv(config.DATA_PATH.format("data/video_profile"), dtype={"video_id": str})
    user_label = {}
    for _, row in rating.iterrows():
        user, video, rating = row["user_id"], row["video_id"], row["rating"]

        try:
            label = video_profile[video_profile["video_id"] == video]["video_label"].values[0]
            if label == "NaN":
                continue
            # cat = video_profile[video_profile["video_id"] == video]["cat_second"].values[0]
            user_label.setdefault(user, {})
            user_label[user].setdefault(label, 0)
            user_label[user][label] += rating
            # user_label[user].setdefault(cat, 0)
            # user_label[user][cat] += rating
        except IndexError:
            pass  # 已删视频 103,104,105,4947
    with open(config.DATA_PATH.format("data/user_label.json"), "w", encoding="utf8") as fw:
        json.dump(user_label, fw, indent=4, ensure_ascii=False)
    for user, recall_lis in recommend.items():
        for video, rating in recall_lis.items():
            try:
                label = video_profile[video_profile["video_id"] == video]["video_label"].values[0]
                if label in user_label[user]:
                    recommend[user][video] += user_label[user][label] * 0.1
            except IndexError:
                pass  # 已删视频 103,104,105,4947
    for user, recall in fr.items():
        recommend.setdefault(user, {})
        for video in recall[:10]:
            recommend[user].setdefault(video, random.uniform(0, 20))
    for user, recall in cr.items():
        recommend.setdefault(user, {})
        for video in recall[:10]:
            recommend[user].setdefault(video, random.uniform(0, 20))

    with open(config.DATA_PATH.format("data/dislike"), "r") as fp:
        dislike = json.load(fp)
    for k, v in recommend.items():
        if k in dislike.keys():
            for vi in dislike[k]:
                try:
                    v.pop(vi)
                except KeyError:
                    pass
        c = dict(sorted(v.items(), key=itemgetter(1), reverse=True))
        recommend[k] = c
    with open(config.DATA_PATH.format("recall/master.json"), "w", encoding="utf8") as fw:
        json.dump(recommend, fw, indent=4, ensure_ascii=False)
    return recommend
