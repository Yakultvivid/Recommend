import random


def load_file(filename):

    with open(filename, 'r') as f:
        for i, line in enumerate(f):
            if i == 0:  # 去掉文件第一行的title
                continue
            yield line.strip('\r\n')
    print('Load %s success!' % filename)


def train_test_split(filename, pivot=0.75):
    # 切分训练、测试集
    train = {}
    test = {}
    train_len = 0
    test_len = 0
    for line in load_file(filename):
        user, goods, rating = line.split(',')
        if random.random() < pivot:
            train.setdefault(user, {})
            train[user][goods] = rating
            train_len += 1
        else:
            test.setdefault(user, {})
            test[user][goods] = rating
            test_len += 1
    print('Split trainingSet and testSet success!')
    print('TrainSet = %s' % train_len)
    print('TestSet = %s' % test_len)
    return train, test

                       
def get_train_data(filename):
    # 获取训练数据
    train = {}
    train_len = 0
    for line in load_file(filename):
        user, goods, rating = line.split(',')
        train.setdefault(user, {})
        train[user][goods] = rating
        train_len += 1
    print('Split trainingSet and testSet success!')
    print('TrainSet = %s' % train_len)
    return train
