#!/usr/bin/env python3
# -*- coding: utf-8 -*-




#==================================================

## @file sm_search_maze_node.py
## @author Kentaro NAKAMURA
## @brief 迷路を探索するROSノード

#==================================================




#==================================================

# import

#==================================================
import sys
from robot_pkg.script.lib.lib_com import LibCom
from robot_pkg.script.lib.lib_if import LibIF
from robot_pkg.script.lib.lib_map import LibMap
from robot_pkg.script.lib.lib_nav import LibNav
from robot_pkg.script.lib.lib_record import LibRecord
from robot_pkg.script.lib.lib_scan import LibScan
import roslib
import rospy
import os

import smach
import smach_ros

import MS_main
from MS_main import *

# robot_pkgのサブディレクトリからモジュールをインポート
sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

# 各ライブラリを個別にインポート
sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/lib")
from lib_map import LibMap
from lib_nav import LibNav
from lib_com import LibCom
from lib_scan import LibScan
from lib_record import LibRecord
from lib_if import LibIF



#==================================================

# グローバル

#==================================================
GP_DEFAULT_START_STATE = "Start"




#==================================================

## @class StateMachine
## @brief ステートマシンクラス

#==================================================
class StateMachine:
    #==================================================
    
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param
    ## @return

    #==================================================
    def __init__(
        self
    ):
        #==================================================

        # メンバ変数

        #==================================================
        self._libmap = LibMap()
        self._libnav = LibNav()
        self._libcom = LibCom()
        self._libscan = LibScan()
        self._librecord = LibRecord()
        self._libif = LibIF()

        self._lib = {
            "map": self._libmap,
            "nav": self._libnav,
            "com": self._libcom,
            "scan": self._libscan,
            "record": self._librecord,
            "if": self._libif,
        }


        #==================================================

        # イニシャライズ

        #==================================================
        #スタートステートの選択
        start_state = GP_DEFAULT_START_STATE

        #ステートマシンの宣言
        self._ssm = smach.StateMachine(outcomes = ["exit"])

        with self._ssm:
            smach.StateMachine.add(
                "Init",
                Init(self._lib), 
                transitions = {
                    "next":"Wait4Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "Wait4Start",
                Wait4Start(self._lib),
                transitions = {
                    "next":start_state,
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "Start",
                Start(self._lib),
                transitions = {
                    "next":"StartTrial",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "StartTrial",
                StartTrial(self._lib),
                transitions = {
                    "next":"CheckIntersection",
                    "restart":"Start",
                    "loop":"StartTrial",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "CheckIntersection",
                CheckIntersection(self._lib),
                transitions = {
                    "true":"MakeDirectionCandidates",
                    "false":"GoAhead",
                    "loop":"CheckIntersection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "GoAhead",
                GoAhead(self._lib),
                transitions = {
                    "next":"CheckIntersection",
                    "loop":"GoAhead",
                    "reset":"Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeDirectionCandidates",
                MakeDirectionCandidates(self._lib),
                transitions = {
                    "next":"UpdateXTable",
                    "loop":"MakeDirectionCandidates",
                    "reset":"Start",
                    "except":"Except",
                    "back":"GoAhead"
                }
            )
            smach.StateMachine.add(
                "UpdateXTable",
                UpdateXTable(self._lib),
                transitions = {
                    "next":"MakeHumanDecideDirection",
                    "loop":"UpdateXTable",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeHumanDecideDirection",
                MakeHumanDecideDirection(self._lib),
                transitions = {
                    "next":"MakeRobotDecideDirection",
                    "loop":"MakeHumanDecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "MakeRobotDecideDirection",
                MakeRobotDecideDirection(self._lib),
                transitions = {
                    "next":"DecideDirection",
                    "loop":"MakeRobotDecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "DecideDirection",
                DecideDirection(self._lib),
                transitions = {
                    "next":"CheckErrP",
                    "loop":"DecideDirection",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "CheckErrP",
                CheckErrP(self._lib),
                transitions = {
                    "next":"UpdateQTable",
                    "loop":"CheckErrP",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "UpdateQTable",
                UpdateQTable(self._lib),
                transitions = {
                    "next":"PassIntersection",
                    "loop":"UpdateQTable",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "PassIntersection",
                PassIntersection(self._lib),
                transitions = {
                    "next":"GoAhead",
                    "loop":"PassIntersection",
                    "reset":"StartTrial",
                    "restart":"Start",
                    "except":"Except"
                }
            )
            smach.StateMachine.add(
                "End",
                End(self._lib),
                transitions = {
                    "end":"exit",
                }
            )
            smach.StateMachine.add(
                "Except",
                Except(self._lib),
                transitions = {
                    "except":"exit"
                }
            )

        sris = smach_ros.IntrospectionServer("ssm", self._ssm, "/SM_ROOT")
        sris.start()


        return




    #==================================================
    
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return

    #==================================================
    def delete(
        self
    ):
        #==================================================

        # ファイナライズ

        #==================================================
        for key in self._lib.keys():
            self._lib[key].delete()

        del self._ssm


        return




    #==================================================
    
    ## @fn proc
    ## @berif 処理関数
    ## @param
    ## @return

    #==================================================
    def proc(
        self
    ):
        self._ssm.execute()


        return




#==================================================

# メイン

#==================================================
if __name__ == "__main__":
    rospy.init_node(os.path.basename(__file__).split(".")[0])

    state_machine = StateMachine()

    rospy.on_shutdown(state_machine.delete)

    state_machine.proc()

    rospy.signal_shutdown("")
