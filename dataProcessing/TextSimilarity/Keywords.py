import jieba.analyse

import config

# 字符串前面加u表示使用unicode编码
# content = u"生活必备好物～满满的幸福感"

# 第一个参数：待提取关键词的文本

# withWeight：是否同时返回每个关键词的权重
# allowPOS：词性过滤，为空表示不过滤，若提供则仅返回符合词性要求的关键词


def content2words(content):
    # jieba.load_userdict(config.DATA_PATH.format(r"TextSimilarity\dict"))
    jieba.analyse.set_stop_words(config.DATA_PATH.format(r"TextSimilarity\stopwords"))
    # 词典格式和dict.txt一样，一个词占一行；每一行分三部分，一部分为词语，另一部分为词频，最后为词性（可省略），用空格隔开
    keywords = jieba.analyse.extract_tags(content, allowPOS=())
    res = str()
    for string in keywords[:3]:
        res += string + "|"
    return res


def stopwords_list(file_path):
    stopwords = [line.strip() for line in open(file_path, 'r', encoding='utf-8').readlines()]
    return stopwords


def content2keywords(content):
    # ('ns', 'n', 'vn', 'v') 地名、名词、动名词、动词、形容词
    # jieba.load_userdict(config.DATA_PATH.format("TextSimilarity\dict"))
    # 词典格式和dict.txt一样，一个词占一行；每一行分三部分，一部分为词语，另一部分为词频，最后为词性（可省略），用空格隔开
    keywords = jieba.analyse.textrank(content,  allowPOS=('ns', 'n', 'vn', 'v', "a"))
    res = str()
    for string in keywords[:3]:
        res += string + "|"
    return res

# print(content2words("雪糕"))
# print(content2keywords("雪糕"))
