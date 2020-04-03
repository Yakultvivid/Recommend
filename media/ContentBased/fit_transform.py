import time

from media.ContentBased import ContentBased as cb
import config


def run():
    start = time.time()
    print("即将开始基于内容的推荐模型")
    ave_score = cb.get_ave_score(config.DATA_PATH.format(r"data\rating"))
    item_cate, cate_item_sort = cb.get_item_cate(ave_score, config.DATA_PATH.format(r"data\video_profile"))
    up = cb.get_user_profile(item_cate, config.DATA_PATH.format(r"data\rating"))
    recom = {}
    for user_id in up.keys():
        res = cb.recom(cate_item_sort, up, user_id)
        recom.update(res)
    print('CB - Cost time: %f' % (time.time() - start))
    return recom

