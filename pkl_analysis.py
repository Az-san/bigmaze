import os
import pickle
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askdirectory

# このプログラムのプロトコル:
# 1. 指定されたディレクトリ内のすべての.pklファイルを検索する。
# 2. 各.pklファイルの内容を.txt形式で保存する。
# 3. すべての.pklファイルの内容をCSV形式で統合して保存する。
# 4. Valueがリストの場合、列ごとに展開する。
# 5. 1列目の要素を削除し、2列目以降にエポック番号を追加する。

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)  # ユーザーに選択を促すメッセージを表示
    Tk().withdraw()  # GUIウィンドウを非表示
    directory = askdirectory()  # ディレクトリ選択ダイアログを表示
    return directory

# ログファイルが保存されているディレクトリを選択
input_dir = select_directory("ログデータが保存されているディレクトリを選択してください。")
output_dir = select_directory("解析結果を保存するディレクトリを選択してください。")
os.makedirs(output_dir, exist_ok=True)

# 指定ディレクトリ内のすべての.pklファイルを取得
pkl_files = [f for f in os.listdir(input_dir) if f.endswith('.pkl')]

# データをまとめるためのリスト
all_data = []

for pkl_file in pkl_files:
    pkl_path = os.path.join(input_dir, pkl_file)

    try:
        # .pklファイルを読み込み
        with open(pkl_path, 'rb') as file:
            data = pickle.load(file)

        # テキストファイルとして保存
        txt_file_path = os.path.join(output_dir, pkl_file.replace('.pkl', '.txt'))
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(str(data))
        print(f"{pkl_file} の内容をテキストファイルに保存しました: {txt_file_path}")

        # データをリスト形式に統一して追加
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, list):
                    for idx, item in enumerate(value):
                        all_data.append({"FileName": pkl_file, "Key": key, "Epoch": idx + 1, "Value": item})
                else:
                    all_data.append({"FileName": pkl_file, "Key": key, "Epoch": 1, "Value": value})
        elif isinstance(data, list):
            for idx, item in enumerate(data):
                all_data.append({"FileName": pkl_file, "Key": "Data", "Epoch": idx + 1, "Value": item})
        else:
            all_data.append({"FileName": pkl_file, "Key": "Data", "Epoch": 1, "Value": data})

        print(f"{pkl_file} の内容を処理しました。")

    except Exception as e:
        print(f"{pkl_file} の読み込み中にエラーが発生しました: {e}")

# データをDataFrameに変換
if all_data:
    df = pd.DataFrame(all_data)

    # Valueがリストの場合、列に展開
    expanded_rows = []
    for _, row in df.iterrows():
        if isinstance(row['Value'], list):
            expanded_row = {"FileName": row['FileName'], "Key": row['Key'], "Epoch": row['Epoch']}
            for idx, val in enumerate(row['Value']):
                expanded_row[f"Value_{idx+1}"] = val
            expanded_rows.append(expanded_row)
        else:
            expanded_row = row.to_dict()
            expanded_rows.append(expanded_row)

    expanded_df = pd.DataFrame(expanded_rows)

    # 不要な1列目の要素を削除
    expanded_df = expanded_df[expanded_df['Epoch'] > 1]

    # ヘッダー名を調整
    expanded_df = expanded_df.rename(columns={"Value": "ErrP"})

    # CSV形式で保存
    csv_path = os.path.join(output_dir, "combined_data.csv")
    expanded_df.to_csv(csv_path, index=False, encoding='utf-8-sig')

    print(f"すべての.pklファイルの内容を {csv_path} に保存しました。")
else:
    print("処理するデータが見つかりませんでした。")
