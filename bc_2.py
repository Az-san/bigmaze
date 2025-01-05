#############################################################################################
#  2024/12/23 作成
# 1. "epoch_summary"ディレクトリを指定して、エポックごとの脳波データを読み取る
# 2. エポックデータのベースライン補正を行う
#    - 各エポックの第2行目から第1001行目までの平均を計算し、それを基準値（ベースライン値）とする
#    - 計算したベースライン値を全データから減算して補正する
# 3. 補正後のエポックデータを新しいCSVファイルとして保存する
#    - 保存形式は"{電極名}_epoch_corrected.csv"
# 4. 補正後のデータを用いてエポックごとの波形プロットを作成し、PNGファイルとして保存する
#    - プロットにはTTL信号の絶対時刻を表示し、補正後の振幅データ(補正前と同じく-17~17μV)を描画する
#    - プロットの保存先は電極ごとに電極名のサブディレクトリを「ベースライン補正後のデータを保存するディレクトリ」下に作成
# 5. すべての電極について補正値（ベースライン値）をまとめたCSVファイルを保存する
#    - 保存形式は"baseline_values.csv"
#############################################################################################


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from tkinter import Tk
from tkinter.filedialog import askdirectory

# GUIを使ったディレクトリ選択関数
def select_directory(prompt):
    print(prompt)  # ユーザーに選択を促すメッセージを表示
    Tk().withdraw()  # GUIウィンドウを非表示
    directory = askdirectory()  # ディレクトリ選択ダイアログを表示
    return directory

# epoch_summaryディレクトリのパスをユーザーに選択させる
input_dir = select_directory("epoch_summaryディレクトリを選択してください。")

# 保存先ディレクトリ
output_dir = select_directory("ベースライン補正後のデータを保存するディレクトリを選択してください。")
os.makedirs(output_dir, exist_ok=True)

# ベースライン補正値を記録するリスト
baseline_values = []

# epoch_summaryディレクトリ内のCSVファイルを取得
csv_files = [f for f in os.listdir(input_dir) if f.endswith("_epoch_summary.csv")]

for file_name in csv_files:
    file_path = os.path.join(input_dir, file_name)

    # CSVファイルをロード
    data = pd.read_csv(file_path)

    # カラム名を修正 (Epoch 1, Epoch 2, ... -> 1, 2, ...)
    new_columns = [str(i + 1) if col.startswith("Epoch") else col for i, col in enumerate(data.columns)]
    data.columns = new_columns

    # 各エポックの2行目から1001行目（0インデックスでは1から1000）の平均を計算
    epoch_means = data.iloc[1:1001, :].mean()

    # エポックごとの平均値を加算して、全体の平均を計算
    baseline_correction_value = epoch_means.mean()

    # ベースライン補正値を記録
    electrode_name = file_name.replace("_epoch_summary.csv", "")
    baseline_values.append({"Electrode": electrode_name, "Baseline Value": baseline_correction_value})

    print(f"{file_name} のベースライン補正値: {baseline_correction_value}")

    # ベースライン補正を実施
    baseline_corrected_data = data - baseline_correction_value

    # 補正後のデータを新しいCSVファイルに保存
    output_file_path = os.path.join(output_dir, file_name.replace("_epoch_summary", "_epoch_corrected"))

    # インデックスをエポック番号として設定 (1, 2, 3, ...)
    baseline_corrected_data.index = range(1, len(baseline_corrected_data) + 1)
    baseline_corrected_data.to_csv(output_file_path, index_label="Epoch", encoding='utf-8-sig')

    print(f"{file_name} のベースライン補正後のデータを保存しました: {output_file_path}")


    # プロット保存用ディレクトリを電極ごとに作成
    electrode_plot_dir = os.path.join(output_dir, electrode_name)
    os.makedirs(electrode_plot_dir, exist_ok=True)

    # 元データディレクトリから対応するエポックデータを参照
    epoch_data_dir = os.path.join(input_dir.replace("epoch_summary", f"epoch_data_{electrode_name}"))

    # 各エポックのプロットを作成して保存
    for col_idx, col in enumerate(baseline_corrected_data.columns, start=1):
        epoch_file_path = os.path.join(epoch_data_dir, f"epoch_{col_idx}_{electrode_name}.csv")

        if not os.path.exists(epoch_file_path):
            print(f"対応するエポックファイルが見つかりません: {epoch_file_path}")
            continue

        epoch_original_data = pd.read_csv(epoch_file_path)
        ttl_time = epoch_original_data.iloc[0, 0]  # TTLの絶対時刻を取得

        plt.figure(figsize=(10, 5))

        # TTLの絶対時刻を基準にした時間軸を計算
        x_values = np.linspace(ttl_time - 1.0, ttl_time + 2.0, len(baseline_corrected_data))

        plt.plot(x_values, baseline_corrected_data[col], label=f"Epoch {col_idx}")
        plt.axvline(x=ttl_time - 1.0, color='blue', linestyle='--', label='Epoch Start')
        plt.axvline(x=ttl_time, color='red', linestyle='--', label='TTL Signal')
        plt.axvline(x=ttl_time + 2.0, color='green', linestyle='--', label='Epoch End')

        plt.title(f"Electrode: {electrode_name} | Baseline Corrected Epoch {col_idx}")
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude [µV]")
        plt.xticks(np.arange(ttl_time - 1.0, ttl_time + 2.1, 0.5), [f"{x:.3f}" for x in np.arange(ttl_time - 1.0, ttl_time + 2.1, 0.5)])
        plt.yticks(np.arange(-17, 18, 5))  # -17から17までに変更
        plt.grid(True, which='both', linestyle='--', linewidth=0.5)

        # 縦軸の細かい罫線を追加
        plt.minorticks_on()
        plt.grid(True, which='minor', axis='y', linestyle=':', linewidth=0.5)

        plt.legend()

        # プロット保存
        plot_file_path = os.path.join(electrode_plot_dir, f"{electrode_name}_epoch_{col_idx}_bc.png")
        plt.savefig(plot_file_path, dpi=300)
        plt.close()

        print(f"プロットを保存しました: {plot_file_path}")

# ベースライン補正値をCSVファイルに保存
baseline_values_df = pd.DataFrame(baseline_values)
baseline_values_file_path = os.path.join(output_dir, "baseline_values.csv")
baseline_values_df.to_csv(baseline_values_file_path, index=False, encoding='utf-8-sig')

print(f"ベースライン補正値を保存しました: {baseline_values_file_path}")
