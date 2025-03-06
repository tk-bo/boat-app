import pandas as pd
import re
import chardet

def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def convert_zen_to_han(text):
    # 全角数字を半角に変換
    zen_to_han_map = str.maketrans("０１２３４５６７８９", "0123456789")
    return text.translate(zen_to_han_map)

def get_race_entry(file):
    lines = file.readlines()
    race_date = race_place = None
    data_B = []  # データ保存用リスト

    for line in lines:
        # 場所と日程、レース番号の抽出
        match = re.search(
            r'(?P<place>\d{2})BBGN|'
            r'(?P<year>\d{4})年\s*(?P<month>\d{1,2})月\s*(?P<day>\d{1,2})日|'
            r'(?P<race_num>\d{1,2})Ｒ',
            line
        )

        if match:
            if match.group('place'):
                race_place = match.group('place')
            if match.group('year'):
                race_date = (
                    convert_zen_to_han(match.group('year')) +
                    convert_zen_to_han(match.group('month')).zfill(2) +
                    convert_zen_to_han(match.group('day')).zfill(2)
                )
            if match.group('race_num'):
                race_num = convert_zen_to_han(match.group('race_num')).zfill(2)
                race_id = f"{race_date}{race_place}{race_num}"

        # 出場選手データを抽出
        match_data = re.search(
            r'(\d{1})\s+(\d{4})([^\d]+)(\d{2})([^\d]+)(\d{2})([A-Z]+\d*)\s+'
            r'(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\s+(\d{1,2}\.\d{2})\s+'
            r'(\d{1,2})\s+(\d{1,2}\.\d{2})\s+(\d{1,2})\s+(\d{1,2}\.\d{2})',
            line
        )

        if match_data and race_place and race_id:
            data_B.append([
                int(match_data.group(1)),    # 艇番
                int(match_data.group(2)),    # 選手登番
                match_data.group(3).strip().replace('\u3000', ''),  # 選手名
                int(match_data.group(4)),    # 年齢
                match_data.group(5).strip(), # 支部
                int(match_data.group(6)),    # 体重
                match_data.group(7),         # 級別
                float(match_data.group(8)),  # 全国勝率
                float(match_data.group(9)),  # 全国2連率
                float(match_data.group(10)), # 当地勝率
                float(match_data.group(11)), # 当地2連率
                float(match_data.group(13)), # モーター2連率
                float(match_data.group(15)), # ボート2連率
                race_place,
                race_id
            ])

    # 一括で DataFrame に変換
    return pd.DataFrame(data_B, columns=[
        '艇番', '選手登番', '選手名', '年齢', '支部', '体重', '級別', '全国勝率',
        '全国2連率', '当地勝率', '当地2連率', 'モーター2連率', 'ボート2連率', '会場', 'レースID'
    ])

def get_race_outcome(file):
    lines = file.readlines()
    race_date = race_place = weather = wind_dir = None
    wind_vol = wave = 0
    data_K = []  # データ保存用リスト

    # 1行ずつ処理
    for line in lines:
        # レース情報を抽出
        match = re.search(
            r'(?P<place>\d{2})KBGN|'
            r'(?P<year>\d{4})/\s*(?P<month>\d{1,2})/\s*(?P<day>\d{1,2})|'
            r'(?P<race_num>\d{1,2})R',
            line
        )

        # レース日・場所・IDを取得
        if match:
            if match.group('place'):
                race_place = match.group('place')
            if match.group('year'):
                race_date = (
                    convert_zen_to_han(match.group('year')) +
                    convert_zen_to_han(match.group('month')).zfill(2) +
                    convert_zen_to_han(match.group('day')).zfill(2)
                )
            if match.group('race_num'):
                race_num = convert_zen_to_han(match.group('race_num')).zfill(2)
                race_id = f"{race_date}{race_place}{race_num}"

        # 天候・風向・波の抽出
        race_info_pattern = re.compile(
            r"(\d+R)\s+.*?H(\d+)m\s+(\S+)\s+風\s+(\S+)\s+(\d+)m\s+波\s+(\d+)cm"
        )
        weather_match = race_info_pattern.search(line)
        if weather_match:
            race_num = weather_match.group(1)
            weather = weather_match.group(3)
            wind_dir = weather_match.group(4)
            wind_vol = int(weather_match.group(5))
            wave = int(weather_match.group(6))

        # 出場選手データを抽出
        match_data = re.search(
            r'(\d{1,2})\s+(\d)\s+(\d{4})\s+([\u3000-\u9FFF\s]+)\s+(\d+)\s+(\d+)\s+(\d+\.\d+)\s+(\d+)\s+([-+]?\d+\.\d+)\s+([\d.]+)',
            line
        )

        if match_data and race_place and race_id:
            data_K.append([
                int(match_data.group(1)),    # 着順
                int(match_data.group(3)),    # 登録番号
                float(match_data.group(7)),  # 展示タイム
                weather,                     # 天候
                wind_dir,                    # 風向
                int(wind_vol),               # 風量
                int(wave),                   # 波
                race_id                      # レースID
            ])

    # DataFrame に変換
    return pd.DataFrame(data_K, columns=[
        '着', '選手登番', '展示タイム', '天候', '風向', '風量', '波', 'レースID'
    ])

