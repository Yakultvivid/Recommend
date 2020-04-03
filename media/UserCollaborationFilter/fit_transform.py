import time

from media.UserCollaborationFilter.UserCollaborationFilter import UserCF


def run(train):
    start = time.time()
    print("即将开始基于用户的协同过滤推荐模型")
    # 基于邻域的协同过滤
    user_cf = UserCF(train)
    user_cf.calc_user_sim()

    # 遍历用户列表
    recommend = {}
    for user in train.keys():

        rec = user_cf.recommend(user)
        recommend[user] = rec

    print('UCF - Cost time: %f' % (time.time() - start))

    return recommend
