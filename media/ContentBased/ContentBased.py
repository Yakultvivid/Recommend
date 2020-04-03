from __future__ import division
import os
import operator


def get_ave_score(input_file):
    """
    Args:
        input_file:user rating file
    Return:
        a dict, key:item_id value: ave_score  {item_id: [分数和, 行为用户和]}
    """

    record = {}
    ave_score = {}
    with open(input_file) as fp:
        for i, line in enumerate(fp):
            if i == 0:  # 去掉文件第一行的title
                continue
            else:
                user, goods, rating = line.split(',')
                if goods not in record:
                    record[goods] = [0, 0]
                record[goods][0] += float(rating)
                record[goods][1] += 1
                i += 1

    for item_id in record:
        ave_score[item_id] = round(record[item_id][0]/record[item_id][1], 3)
    return ave_score


def get_item_cate(ave_score, input_file):
    """
    returns
            a dict : key item_id  value a dict ,key:cate value:ratio {item_id:{cate:ratio}}
            a dict: ket cate value[item_id1,item_id2,....]
    """
    topk = 100
    item_cate = {}  # 物品、类别字典
    record = {}
    cate_item_sort = {}  # 物品、类别字典
    fp = open(input_file, 'r', encoding='UTF-8')
    for line in fp:
        item = line.strip().split('::')
        if len(item) < 3:
            continue
        item_id = item[0]
        cate_str = item[-1]  # 物品的种类
        cate_list = cate_str.strip().split('|')
        ratio = round(1/len(cate_list), 3)   # 算出每个物品种类的比率
        if item_id not in item_cate:
            item_cate[item_id] = {}
        for fix_cate in cate_list:
            item_cate[item_id][fix_cate] = ratio  # 物品、类别
    fp.close()
    for item_id in item_cate:
        for cate in item_cate[item_id]:
            if cate not in record:
                record[cate] = {}
            item_id_rating_score = ave_score.get(item_id, 0)
            record[cate][item_id] = item_id_rating_score  # {label: {item_id: 平均分}}
    for cate in record:
        if cate not in cate_item_sort:
            cate_item_sort[cate] = []
        for zuhe in sorted(record[cate].items(), key=operator.itemgetter(1), reverse=True)[:topk]:
            cate_item_sort[cate].append(zuhe[0])
    print("item_cate", item_cate)
    print("cate_item_sort", cate_item_sort)
    return item_cate,cate_item_sort


def get_user_profile(item_cate, input_file):
    """
    Args:
        item_cate:key item_id, value: dict , key category value ratio  即{item_id:{category:ratio}}
        input_file:user rating file 评分文件
    Return:
        a dict: key user_id, value [(category, ratio), (category1, ratio1)] 即{user_id:[(category,ratio)......}
    """
    record = {}
    user_profile = {}
    score_thr = 4.0
    topk = 2
    fp = open(input_file)
    for line in fp:
        item = line.strip().split('::')
        if len(item) < 4:
            continue
        user_id, item_id, rating, timestamp = item[0], item[1], float(item[2]), int(item[3])
        if rating < score_thr:
            continue
        if item_id not in item_cate:
            continue
        if user_id not in record:
            record[user_id] = {}
        for fix_cate in item_cate[item_id]:
            if fix_cate not in record[user_id]:
                record[user_id][fix_cate] = 0
            record[user_id][fix_cate] += rating * item_cate[item_id][fix_cate]  # 每一个类别权重和
    fp.close()
    for user_id in record:  # 排序
        if user_id not in user_profile:
            user_profile[user_id] = []
        total_score = 0
        for zuhe in sorted(record[user_id].items(), key=operator.itemgetter(1), reverse=True)[:topk]:  # 对类别中的权重进行排序
            user_profile[user_id].append((zuhe[0], zuhe[1]))  # zuhe[0]种类 zuhe[1]权重
            total_score += zuhe[1]
        for index in range(len(user_profile[user_id])):
            user_profile[user_id][index] = (user_profile[user_id][index][0], round(user_profile[user_id][index][1]/total_score, 3))
            # 这里的ratio表征着用户与物品的相近关系，得分越低，差距越大
    print("user_profile", user_profile)
    return user_profile


def recom(cate_item_sort, user_profile, user_id, topk= 10):
    """
    Args:
        cate_item_sort:reverse sort
        user_profile: 用户画像
        user_id:fix user_id to recom
        topk:recom num
    Return:
         a dict, key user_id value [item_id1, item_id2]
    """

    if user_id not in user_profile:
        return {}
    recom_result = {}
    if user_id not in recom_result:
        recom_result[user_id] = []
    for zuhe in user_profile[user_id]:
        cate = zuhe[0]
        ratio = zuhe[1]
        num = int(topk*ratio)
        if cate not in cate_item_sort:
            continue
        recom_list = cate_item_sort[cate][:num]
        recom_result[user_id] += recom_list
    return recom_result



