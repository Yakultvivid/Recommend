import time

from media.ItemCollaborationFilter.ItemCollaborationFiler import ItemCF


def run(train):
    start = time.time()
    print("即将开始基于物品的协同过滤推荐模型")
    # 基于邻域的协同过滤
    item_cf = ItemCF(train)

    item_cf.calc_item_sim()

    recommend = {}
    for user in train.keys():
        rec = item_cf.recommend(user)
        recommend[user] = rec

    print('ICF - Cost time: %f' % (time.time() - start))
    return recommend

