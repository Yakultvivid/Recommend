import numpy as np
import cv2


# 感知哈希算法
def p_hash(image):
    image = cv2.resize(image, (32, 32), interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dct = cv2.dct(np.float32(image))
    dct_roi = dct[0:8, 0:8]
    avreage = np.mean(dct_roi)
    hash_l = []
    for i in range(dct_roi.shape[0]):
        for j in range(dct_roi.shape[1]):
            if dct_roi[i, j] > avreage:
                hash_l.append(1)
            else:
                hash_l.append(0)
    return hash_l


# 均值哈希算法
def a_hash(image):
    # 缩放为8*8
    image = cv2.resize(image, (8, 8), interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    avreage = np.mean(image)
    hash_l = []
    for i in range(image.shape[0]):
        for j in range(image.shape[1]):
            if image[i, j] > avreage:
                hash_l.append(1)
            else:
                hash_l.append(0)
    return hash_l


# 差值感知算法
def d_hash(image):
    # 缩放9*8
    image = cv2.resize(image, (9, 8), interpolation=cv2.INTER_CUBIC)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hash_l = []
    # 每行前一个像素大于后一个像素为1，相反为0，生成哈希
    for i in range(8):
        for j in range(8):
            if image[i, j] > image[i, j+1]:
                hash_l.append(1)
            else:
                hash_l.append(0)
    return hash_l


# 计算汉明距离
def hamming_distance(hash_1, hash_2):
    num = 0
    for index in range(len(hash_1)):
        if hash_1[index] != hash_2[index]:
            num += 1
    return num


if __name__ == "__main__":
    image_file1 = './images/390.jpg'
    image_file2 = './images/5.jpg'
    img1 = cv2.imread(image_file1)
    img2 = cv2.imread(image_file2)

    hash1 = p_hash(img1)
    hash2 = p_hash(img2)
    dist = hamming_distance(hash1, hash2)
    # 将距离转化为相似度
    similarity = 1 - dist * 1.0 / 64
    print("感知哈希算法: ", similarity)

    hash1 = a_hash(img1)
    hash2 = a_hash(img2)
    dist = hamming_distance(hash1, hash2)
    # 将距离转化为相似度
    similarity = 1 - dist * 1.0 / 64
    print("均值哈希算法: ", similarity)

    hash1 = d_hash(img1)
    hash2 = d_hash(img2)
    dist = hamming_distance(hash1, hash2)
    # 将距离转化为相似度
    similarity = 1 - dist * 1.0 / 64
    print("差值感知算法: ", similarity)
