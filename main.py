from dataProcessing import dataProcessing
from media import manage
from Ranking import ranking
from update import update

if __name__ == '__main__':

    # 数据加载层
    dataProcessing.Preprocess().user_profile()
    follow_recommend, circle_recommend = dataProcessing.Preprocess().follow_circle()

    # 多路召回
    icf_recommend, ucf_recommend, lfm_recommend = manage.learning()

    # 权重融合
    recall_master = ranking.fuse(icf_recommend, ucf_recommend, lfm_recommend)
    ranking.ranking(recall_master, follow_recommend, circle_recommend)

    # 缓存
    # update.run()
