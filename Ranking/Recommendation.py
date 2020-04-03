import pandas as pd
from sklearn.model_selection import train_test_split

import config


video_profile = pd.read_csv(config.DATA_PATH.format(r"data\video_profile"))
user_profile = pd.read_csv(config.DATA_PATH.format(r"data\user_profile"))
rating = pd.read_csv(config.DATA_PATH.format(r"data\rating"))

df = rating.merge(user_profile, on="user_id", how="outer").merge(video_profile, on="video_id", how="outer")
# print(df.columns.values.tolist())
# ['user_id', 'video_id', 'rating', 'gender', 'age', 'birthday', 'city', 'labels', 'video_user', 'des_keywords',
#  'time_factor', 'hot_number', 'circle_id', 'cat_second', 'video_label', 'cat']

data = df[['gender', 'age', 'constellation', 'city', 'labels', 'video_user', 'des_keywords',  'time_factor', 'hot_number',
           'circle_id', 'cat_second', 'video_label', 'cat', "rating"]]
X = data[['gender', 'age', 'constellation', 'city', 'labels', 'video_user', 'des_keywords',  'time_factor', 'hot_number',
          'circle_id', 'cat_second', 'video_label', 'cat']]
Y = data["rating"]
# X_train, X_test, Y_train, Y_test = train_test_split(X, Y)
df.to_csv("./data", index=None)
