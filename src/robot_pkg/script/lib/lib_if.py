#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file libraspi
## @author Kentaro NAKAMURA
## @modified for hidapi by Maiko Kudo
## @brief ライブラリクラス
#==================================================

#==================================================
# import
#==================================================
import sys
import roslib
import hid  # hidapiをインポート
import time
import math
import rospy
from std_msgs.msg import String

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================

#==================================================
## @class LibIF
## @brief 自作ライブラリクラス
#==================================================
class LibIF:
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param 
    ## @return
    #==================================================
    def __init__(self):
        # メンバ変数
        self.pub_gui_state = rospy.Publisher(
            'gui_state', 
            String, 
            queue_size=1
        )

        self.pub_gui_state = rospy.Publisher('gui_state', String, queue_size=1)
        self.device_path = "/dev/hidraw0"  # hidrawデバイスパス

        # 十字ボタンのデータパターンをマッピング
        self.direction_mapping = {
            "0000": "Up",     # 上
            "0400": "Down",   # 下
            "0200": "Right",  # 右
            "0600": "Left"    # 左
        }
        
        self.right_direction_mapping = {
            "8800": "4",    # 右キー上
            "2800": "2",    # 右キー下
            "4800": "exit", # 右キー右（終了確認画面に遷移）
            "1800": "1"     # 右キー左
        }


        self.neutral_data = "0800"  # 押していない状態のデータ
        print("ゲームパッドの初期化完了")
        

    #==================================================
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def delete(self):
        if self.device:
            self.device.close()
        return

    #==================================================
    ## @fn waitGamepad
    ## @brief ゲームパッドの入力を待つ関数
    ## @param
    ## @return
    #==================================================
    def waitGamepad(self):
        # ゲームパッドのデータを待つ処理
        print("ゲームパッドからのデータを待っています...")

        try:
            with open(self.device_path, "rb") as hid_device:
                while True:
                    data = hid_device.read(8).hex()  # 8バイトのデータを16進数で読み取る
                    left_dpad_data = data[8:12]  # 左十字ボタンの該当データ位置

                    # 無入力状態（neutral_data）の場合はスキップ
                    if left_dpad_data == self.neutral_data:
                        continue

                    # 入力がある場合のみ方向を判定して結果を返す
                    if left_dpad_data in self.direction_mapping:
                        direction = self.direction_mapping[left_dpad_data]
                        print(f"Direction: {direction}")
                        # [上, 下, 右, 左]の配列形式で返す
                        if direction == "Up":
                            return [1, 0, 0, 0]
                        elif direction == "Down":
                            return [0, 1, 0, 0]
                        elif direction == "Right":
                            return [0, 0, 1, 0]
                        elif direction == "Left":
                            return [0, 0, 0, 1]

        except FileNotFoundError:
            print(f"Device {self.device_path} not found.")
        except PermissionError:
            print(f"Permission denied for device {self.device_path}. Try 'sudo chmod 666 {self.device_path}'")
        except Exception as e:
            print(f"An error occurred: {e}")
        return None




    #==================================================
    ## @fn changeGamepadInputUDRLtoNSEW
    ## @brief ゲームパッドで入力したロボットの進行方向を上下左右から東西南北にする関数
    ## @param direction_udrl 決定されたロボットの進行方向（上下左右）
    ## @param rad 地図座標系におけるロボットの現在角度
    ## @return direction_nsew 決定されたロボットの進行方向（東西南北）
    #==================================================
    def changeGamepadInputUDRLtoNSEW(self, direction_udrl, rad):
        rad_list_udrl = [0.0, math.pi, math.pi * 3/2, math.pi/2]
        rad_direction_udrl = rad_list_udrl[[i for i in range(len(direction_udrl)) if direction_udrl[i] == 1][0]]
        direction_nsew = [0, 0, 0, 0]
        if 0.70 < math.cos(rad_direction_udrl + rad):
            direction_nsew[0] = 1
        elif -0.70 > math.cos(rad_direction_udrl + rad):
            direction_nsew[1] = 1
        elif -0.70 > math.sin(rad_direction_udrl + rad):
            direction_nsew[2] = 1
        elif 0.70 < math.sin(rad_direction_udrl + rad):
            direction_nsew[3] = 1
        return direction_nsew

    #==================================================
    ## @fn changeGUI
    ## @brief GUIの描画を変化させる関数
    ## @param state = "start"   スタート時のGUI
    ## @param state = "move"    ロボット移動時のGUI
    ## @param state = "wait"    ロボット周辺の地図作成を待っている時のGUI
    ## @param state = "select"  被験者の進行方向選択を待っている時のGUI
    ## @param state = "error"   被験者の選択した進行方向が進行不能である時のGUI
    ## @param state = x,y,rad   GUI上のロボットの位置情報を更新する際のデータ
    ## @return
    #==================================================

    def changeGUI(self, state="start"):
        if state == "start":
            self.pub_gui_state.publish("start")
        elif state == "move":
            self.pub_gui_state.publish("move")
        elif state == "wait":
            self.pub_gui_state.publish("wait")
        elif state == "select":
            self.pub_gui_state.publish("select")
        elif state == "error":
            self.pub_gui_state.publish("error")
        elif state == "exit_comfirm":
            self.pub_gui_state.publish("exit_comfirm")
        else:
            state_str = [str(n) for n in state]
            self.pub_gui_state.publish(",".join(state_str))  # 座標値をコンマ区切りでPublish


# テスト用コード
if __name__ == "__main__":
    lib_if = LibIF()
    while True:
        direction = lib_if.waitGamepad()
        if direction:
            print(f"Detected direction: {direction}")