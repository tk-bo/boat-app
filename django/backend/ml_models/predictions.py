from .create_model import model, label_encode, calculate_std, list_std, place_code, class_mapping, from_mapping
from .mymodule import get_race_entry
from .create_model import model
from django.conf import settings
import os

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
    pred_classes = pred_probs.argmax(axis=1)

    # 結果を整形
    predictions = []
    for idx, pred in enumerate(pred_classes):
        race_id = race_entry_df.iloc[idx]['レースID']
        boat_number = race_entry_df.iloc[idx]['艇番']
        player_number = race_entry_df.iloc[idx]['選手登番']

        # 9番目と10番目の数字を抽出して会場を決定
        race_id_str = str(race_id)
        place_code_num = int(race_id_str[8:10])  # 9番目と10番目の数字を取得
        # 11番目と12番目の数字でレース番号を取得
        race_number = int(race_id_str[10:12])  # 11番目と12番目の数字を取得
        
        # 会場名をplace_codeから取得
        venue = [key for key, value in place_code.items() if value == place_code_num][0]  # place_code_numに対応する会場名

        predictions.append({
            'venue': venue,  # 会場を追加
            'race_number': race_number,  # レース番号を追加
            'boat_number': boat_number,
            'player_number': player_number,
            'interpretation': interpret_prediction(pred)
        })

    # 出力先ファイルのパス
    output_path = os.path.join(settings.BASE_DIR, 'backend', 'ml_models', 'data', 'output', 'predictions.txt')
    
    # 結果をテキストファイルに書き込み
    with open(output_path, 'w', encoding='utf-8') as f:
        for prediction in predictions:
            player_number = prediction['player_number']
            venue = prediction['venue']
            race_number = prediction['race_number']
            interpretation = prediction['interpretation']
            f.write(f"Player Number: {player_number}, Venue: {venue}, Race Number: {race_number}, Interpretation: {interpretation}\n")

    return predictions

def interpret_prediction(pred):
    if pred == 0:
        return '1～2着'
    elif pred == 1:
        return '3～4着'
    else:
        return '5～6着'
