import pandas as pd
import re
import os
import sklearn
import lightgbm as lgb
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from .mymodule import detect_encoding, get_race_entry, get_race_outcome
from django.conf import settings

# エンコーダーを定義
def label_encode(df, columns):
    # 各カラムごとにエンコーダーを適用
    for column in columns:
        if column not in df.columns:
            print(f"列 '{column}' がデータフレームに存在しません")
            continue
        le = sklearn.preprocessing.LabelEncoder()
        # df[column] を基にラベルを学習し、変換を行う
        df[column] = le.fit_transform(df[column])
    return df

def calculate_std(value, mean, std):
    if pd.isnull(std) or std == 0:
        return 50  # 標準偏差が0の場合は平均値に設定
    return 50 + (10 * (value - mean) / std)

# 各種マッピング辞書
place_code = {
    '桐生': 1, '戸田': 2, '江戸川': 3, '平和島': 4, '多摩川': 5, '浜名湖': 6,
    '蒲郡': 7, '常滑': 8, '津': 9, '三国': 10, 'びわこ': 11, '住之江': 12,
    '尼崎': 13, '鳴門': 14, '丸亀': 15, '児島': 16, '宮島': 17, '徳山': 18,
    '下関': 19, '若松': 20, '芦屋': 21, '福岡': 22, '唐津': 23, '大村': 24
}
from_mapping = {
    '群馬': 1, '埼玉': 2, '東京': 3, '静岡': 4, '愛知': 5, '三重': 6,
    '富山': 7, '滋賀': 8, '大阪': 9, '兵庫': 10, '徳島': 11, '香川': 12,
    '岡山': 13, '広島': 17, '山口': 18, '福岡': 19, '佐賀': 20, '長崎': 21
}
class_mapping = {'B2': 1, 'B1': 2, 'A2': 3, 'A1': 4}

import os

folder_path = os.path.join(settings.BASE_DIR, 'backend', 'ml_models', 'data', 'input')
files = os.listdir(folder_path)

data_B_list = []
data_K_list = []

for file_name in files:
    if re.match(r'^B\d{6}\.TXT$', file_name):
        file_path = os.path.join(folder_path, file_name)
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            data_B_list.append(get_race_entry(file))

    if re.match(r'^K\d{6}\.TXT$', file_name):
        file_path = os.path.join(folder_path, file_name)
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            data_K_list.append(get_race_outcome(file))

# データフレームを結合
data_B_df = pd.concat(data_B_list, ignore_index=True)
data_K_df = pd.concat(data_K_list, ignore_index=True)
data_general = pd.merge(data_B_df, data_K_df, on=['選手登番', 'レースID'], how='left')


# 偏差値に変える列名をリストで宣言
list_std = ['全国勝率', '全国2連率', '当地勝率', '当地2連率', 'モーター2連率', 'ボート2連率']
for col in list_std:
    group_means = data_general.groupby('レースID')[col].transform('mean')
    group_stds = data_general.groupby('レースID')[col].transform('std')
    data_general[col] = data_general.apply(
        lambda x: calculate_std(x[col], group_means[x.name], group_stds[x.name]), axis=1
    )

# data_general と race_df にマッピングを適用
data_general['級別'] = data_general['級別'].map(class_mapping)
data_general['会場'] = data_general['会場'].map(place_code)
data_general['支部'] = data_general['支部'].map(from_mapping)
# 必要なカラムを一度にエンコード
label_columns = ['選手名', '支部', '天候', '風向']
label_encode(data_general, label_columns)

def map_target(row):
    if row['着'] in [1, 2]:
        return 0
    elif row['着'] in [3, 4]:
        return 1
    else:
        return 2

data_general['target'] = data_general.apply(map_target, axis=1)

# 特徴量と目的変数
X = data_general.drop(columns=['target', '着', '選手名', 'レースID'])
y = data_general['target']

# データ分割
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# nfoldをサンプル数以下に調整
nfold = min(5, len(X_train))

# LightGBM用データセット
train_data = lgb.Dataset(X_train, label=y_train)
test_data = lgb.Dataset(X_test, label=y_test)

# パラメータ設定
params = {
    'objective': 'multiclass',
    'num_class': 3,
    'metric': 'multi_logloss',
    'boosting_type': 'gbdt',
    'learning_rate': 0.1,
    'num_leaves': 31,
    'max_depth': -1,
    'verbosity': -1,
    'seed': 42
}

# クロスバリデーション
cv_results = lgb.cv(
    params,
    train_data,
    num_boost_round=100,
    nfold=nfold,
    stratified=True,
    metrics='multi_logloss',
    seed=42,
    callbacks=[lgb.early_stopping(stopping_rounds=10)]
)

# 最良の反復回数
best_iteration = np.argmin(cv_results['valid multi_logloss-mean']) + 1


# 最終モデル訓練
model = lgb.train(params, train_data, num_boost_round=best_iteration)

# 予測
y_pred = model.predict(X_test, num_iteration=model.best_iteration)
y_pred_max = np.argmax(y_pred, axis=1)

# モデル評価
accuracy = accuracy_score(y_test, y_pred_max)
print(f'Accuracy: {accuracy:.4f}')
print(classification_report(y_test, y_pred_max))