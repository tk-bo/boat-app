import pandas as pd
import re
import os
import numpy as np
import matplotlib.pyplot as plt
from .mymodule import detect_encoding, get_race_entry
from .create_model import calculate_std, label_encode, model, list_std, place_code, class_mapping, from_mapping
from django.conf import settings

# フォルダのパスを指定
folder_path = os.path.join(settings.BASE_DIR, 'backend', 'ml_models', 'data', 'input')
output_path = os.path.join(settings.BASE_DIR, 'backend', 'ml_models', 'data', 'output')
files = os.listdir(folder_path)

# ファイル処理
data_B_list = []

for file_name in files:
    if re.match(r'^B\d{6}.TXT$', file_name):
        file_path = os.path.join(folder_path, file_name)
        encoding = detect_encoding(file_path)
        with open(file_path, 'r', encoding=encoding) as file:
            data_B_list.append(get_race_entry(file))

# データフレームを結合
race_df = pd.concat(data_B_list, ignore_index=True)

# 各レースIDごとの偏差値計算
for col in list_std:
    group_means = race_df.groupby('レースID')[col].transform('mean')
    group_stds = race_df.groupby('レースID')[col].transform('std')

    race_df[col] = race_df.apply(
        lambda x: calculate_std(x[col], group_means[x.name], group_stds[x.name]), axis=1
    )

# 必要なカラムを一度にエンコード
label_columns = ['選手名', '支部', '天候', '風向']
label_encode(race_df, label_columns)

# 数値変換
numeric_columns = ['艇番', '選手登番', '年齢', '体重', '会場', '級別', '支部']
for col in numeric_columns:
    race_df[col] = pd.to_numeric(race_df[col], errors='coerce')

# 欠損値を0で埋める
race_df.fillna(0, inplace=True)

# マッピングを適用
race_df['会場'] = race_df['会場'].map(place_code)
race_df['級別'] = race_df['級別'].map(class_mapping)
race_df['支部'] = race_df['支部'].map(from_mapping)

# 偏差値変換
for col in list_std:
    mean = race_df[col].mean()
    std = race_df[col].std()
    race_df[col] = race_df[col].apply(lambda x: 50 if std == 0 else (x - mean) * 10 / std + 50)

# 特徴量不足に対応
# モデルの訓練時の特徴量を取得
trained_features = model.feature_name()

# 不足カラムをrace_dfに追加
for col in trained_features:
    if col not in race_df.columns:
        race_df[col] = 0  # 適切なデフォルト値を使用

# 特徴量を訓練時の順番に揃える
X_pred = race_df[trained_features]

# 予測
pred_probs = model.predict(X_pred, num_iteration=model.best_iteration)

# 最も確率の高いクラスを取得
pred_classes = np.argmax(pred_probs, axis=1)

# 結果を保存
output_file_path = os.path.join(output_path, 'prediction_results.txt')
with open(output_file_path, 'w', encoding='utf-8') as f:
    for idx, pred in enumerate(pred_classes):
        race_id = race_df.iloc[idx]['レースID']
        boat_number = race_df.iloc[idx]['艇番']
        player_number = race_df.iloc[idx]['選手登番']
        result = f"{race_id}, 艇番: {boat_number}, 選手登番: {player_number}, 予測着順: {pred} (0:12着, 1:34着, 2:5~6着)\n"
        f.write(result)

# 特徴量の重要度を取得
importance = model.feature_importance(importance_type='gain')  # 'gain'は情報利得ベースの重要度
feature_names = model.feature_name()

# データフレーム化
importance_df = pd.DataFrame({'Feature': feature_names, 'Importance': importance})

# 重要度の高い順にソート
importance_df = importance_df.sort_values(by='Importance', ascending=False)

# 表示
print(importance_df)

# 特徴量の重要度を保存
importance_file_path = os.path.join(output_path, 'feature_importance.txt')
importance_df.to_csv(importance_file_path, index=False, sep='\t', encoding='utf-8')

# 可視化（グラフ）
plt.figure(figsize=(10, 6))
plt.barh(importance_df['Feature'], importance_df['Importance'])
plt.xlabel("Feature Importance (Gain)")
plt.ylabel("Feature")
plt.title("Feature Importance")
plt.gca().invert_yaxis()  # 上から重要な順に並べる
plt.show()

# DJANGO_SETTINGS_MODULE=backend.settings python -m backend.ml_models.inspection
