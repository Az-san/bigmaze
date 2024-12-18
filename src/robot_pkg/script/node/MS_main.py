#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file sm_main.py
## @original author Kentaro NAKAMURA
## @author Takumi FUJI
## @brief メインステートマシン
#==================================================


#==================================================
# import
#==================================================
import sys
import roslib
import rospy
import os

import smach
#import smach_ros

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================
CheckIntersectionCLOCK = 0.5
ErrRate = 0 #エラー率を割合で表す(3割)
SocketActive = False
TTLActive = True

#==================================================
## @class Init
## @berif 初期化ステート
#==================================================
class Init(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        #ソケット通信確立
        if SocketActive:
            self._lib["com"].initSocket()
            
        #実験情報入力
        sub     = input("参加者番号を入力してください >>> ")
        exp_cnt = input("実験番号を入力してください >>> ")
        info    = input("備考を入力してください >>> ")
        MiniMap = rospy.get_param("/MiniMap", False)
        print(f"MiniMap Visible = {MiniMap}")
        self._lib["record"].updateInfo(sub, exp_cnt, info, MiniMap)
        return "next"




#==================================================
## @class Wait4Start
## @berif 開始待ちステート
#==================================================
class Wait4Start(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered Wait4Start state.")
        input("Enter to START >>> ")
        print("[DEBUG] Exiting Wait4Start state.")
        return "next"




#==================================================
## @class Start
## @brief 開始ステート
#==================================================
class Start(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "except"]
        )

        self._lib = lib

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        return "next"



#==================================================
## @class StartTrial
## @berif 
#==================================================
class StartTrial(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "restart", "loop", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================


        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        self._lib["record"].initPath(rospy.get_param("/exp_type", "")) # データ保存先の初期化
                
        self._lib["record"].saveInfo(ErrRate, SocketActive, TTLActive) # 実験情報のテキストファイル保存
        
        #スタート時点の地図の保存
        self._lib["record"].saveMap()

        # GUIの変更
        point_pixel = self._lib["map"].getRobotPointPixel()
        self._lib["if"].changeGUI(point_pixel)
        
        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", []) #進行可能方角
        rospy.set_param(rospy.get_name() + "/position_meter", []) #現在位置・角度
        rospy.set_param(rospy.get_name() + "/nearest_inf_rad_to_present_rad", 0.0) #正面に向けるための後進方向
        rospy.set_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", [-1,-1,-1,-1]) #進行可能方角とインデックス対応
        rospy.set_param(rospy.get_name() + "/direction_candidates_UDRL", [-1,-1,-1,-1]) #進行可能方向とインデックス対応
        rospy.set_param(rospy.get_name() + "/robot_decided_direction", []) #ロボットの決定方向
        rospy.set_param(rospy.get_name() + "/human_decided_direction", []) #人間の決定方向
        rospy.set_param(rospy.get_name() + "/pilot", []) #ロボットか人間か
        rospy.set_param(rospy.get_name() + "/decided_direction", []) #最終的に選んだ進行方向
        rospy.set_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0) #選んだ方向の角度値
        rospy.set_param(rospy.get_name() + "/nearest_x_table_idx", -1) #現在地と対応した交差点の番号
        rospy.set_param(rospy.get_name() + "/unexp_points_meter", []) #未探索進行可能位置情報
        rospy.set_param(rospy.get_name() + "/unexp_rad_sorted", []) #未探索進行可能方向情報
        rospy.set_param(rospy.get_name() + "/x_cnt", 0) #交差点通過回数
        rospy.set_param(rospy.get_name() + "/s_time", 0)

        print("###    EEG  experiment    ###")
        if rospy.get_param("/data_file", "") == "":
            rospy.set_param(rospy.get_name() + "/q_table", [])
            rospy.set_param(rospy.get_name() + "/x_table", [])
        else:
            save_date_path = roslib.packages.get_pkg_dir("robot_pkg") + "/data" + "/" + rospy.get_param("/data_file", "")
            q_table = self._lib["record"].loadRecordQTable(save_date_path)
            x_table = self._lib["record"].loadRecordXTable(save_date_path)
            rospy.set_param(rospy.get_name() + "/q_table", q_table)
            rospy.set_param(rospy.get_name() + "/x_table", x_table)
        
        rospy.sleep(1)
        # ストップウォッチを開始する
        self._lib["record"].recordTime(state="start")

        return "next"





#==================================================
## @class CheckIntersection
## @brief 
#==================================================
class CheckIntersection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["true", "false", "loop", "except"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered CheckIntersection state.")
        inf_rad_sorted = self._lib["scan"].getLaserInfRad()
        position_meter = self._lib["map"].getRobotPointMeter()

        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", inf_rad_sorted)

        # GUIの変更
        self._lib["if"].changeGUI("move")

        # 進行可能な空間がない場合
        if len(inf_rad_sorted) == 0:
            print("[DEBUG] No possible way found, looping.")
            rospy.loginfo("no passible way !!!(ChkInterS)")

            rospy.sleep(CheckIntersectionCLOCK)

            # かつ、ロボットが動いていない時は回避行動を行う（アドホック）
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                rospy.loginfo("escaping now ...(ChkInterS)")

                # ロボットを180deg回転させる
                self._lib["nav"].sendRotationTwist(position_meter[2] - math.pi, position_meter[2])
                # とにかく前進する
                self._lib["nav"].sendRunTwist(
                    position_meter[2],
                    position_meter[2],
                    rad_speed = 0.0
                )

            return "loop"

        # 交差点を見つけた場合
        elif 2 < len(inf_rad_sorted):
            print("[DEBUG] Intersection found")
            rospy.loginfo("Intersection found.")
            self._lib["nav"].sendRunTwist(
                inf_rad_sorted[0],
                position_meter[2],
                rad_speed = 0.0,
                target_time = 0.5
            )
            """rospy.sleep(0.5)
            # ロボットを停止させる
            self._lib["nav"].sendRunTwist(
                inf_rad_sorted[0],
                position_meter[2],
                lin_speed = 0,
                rad_speed = 0.0
            )"""
            #地図の保存とGUIの変更
            self._lib["record"].saveMap()
            point_pixel = self._lib["map"].getRobotPointPixel()
            self._lib["if"].changeGUI(point_pixel)
            rospy.sleep(0.5)
            inf_rad_sorted = self._lib["scan"].getLaserInfRad()
            position_meter = self._lib["map"].getRobotPointMeter()
            rospy.set_param(rospy.get_name() + "/inf_rad_sorted", inf_rad_sorted)
            # 現在のロボットの後進方向から一番近いinf_radを発見する
            nearest_inf_rad_to_present_rad = inf_rad_sorted[0] - math.pi
            for i in range(len(inf_rad_sorted)):
                if math.cos(inf_rad_sorted[i] - position_meter[2] - math.pi) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2] - math.pi):
                    nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
            #GUIの変更
            self._lib["if"].changeGUI("wait")        
            # ロボットを回転させる（正面を向かせる）*交差点の内側を向かせるように条件分岐
            if 0.70 < abs(math.cos(nearest_inf_rad_to_present_rad)):      # 南北
                self._lib["nav"].sendRotationTwist(math.pi - nearest_inf_rad_to_present_rad, position_meter[2])
            else:   # 東西
                self._lib["nav"].sendRotationTwist(- nearest_inf_rad_to_present_rad, position_meter[2])
            
            rospy.sleep(0.5)

            # 未探索領域の座標、方向を求める
            inf_rad_sorted = self._lib["scan"].getLaserInfRad()
            resolution = self._lib["map"].getResolution()
            point_pixel = self._lib["map"].getRobotPointPixel()
            inf_points_pixel = self._lib["scan"].getLaserInfPointPixel(inf_rad_sorted, point_pixel[0], point_pixel[1], resolution)
            map_out = self._lib["map"].getMap()
            unexp_points_pixel, unexp_rad_sorted = self._lib["map"].countUnexpPix(map_out, inf_points_pixel, inf_rad_sorted)
            unexp_points_meter = self._lib["map"].convPixels2Meters(unexp_points_pixel)
            if len(unexp_points_pixel) != 0:
                for i in range(len(unexp_points_meter)):
                    print("unexp_points_meter = {}, {}".format(unexp_points_meter[i][0], unexp_points_meter[i][1]))

            rospy.set_param(rospy.get_name() + "/unexp_points_meter", unexp_points_meter)
            rospy.set_param(rospy.get_name() + "/unexp_rad_sorted", unexp_rad_sorted)
            
            """map_tmp_img = self._lib["map"].getMapImg() #探索領域の地図画像表示
            for xy in inf_points_pixel:
                if xy[0]+9<map_tmp_img.shape[1] and xy[1]+9<map_tmp_img.shape[0]:
                    if xy in unexp_points_pixel:
                        cv2.rectangle(map_tmp_img,(xy[0]-9,xy[1]-9),(xy[0]+9,xy[1]+9),(0,255,255),thickness=1)
                    else:
                        cv2.rectangle(map_tmp_img,(xy[0]-9,xy[1]-9),(xy[0]+9,xy[1]+9),(0,255,0),thickness=1)    
            orig=self._lib["map"].getMapOriginPixel()
            cv2.circle(map_tmp_img,(point_pixel[0],point_pixel[1]),2,(0,0,255),thickness=-1)
            cv2.circle(map_tmp_img,(orig[0],orig[1]),2,(255,0,0),thickness=-1)
            map_tmp_img = cv2.resize(map_tmp_img,None,None,2.0,2.0)
            cv2.imshow('map',map_tmp_img)
            cv2.waitKey(2000)
            cv2.destroyAllWindows()"""

            return "true"

        # 進行可能な空間がある場合(交差点ではない場合)
        else:
            #rospy.loginfo("I will go straight.")
            print("[DEBUG] No intersection, proceefing straight.")
            return "false"




#==================================================
## @class GoAhead
## @berif 
#==================================================
class GoAhead(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered GoAhead state.")
        inf_rad_sorted = rospy.get_param(rospy.get_name() + "/inf_rad_sorted", [])

        position_meter = self._lib["map"].getRobotPointMeter()

        # 手前に壁がある場合、
        if self._lib["scan"].getAheadDistance() < 1.0:
            print("[DEBUG] Obstacle ahead, stopping and rotating.")
            
            # ロボットを停止させる
            self._lib["nav"].sendRunTwist(
                inf_rad_sorted[0],
                position_meter[2],
                lin_speed = 0,
                rad_speed = 0.01
            )

            rospy.sleep(0.5)

            # 現在のロボットの前進方向から一番近いinf_radを発見する
            nearest_inf_rad_to_present_rad = inf_rad_sorted[0]
            for i in range(len(inf_rad_sorted)):
                if math.cos(inf_rad_sorted[i] - position_meter[2]) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2]):
                    nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
            # ロボットを回転させる（位置調整のため）
            self._lib["nav"].sendRotationTwist(nearest_inf_rad_to_present_rad, position_meter[2])
            rospy.sleep(0.5)

        else:
            print("[DEBUG] Moving ahead.")
            
            # 両サイドの40cmに壁があるか確認。壁が近いならば離れる方向を指示
            proxi = self._lib["scan"].getSideProximity()
            if proxi != 0:
                nearest_inf_rad_to_present_rad = position_meter[2] + proxi
                print(f"proxi={proxi}")
            else:
            # 現在のロボットの前進方向から一番近いinf_radを発見する
                nearest_inf_rad_to_present_rad = inf_rad_sorted[0]
                for i in range(len(inf_rad_sorted)):
                    if math.cos(inf_rad_sorted[i] - position_meter[2]) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2]):
                        nearest_inf_rad_to_present_rad = inf_rad_sorted[i]

            # nearest_inf_rad_to_present_rad方向に前進する
            self._lib["nav"].sendRunTwist(
                nearest_inf_rad_to_present_rad,
                position_meter[2],
            )

            rospy.sleep(CheckIntersectionCLOCK)

            # ロボットが動いていない場合、トライアルをリセットする
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                """rospy.loginfo("escaping now ...(GoAhead)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="lap")
                self._lib["nav"].resetTrial()"""
                self._lib["nav"].sendRunTwist(
                0,
                0,
                lin_speed = -0.3,
                rad_speed = 0.0,
                target_time = 1.0)
                return "loop"
                

        return "next"



#==================================================
## @class MakeDirectionCandidates
## @berif 
#==================================================
class MakeDirectionCandidates(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "except","back"]
        )

        self._lib = lib


        #==================================================
        # ROSインタフェース
        #==================================================


        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered MakeHumanDecideDirection state.")
        
        inf_rad_sorted = self._lib["scan"].getLaserInfRad()
        position_meter = self._lib["map"].getRobotPointMeter()

        # もし、進行可能な空間がない場合、かつロボットが動いていない場合、トライアルをリセットする
        if len(inf_rad_sorted) == 0:
            robot_vel = self._lib["nav"].getRobotVel()
            if robot_vel < 0.001:
                rospy.loginfo("escaping now ...(MakeDirCan)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="lap")
                self._lib["nav"].resetTrial()

                return "reset"
        elif len(inf_rad_sorted) <= 2:

                return "back"

        # 交差点において進行可能な方角をリストアップする
        direction_candidates_inf_rad_sorted_idx = [-1,-1,-1,-1] # [北、南、東、西]
        for i in range(len(inf_rad_sorted)):
            if 0.70 < math.cos(inf_rad_sorted[i]):      # 北 
                direction_candidates_inf_rad_sorted_idx[0] = i
            elif -0.70 > math.cos(inf_rad_sorted[i]):   # 南
                direction_candidates_inf_rad_sorted_idx[1] = i
            elif -0.70 > math.sin(inf_rad_sorted[i]):   # 東
                direction_candidates_inf_rad_sorted_idx[2] = i
            elif 0.70 < math.sin(inf_rad_sorted[i]):    # 西
                direction_candidates_inf_rad_sorted_idx[3] = i

        #print("direction_candidates_inf_rad_sorted_idx = {}".format(direction_candidates_inf_rad_sorted_idx))
        
        # 交差点において進行可能な方向をリストアップする
        direction_candidates_UDRL= [-1,-1,-1,-1] # [上、下、右、左]
        for i in range(len(inf_rad_sorted)):
            if 0.70 < math.cos(inf_rad_sorted[i]-position_meter[2]):      # 上 
                direction_candidates_UDRL[0] = i
            elif -0.70 > math.cos(inf_rad_sorted[i]-position_meter[2]):   # 下
                direction_candidates_UDRL[1] = i
            elif -0.70 > math.sin(inf_rad_sorted[i]-position_meter[2]):   # 右
                direction_candidates_UDRL[2] = i
            elif 0.70 < math.sin(inf_rad_sorted[i]-position_meter[2]):    # 左
                direction_candidates_UDRL[3] = i

        print("direction_candidates_UDRL = {}".format(direction_candidates_UDRL))
        if direction_candidates_UDRL[3] != -1:
            if direction_candidates_UDRL[0] != -1:
                if direction_candidates_UDRL[2] != -1:
                    print("←↑→")
                else:
                    print("←↑")
            else:
                if direction_candidates_UDRL[2] != -1:
                    print("←→")
                else:
                    print("????????????")
        else:
            if direction_candidates_UDRL[0] != -1 and direction_candidates_UDRL[2] != -1:
                print("↑→")
            else:
                print("???????????")
        
        rospy.set_param(rospy.get_name() + "/inf_rad_sorted", inf_rad_sorted)
        rospy.set_param(rospy.get_name() + "/direction_candidates_inf_rad_sorted_idx", direction_candidates_inf_rad_sorted_idx)
        rospy.set_param(rospy.get_name() + "/direction_candidates_UDRL", direction_candidates_UDRL)
        
        self._lib["record"].saveRecordFork(inf_rad_sorted)
        
        return "next"



#==================================================
## @class UpdateXTable
## @berif 
#==================================================
class UpdateXTable(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        q_table = rospy.get_param(rospy.get_name() + "/q_table", [])
        x_table = rospy.get_param(rospy.get_name() + "/x_table", [])
        position_meter = self._lib["map"].getRobotPointMeter()
        
        # 交差点のx_tableを更新
        nearest_x = [10000, 10000, 10000]   # 現在地点に一番近い交差点の座標x
        nearest_q = [0,0,0,0]               # 現在地点に一番近い交差点のQ
        nearest_x_table_idx = 0             # 現在地点に一番近い交差点の座標xのインデックス
        if len(x_table) == 0:
            x_table.append(position_meter)
            q_table.append([0,0,0,0])
            nearest_x = position_meter
        else:
            # 現在地点とx_table・q_tableの紐付け
            for i in range(len(x_table)):
                tmp1 = math.sqrt((x_table[i][0] - position_meter[0])**2 + (x_table[i][1] - position_meter[1])**2)
                tmp2 = math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2)
                if tmp1 < tmp2:
                    nearest_x = x_table[i]
                    nearest_q = q_table[i]
                    nearest_x_table_idx = i
            print("x_min = {}".format(math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2)))  
            # 新しい交差点を見つけたら、x_table・q_tableに追加する
            if math.sqrt((nearest_x[0] - position_meter[0])**2 + (nearest_x[1] - position_meter[1])**2) > 2.0:
                x_table.append(position_meter)
                q_table.append([0,0,0,0])
                nearest_x = position_meter
                nearest_q = [0,0,0,0]
                nearest_x_table_idx = len(x_table)-1
            # 発見済みの交差点を再度見つけたら、x_tableを更新する
            else:
                x_table[nearest_x_table_idx][0] = (x_table[nearest_x_table_idx][0] + position_meter[0]) / 2
                x_table[nearest_x_table_idx][1] = (x_table[nearest_x_table_idx][1] + position_meter[1]) / 2

        rospy.set_param(rospy.get_name() + "/q_table", q_table)
        rospy.set_param(rospy.get_name() + "/x_table", x_table)
        rospy.set_param(rospy.get_name() + "/nearest_x_table_idx", nearest_x_table_idx)
        
        self._lib["record"].saveRecordXid()

        return "next"



#==================================================
## @class MakeHumanDecideDirection
## @brief 
#==================================================
class MakeHumanDecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        direction_candidates_UDRL = rospy.get_param(rospy.get_name() + "/direction_candidates_UDRL", [-1,-1,-1,-1])

        position_meter = self._lib["map"].getRobotPointMeter()

        # GUIの変更
        self._lib["if"].changeGUI("select")

        decided_direction = []
        while True:
            if SocketActive:
                human_direction = self._lib["com"].waitSockets(timeout = 15)
            else:
                human_direction = self._lib["if"].waitGamepad()                                                     # [上、下、右、左]

            if human_direction == None:
                print("input timeout ...")
                continue

            """while True:
            human_direction = [0,0,1,0]
            if direction_candidates_UDRL[[i for i in range(len(human_direction)) if human_direction[i]==1][0]] == -1:
                human_direction = [1,0,0,0]
                if direction_candidates_UDRL[[i for i in range(len(human_direction)) if human_direction[i]==1][0]] == -1:
                    human_direction = [0,0,0,1]
                    if direction_candidates_UDRL[[i for i in range(len(human_direction)) if human_direction[i]==1][0]] == -1:
                        human_direction = [0,1,0,0]"""
            
            if direction_candidates_UDRL[[i for i in range(len(human_direction)) if human_direction[i]==1][0]] == -1:
                print("plz select correct direction !!!")
            else:
                decided_direction = human_direction #[上、下、右、左]
                rospy.set_param(rospy.get_name() + "/s_time", time.perf_counter())
                break

        rospy.set_param(rospy.get_name() + "/human_decided_direction", decided_direction) # [上、下、右、左]

        return "next"


#==================================================
## @class MakeRobotDecideDirection
## @brief 
#==================================================
class MakeRobotDecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )
        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered MakeRobotDecideDirection state.")

        direction_candidates_UDRL = rospy.get_param(rospy.get_name() + "/direction_candidates_UDRL", [-1,-1,-1,-1])
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [0,0,0,0])  # [上、下、右、左]
        position_meter = self._lib["map"].getRobotPointMeter()
        #q_table = rospy.get_param(rospy.get_name() + "/q_table", [])
        #x_table = rospy.get_param(rospy.get_name() + "/x_table", [])
        #nearest_x_table_idx = rospy.get_param(rospy.get_name() + "/nearest_x_table_idx", -1)

        # GUIの変更
        self._lib["if"].changeGUI("move")

        decided_direction = []
        # random時であれば、人間選択方向と後進方向以外で進行可能な中からランダムに選ぶ(3差路ならただ一つに決まる)
        if rospy.get_param("/random", "") == True:
            direction_candidates_UDRL[1] = -1 #後進方向除外
            decided_direction = [0 if direction_candidates_UDRL[i]==-1 else 1 for i in range(len(direction_candidates_UDRL))]#進行不可方向除外
            decided_direction = [0 if human_decided_direction[i] == 1 else decided_direction[i] for i in range(len(human_decided_direction))]#人間選択方向除外
            if sum(decided_direction) > 1: #候補が複数方向のときランダム選択
                temp = random.choice([i for i in range(len(decided_direction)) if decided_direction[i] == 1])
                decided_direction = [1 if i == temp else 0 for i in range(len(decided_direction))]
            print("decided_direction = {}".format(decided_direction))
            if decided_direction == [0,0,0,0]:
                decided_direction = [0,1,0,0]
            
        # not random時であれば、人間が選んだ方向以外かつ未探索を優先してランダムに選択する？
        elif rospy.get_param("/random", "") == False:
            direction_candidates_UDRL[1] = -1 #後進方向除外
            decided_direction = [0 if direction_candidates_UDRL[i]==-1 else 1 for i in range(len(direction_candidates_UDRL))]#進行不可方向除外
            decided_direction = [0 if human_decided_direction[i] == 1 else decided_direction[i] for i in range(len(human_decided_direction))]#人間選択方向除外
            if sum(decided_direction) > 1:         #候補が複数方向のとき未探索優先
            
                temp = random.choice([i for i in range(len(decided_direction)) if decided_direction[i] == 1])
                decided_direction = [1 if i == temp else 0 for i in range(len(decided_direction))]
                if decided_direction[2]==1:        #左手：decided_direction[3]==1:
                    decided_direction = [0,0,1,0] #decided_direction = [0,0,0,1]
                elif decided_direction[0]==1:
                    decided_direction = [1,0,0,0]
                elif decided_direction[3]==1:      #decided_direction[2]==1:
                    decided_direction = [0,0,0,1] #decided_direction = [0,0,1,0]
                else:
                    decided_direction = [0,1,0,0]
            print("decided_direction = {}".format(decided_direction))
            if decided_direction == [0,0,0,0]:
                decided_direction = [0,1,0,0]

            #print("nearest_x_table_idx = {}".format(nearest_x_table_idx))
            #print("q_table = {}".format(q_table))
            

        else:
            print("/random param error!")
            print(rospy.get_param("/random", ""))

        rospy.set_param(rospy.get_name() + "/robot_decided_direction", decided_direction) # [上、下、右、左]
        
        # 地図作成を待つ
        rospy.sleep(0.5)
        
        print(f"[DEBUG] Robot decided direction: {decided_direction}")
        return "next"



#==================================================
## @class DecideDirection
## @berif 
#==================================================
class DecideDirection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib
        robot_w = ErrRate
        human_w = 10 - robot_w
        self.L_tmp = ["robot"]*robot_w
        self.L_tmp.extend(["human"]*human_w)

        #==================================================
        # ROSインタフェース
        #==================================================

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered DecideDirection state.")
        
        inf_rad_sorted = rospy.get_param(rospy.get_name() + "/inf_rad_sorted", [])
        direction_candidates_UDRL = rospy.get_param(rospy.get_name() + "/direction_candidates_UDRL", [-1,-1,-1,-1])
        robot_decided_direction = rospy.get_param(rospy.get_name() + "/robot_decided_direction", [0,0,0,0])  # [上、下、右、左]
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [0,0,0,0])  # [上、下、右、左]
        x_cnt = rospy.get_param(rospy.get_name() + "/x_cnt", 0)

        print("inf_rad_sorted = {}".format(inf_rad_sorted))
        print("direction_candidates_UDRL[{}] = {}".format(x_cnt,direction_candidates_UDRL))
        print("robot_decided_direction[{}] = {}".format(x_cnt,robot_decided_direction))
        print("human_decided_direction[{}] = {}".format(x_cnt,human_decided_direction))

        position_meter = self._lib["map"].getRobotPointMeter()

        decided_direction = []
        if human_decided_direction == [0,0,0,0]: #人間側無入力の場合
            pilot = "robot"
        else:
            
            if x_cnt%len(self.L_tmp) == 0:
                random.shuffle(self.L_tmp)
            pilot = self.L_tmp[x_cnt%len(self.L_tmp)]
            #pilot = random.choices(("human", "robot"), weights = [10,0])[0]
        x_cnt += 1
            
        if pilot == "robot":
            print("chose robot's decided direction !")
            decided_direction = robot_decided_direction
        else:
            print("chose human's decided direction !")
            decided_direction = human_decided_direction

        idx = [direction_candidates_UDRL[i] for i,ele in enumerate(decided_direction) if decided_direction[i]==1][0]
        decided_direction_inf_rad_sorted = inf_rad_sorted[idx]

        rospy.set_param(rospy.get_name() + "/x_cnt", x_cnt)
        rospy.set_param(rospy.get_name() + "/pilot", pilot)
        rospy.set_param(rospy.get_name() + "/decided_direction", decided_direction)
        rospy.set_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", decided_direction_inf_rad_sorted)

        self._lib["record"].saveRecordPilot()
        self._lib["record"].saveRecordDirection()
        
        print(f"[DEBUG] Decided pilot: {pilot}")
        return "next"


#==================================================
## @class CheckErrP
## @berif errp状態をチェックしてArduinoに送信
#==================================================
class CheckErrP(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )
        self._lib = lib
        #TTL用にシリアル通信確立
        if TTLActive:
            self._lib["com"].openArduino()

        #==================================================
        # ROSインタフェース
        #==================================================

        return

    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return

    def execute(
        self,
        userdata
    ):
        if TTLActive:
            self._lib["com"].writeArduino("1")
        pilot = rospy.get_param(rospy.get_name() + "/pilot", "None")
        robot_decided_direction = rospy.get_param(rospy.get_name() + "/robot_decided_direction", [])  # [北、南、東、西]
        human_decided_direction = rospy.get_param(rospy.get_name() + "/human_decided_direction", [])  # [北、南、東、西]
        decided_direction_inf_rad_sorted = rospy.get_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0)
        position_meter = self._lib["map"].getRobotPointMeter()
        self._lib["record"].recordTime(state="lap")
        s_time = rospy.get_param(rospy.get_name() + "/s_time", 0.0)
        print("elapsed time = {}".format(time.perf_counter()-s_time))

        # 前進方向が選択された場合、ロボットが少し前進する(ErrP誘発のため)
        if 0.70 < math.cos(decided_direction_inf_rad_sorted - position_meter[2]):
            # decided_direction_inf_rad_sorted方向に前進する
            self._lib["nav"].sendRunTwist(
                decided_direction_inf_rad_sorted,
                position_meter[2],
                rad_speed = 0.01,
                target_time = 1.0
            )
        # 後退方向が選択された場合、回れ右をする(ErrP誘発のため)
        elif -0.70 > math.cos(decided_direction_inf_rad_sorted - position_meter[2]):
            # decided_direction_inf_rad_sorted方向に回転する
            self._lib["nav"].sendRotationTwist(decided_direction_inf_rad_sorted,position_meter[2],)
        # それ以外の方向が選択された場合、ロボットが回転する(ErrP誘発のため)
        else:
            self._lib["nav"].sendRotationTwist(decided_direction_inf_rad_sorted, position_meter[2])

        rospy.sleep(1.0)

        # ロボットの決定した進行方向が選択され、人間とロボットの選択した進行方向が異なる場合
        if pilot == "robot" and robot_decided_direction != human_decided_direction:
                print("ErrP evoked !!!")
                errp = 1    # ErrP発生
        else:
            errp = 0

        rospy.set_param(rospy.get_name() + "/errp", errp)
        rospy.set_param(rospy.get_name() + "/position_meter", position_meter)

        self._lib["record"].saveRecordErrP()


        return "next"


#==================================================
## @class UpdateQTable
## @berif 
#==================================================
class UpdateQTable(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param robot_decided_direction
    def execute(
        self,
        userdata
    ):

        decided_direction   = rospy.get_param(rospy.get_name() + "/decided_direction", [])              # [北、南、東、西]
        q_table             = rospy.get_param(rospy.get_name() + "/q_table", [])
        x_table             = rospy.get_param(rospy.get_name() + "/x_table", [])
        nearest_x_table_idx = rospy.get_param(rospy.get_name() + "/nearest_x_table_idx", -1)
        errp                = rospy.get_param(rospy.get_name() + "/errp", 0)

        # 交差点のq_tableを更新
        # TODO ErrPの認識結果をreward則に反映する
        reward = 0
        if errp == 1: # ErrPが発生した場合、
            reward = 0 # 罰則を与える
        decided_direction_idx = [i for i in range(len(decided_direction)) if decided_direction[i]==1][0]
        q_table[nearest_x_table_idx][decided_direction_idx] += reward

        #print("q_table = {}".format(q_table))
        #print("x_table = {}".format(x_table))
        print("errp = {}".format(errp))

        rospy.set_param(rospy.get_name() + "/q_table", q_table)

        self._lib["record"].saveRecordQTable()
        self._lib["record"].saveRecordXTable()

        #if errp == 1:

            #return "err"
        
        #else:
        
        return "next"


#==================================================
## @class PassIntersection
## @berif 
#==================================================
class PassIntersection(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["next", "loop", "reset", "restart", "except"]
        )

        self._lib = lib

        #==================================================
        # ROSインタフェース
        #==================================================

        return



    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return



    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param 
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):
        print("[DEBUG] Entered PassIntersection state.")
        
        decided_direction_inf_rad_sorted = rospy.get_param(rospy.get_name() + "/decided_direction_inf_rad_sorted", 0)
        
        # decided_direction_inf_rad_sorted方向に2.0m進行する
        position_meter = self._lib["map"].getRobotPointMeter()
        inf_points_meter = self._lib["scan"].getLaserInfPointMeter(
            [decided_direction_inf_rad_sorted],
            position_meter,
            distance = 1.8
        )
        self._lib["nav"].sendMeterGoal(
            inf_points_meter[0],
            decided_direction_inf_rad_sorted
        )

        # ナビゲーションがスタックした場合、トライアルをリセットする
        for s in self._lib["nav"].subNaviStatus():
            if s == 4: 
                """print("Navi stack ...(GoToCorre)")
                self._lib["record"].recordGoal(False)
                self._lib["record"].recordStatus("stack")
                self._lib["record"].recordTime(state="lap")
                self._lib["nav"].resetTrial()"""
                self._lib["nav"].sendRunTwist(
                decided_direction_inf_rad_sorted,
                position_meter[2],
                lin_speed = -0.3,
                rad_speed = 0,
                target_time = 1.0
            )

                return "next"

        rospy.sleep(0.3)

        #地図の保存とGUIの更新
        point_pixel = self._lib["map"].getRobotPointPixel()
        self._lib["record"].saveMap()
        self._lib["if"].changeGUI(point_pixel)

        inf_rad_sorted = self._lib["scan"].getLaserInfRad()

        # もし、進行可能な空間がない場合、GoAheadステートで直進する
        if len(inf_rad_sorted) == 0:
            print("[DEBUG] No way forward, moving ahead.")
            return "next"                      


        # 現在のロボットの後進方向から一番近いinf_radを発見する
        position_meter = self._lib["map"].getRobotPointMeter()
        nearest_inf_rad_to_present_rad = inf_rad_sorted[0] - math.pi
        for i in range(len(inf_rad_sorted)):
            if math.cos(inf_rad_sorted[i] - position_meter[2] - math.pi) >= math.cos(nearest_inf_rad_to_present_rad - position_meter[2] - math.pi):
                nearest_inf_rad_to_present_rad = inf_rad_sorted[i]
        if 0.0 < math.cos(nearest_inf_rad_to_present_rad - math.pi - position_meter[2]):
            # ロボットを回転させる（位置調整のため）
            self._lib["nav"].sendRotationTwist(nearest_inf_rad_to_present_rad - math.pi, position_meter[2])


        rospy.sleep(0.3)
        
        print("[DEBUG] Passing intersection.")
        return "next"


#==================================================
## @class ConfirmExit
## @brief 終了確認画面表示ステート
#==================================================
class ConfirmExit(smach.State):
    def __init__(self, lib):
        smach.State.__init__(self, outcomes=["yes", "except"])
        self._lib = lib

    def execute(self, userdata):
        print("[DEBUG] Entered ConfirmExit state.")

        # GUIを終了確認モードに変更
        self._lib["if"].changeGUI("exit_confirm")

        # 選択肢の初期値
        current_selection = "No"
        options = ["Yes", "No"]

        while True:
            # ゲームパッド入力を待機
            print("[DEBUG] Waiting for gamepad input...")
            response = self._lib["if"].waitGamepad()

            if response == [1, 0, 0, 0]:  # 左十字キー上（選択肢切り替え: 上）
                current_selection = "Yes"
                print("[DEBUG] Selection changed to: Yes")
                self._lib["if"].changeGUI("exit_confirm_yes")  # Yesが選択されているGUI表示

            elif response == [0, 1, 0, 0]:  # 左十字キー下（選択肢切り替え: 下）
                current_selection = "No"
                print("[DEBUG] Selection changed to: No")
                self._lib["if"].changeGUI("exit_confirm_no")  # Noが選択されているGUI表示

            elif response in [[0, 0, 1, 0], [0, 0, 0, 1]]:  # 右十字キーのどれか（決定）
                print(f"[DEBUG] Confirmed selection: {current_selection}")
                if current_selection == "Yes":
                    return "yes"
                else:
                    return "except"

            elif response is None:  # 入力がタイムアウトした場合
                print("[DEBUG] No input detected, returning to except.")
                return "except"



#==================================================
## @class End
## @berif 終了ステート
#==================================================
class End(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["end"]
        )

        self._lib = lib
        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        return "end"




#==================================================
## @class Except
## @brief 例外ステート
#==================================================
class Except(
    smach.State
):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param lib ライブラリ群
    ## @return
    #==================================================
    def __init__(
        self,
        lib = {}
    ):
        #==================================================
        # イニシャライズ
        #==================================================
        smach.State.__init__(
            self,
            outcomes = ["except"]
        )

        self._lib = lib

        return




    #==================================================
    ## @fn __del__
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def __del__(self):
        #==================================================
        # ファイナライズ
        #==================================================

        return




    #==================================================
    ## @fn execute
    ## @brief 実行関数
    ## @param userdata
    ## @return
    #==================================================
    def execute(
        self,
        userdata
    ):

        return "except"
