import json

from media.ContentBased import fit_transform as cb
from media.ItemCollaborationFilter import fit_transform as icf
from media.UserCollaborationFilter import fit_transform as ucf
from media.LatentFactorModel import fit_transform as lfm
from dataProcessing import train_test_split
from evaluate import evaluate
import config


def learning():
    # 数据切分
    file_name = config.DATA_PATH.format("data/rating")
    # train, test = train_test_split.train_test_split(file_name)
    train = train_test_split.get_train_data(file_name)

    # 基于内容的推荐

    # with open(config.DATA_PATH.format("recall\\1.json"), "w", encoding="utf8") as fw:
    #     cb_recommend = cb.run()
    #     json.dump(cb_recommend, fw, indent=4, ensure_ascii=False)

    # 基于item的协同过滤

    with open(config.DATA_PATH.format("recall/2.json"), "w", encoding="utf8") as fw:
        icf_recommend = icf.run(train)
        json.dump(icf_recommend, fw, indent=4, ensure_ascii=False)
    # 准确率: 0.12579022061669462
    # 覆盖率: 0.985480943738657
    # 新颖度: 1.404205705016157

    # 基于user的协同过滤

    with open(config.DATA_PATH.format("recall/3.json"), "w", encoding="utf8") as fw:
        ucf_recommend = ucf.run(train)
        json.dump(ucf_recommend, fw, indent=4, ensure_ascii=False)
    # 准确率: 0.14024649383765406
    # 覆盖率: 0.9908759124087592
    # 新颖度: 1.37742911267773

    # 隐语义模型

    with open(config.DATA_PATH.format("recall/4.json"), "w", encoding="utf8") as fw:
        lfm_recommend = lfm.run(train)
        json.dump(lfm_recommend, fw, indent=4, ensure_ascii=False)
    # 准确率: 0.13861386138613863
    # 覆盖率: 0.37749546279491836
    # 新颖度: 1.2455207410149916

    # evaluate.precision(train, test, lfm_recommend)
    # evaluate.coverage(train, test, lfm_recommend)
    # evaluate.popularity(train, test, lfm_recommend)

    # recommendation = {}

    return icf_recommend, ucf_recommend, lfm_recommend


if __name__ == '__main__':
    learning()
