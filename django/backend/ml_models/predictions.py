from .create_model import model, label_encode, calculate_std, list_std, place_code, class_mapping, from_mapping
from .mymodule import get_race_entry
from django.conf import settings
import os
import numpy as np

def process_and_predict(file_path):
    # アップロードされたファイルを読み込み、処理
    with open(file_path, 'r', encoding='shift_jis') as file:
        race_entry_df = get_race_entry(file)

    # トレーニング時と同じ前処理を適用
    # 偏差値の計算
    for col in list_std:
        mean = race_entry_df[col].mean()
        std = race_entry_df[col].std()
        race_entry_df[col] = race_entry_df[col].apply(lambda x: calculate_std(x, mean, std))

    # ラベルエンコード
    label_columns = ['選手名', '支部', '天候', '風向']
    label_encode(race_entry_df, label_columns)

    # カテゴリカルデータのマッピング
    race_entry_df['級別'] = race_entry_df['級別'].map(class_mapping)
    race_entry_df['会場'] = race_entry_df['会場'].map(place_code)
    race_entry_df['支部'] = race_entry_df['支部'].map(from_mapping)

    # 予測用の特徴量を準備
    trained_features = model.feature_name()
    for col in trained_features:
        if col not in race_entry_df.columns:
            race_entry_df[col] = 0  # 欠損しているカラムを追加

    X_pred = race_entry_df[trained_features]

    # 予測を実行
    pred_probs = model.predict(X_pred, num_iteration=model.best_iteration)
    # 各選手の予測クラス（argmax）を取得し、解釈用に保持
    pred_classes = np.argmax(pred_probs, axis=1)
    race_entry_df['pred_class'] = pred_classes
    # 1着になる確率（クラス0の確率）を勝率として使用
    race_entry_df['win_prob'] = pred_probs[:, 0]

    predictions = []
    # レースIDごとにグループ化して、各レース内で順位付けを行う
    for race_id, group in race_entry_df.groupby('レースID'):
        # 勝率の高い順にソート
        sorted_group = group.sort_values(by='win_prob', ascending=False)
        
        # レースIDから会場コードとレース番号を取得
        race_id_str = str(race_id)
        place_code_num = int(race_id_str[8:10])  # 9番目と10番目の数字を取得
        race_number = int(race_id_str[10:12])      # 11番目と12番目の数字を取得
        venue = [key for key, value in place_code.items() if value == place_code_num][0]

        # 並べ替えた順に順位（1～6）を付与し、interpret_prediction() で解釈を追加
        for rank, (_, row) in enumerate(sorted_group.iterrows(), start=1):
            predictions.append({
                'venue': venue,
                'race_number': race_number,
                'boat_number': row['艇番'],
                'player_number': row['選手登番'],
                'rank': rank,  # 1～6の順位
                'interpretation': interpret_prediction(row['pred_class'])
            })

    # 出力先ファイルのパス
    output_path = os.path.join(settings.BASE_DIR, 'backend', 'ml_models', 'data', 'output', 'predictions.txt')
    
    # 結果をテキストファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        for prediction in predictions:
            f.write(
                f"Player Number: {prediction['player_number']}, Venue: {prediction['venue']}, "
                f"Race Number: {prediction['race_number']}, Rank: {prediction['rank']}, "
                f"Interpretation: {prediction['interpretation']}\n"
            )

    return predictions

def interpret_prediction(pred):
    if pred == 0:
        return '1~2着'
    elif pred == 1:
        return '3~4着'
    else:
        return '5~6着'
