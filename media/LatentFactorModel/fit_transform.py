import time
import operator

from media.LatentFactorModel import LatentFactorModel
import config


def recommend(user, train, p, q):
    rank = dict()
    interacted_items = train[user]
    for i in q:
        if i in interacted_items.keys():
            continue
        rank.setdefault(i, 0)
        for f, qif in q[i].items():
            puf = p[user][f]
            rank[i] += puf * qif
    return rank


def recommendation(users, train, p, q):
    result = dict()
    i = 1
    for user in users:
        rank = recommend(user, train, p, q)
        r = dict(sorted(rank.items(), key=operator.itemgetter(1), reverse=True)[: config.LFM_TOP_N])
        result[user] = r
        i += 1

    print("用户总数：%d" % i)
    return result


def run(train):
    start = time.time()
    print("即将开始基于隐语义矩阵分解的推荐模型")
    lfm = LatentFactorModel.LFM()
    [P, Q] = lfm.latent_factor_model(train)
    # rank = recommend(user, train, P, Q)
    result = recommendation(train.keys(), train, P, Q)
    print('LFM - Cost time: %f' % (time.time() - start))
    return result


