#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#==================================================
## @file libnav
## @original_author Kentaro NAKAMURA
## @author Takumi FUJI
## @modified by Maiko KUDO
## @brief ライブラリクラス
#==================================================

#==================================================
# import
#==================================================
import sys
import roslib
import rospy
import cv2
import numpy as np
import math
import hid  # hidapiを使ったジョイスティックサポート
import os
from PyQt5 import QtGui, QtCore, QtWidgets
from cv_bridge import CvBridge, CvBridgeError
from std_msgs.msg import String
from sensor_msgs.msg import Image

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================

#==================================================
## @class GUI
## @brief GUIのアニメーションを操作する
#==================================================
class GUI(QtWidgets.QWidget):
    #==================================================
    ## @fn __init__
    ## @brief コンストラクタ
    ## @param 
    ## @return
    #==================================================
    def __init__(self, *args):
        super(QtWidgets.QWidget, self).__init__()

        #==================================================
        # メンバ変数
        #==================================================
        # FPS
        self.fps = 24
        size_img = 1, 1, 3
        self.robot_img = np.zeros(size_img, dtype=np.uint8)
        self.gui_state = "start"
        self.load_images()
        
        # Map用パス
        self.data_path = roslib.packages.get_pkg_dir("robot_pkg") + "/io"

        #==================================================
        # ROSインタフェース
        #==================================================
        self.bridge = CvBridge()

        self.sub_img = rospy.Subscriber(
            "/camera/rgb/image_raw", 
            Image, 
            self.imgCallback
        )

        self.sub_gui_state = rospy.Subscriber(
            "/gui_state", 
            String, 
            self.guiStateCallback
        )
        
        self.MiniMap = rospy.get_param("/MiniMap", False)

        #==================================================
        # イニシャライズ
        #==================================================
        self.video_frame = QtWidgets.QLabel()
        self.lay = QtWidgets.QVBoxLayout()
        self.lay.setContentsMargins(0,0,0,0)
        self.lay.addWidget(self.video_frame)
        self.setLayout(self.lay)

        # hidapiによるジョイスティックの初期化
        try:
            self.joystick = hid.device()
            self.joystick.open(0x046d, 0xc218)  # Logitech RumblePad 2のVIDとPID
            self.joystick.set_nonblocking(True)
            print("Joystickの名称: Logitech RumblePad 2 USB")
        except IOError:
            print("Joystickが見つかりませんでした。")

    #==================================================
    ## @fn delete
    ## @brief デストラクタ
    ## @param
    ## @return
    #==================================================
    def delete(self):
        if self.joystick:
            self.joystick.close()

    #==================================================
    ## @fn imgCallback
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def imgCallback(self, data):
        try:
            tmp_sub_img_data = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)
        self.robot_img = tmp_sub_img_data

    #==================================================
    ## @fn guiStateCallback
    ## @brief 
    ## @param
    ## @return
    #==================================================
    def guiStateCallback(self, data):
        self.gui_state = data.data

    #==================================================
    ## @fn start
    ## @brief QT独自スレッドの開始
    ## @param
    ## @return
    #==================================================
    def start(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.gamepadEvent)
        self.timer.start(int(1000./self.fps))

    #==================================================
    ## @fn gamepadEvent
    ## @brief QTウィンドウ上でのゲームパッドイベント管理
    ## @param
    ## @return
    #==================================================
    def gamepadEvent(self):
        try:
            data = self.joystick.read(64)
            if data:
                x_axis = data[0]
                y_axis = data[1]
                if x_axis == -1:
                    print("Le")
                elif x_axis == 1:
                    print("Ri")
                elif y_axis == 1:
                    print("St")
                elif y_axis == -1:
                    print("Ba")
        except Exception as e:
            print(f"ジョイスティック入力エラー: {e}")

    #==================================================
    ## @fn keyPressEvent
    ## @brief QTウィンドウ上でのキーイベント管理
    ## @param
    ## @return
    #==================================================
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            sys.exit()
        elif e.key() == QtCore.Qt.Key_D:
            print("D")
        elif e.key() == QtCore.Qt.Key_Q:
            print("Q")
        elif e.key() == QtCore.Qt.Key_R:
            print("R")
        elif e.key() == QtCore.Qt.Key_W:
            print("W")
        elif e.key() == QtCore.Qt.Key_M:
            print("M")
        elif e.key() == QtCore.Qt.Key_I:
            print("I")

    #==================================================
    ## @fn 
    ## @brief QTウィンドウ上での描画管理（スーパークラス定義）
    ## @param
    ## @return
    #==================================================
    def paintEvent(self, e):
        frame = self.robot_img
        print("paintEvent called")
        print("Current GUI State:", self.gui_state)
        print("MiniMap Enabled:", self.MiniMap)  # MiniMapが有効かどうか

        if self.gui_state == "start":
            # タイトル画面
            img = QtGui.QImage(self.title_img, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
            self.MiniMap = rospy.get_param("/MiniMap", False)
        else:
            # ロボットカメラ
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = QtGui.QImage(frame, frame.shape[1], frame.shape[0], QtGui.QImage.Format_RGB888)
        painter = QtGui.QPainter(img)
        # 四角形
        painter.setBrush(QtCore.Qt.yellow)
        if self.gui_state == "wait":
            painter.drawRect(102*2, 50*2, 110, 50)
        elif self.gui_state == "select":
            painter.drawRect(102*2, 50*2, 160, 50)
        elif self.gui_state == "error":
            painter.drawRect(102*2, 50*2, 145, 50)
        # 文字
        painter.setBrush(QtCore.Qt.lightGray)
        painter.setPen(QtCore.Qt.red)
        painter.setFont(QtGui.QFont(u'メイリオ', 30, QtGui.QFont.Bold, False))
        if self.gui_state == "wait":
            painter.drawText(QtCore.QPoint(105*2, 140), 'WAIT')
        elif self.gui_state == "select":
            painter.drawText(QtCore.QPoint(105*2, 140), 'SELECT')
        elif self.gui_state == "error":
            painter.drawText(QtCore.QPoint(105*2, 140), 'ERROR')
        # 注視点
        if self.gui_state != "start":
            painter.setPen(QtCore.Qt.cyan)
            painter.drawText(QtCore.QPoint(480*2, 270*2), '+')
            
        # ミニマップ
        print("Current State for MiniMap:", self.gui_state)
        if self.MiniMap == True:
            print("MiniMap is enabled, checking state...")  # MiniMapが有効なことを確認
            if self.gui_state != "move" and self.gui_state != "wait" and self.gui_state != "select" and self.gui_state != "error":
                print("Valid state for showing MiniMap:", self.gui_state)
                if self.gui_state == "start":
                    position_pixel = (10,10)
                    angle = 0.0
                else:
                    position_pixel_str = self.gui_state.split(",")
                    position_pixel = (int(position_pixel_str[0]),int(position_pixel_str[1]))
                    angle = float(position_pixel_str[2])

                print(f"Loading map image with position: {position_pixel}, angle: {angle}")

                self.load_mapimg(position_pixel, angle)
            if self.gui_state != "start":
                height, width, dim = self.map_img.shape
                print("Map Image Shape:", self.map_img.shape)  # マップ画像のサイズ確認
                bytesPerLine = dim * width
                mapimg = QtGui.QImage(self.map_img, width, height, bytesPerLine, QtGui.QImage.Format_RGBA8888)
                map_pos_x = int(frame.shape[1]/2 - width/2)
                map_pos_y = int(frame.shape[0]/4*3 - height/2)
                print(f"Drawing MiniMap at position: ({map_pos_x}, {map_pos_y})")  # 描画位置の確認
                painter.drawImage(map_pos_x,map_pos_y,mapimg)

            else:
                print("No map image loaded.")

        painter.end()

        pix = QtGui.QPixmap.fromImage(img)
        self.video_frame.setPixmap(pix)



    #==================================================
    ## @fn 
    ## @brief シャットダウン
    ## @param
    ## @return
    #==================================================
    def shutdown(self):
        self.close() # 閉じる

    #==================================================
    ## @fn load_images
    ## @brief 描画する画像のロード
    ## @param
    ## @return
    #==================================================
    def load_images(self):
        self.title_img = cv2.imread(roslib.packages.get_pkg_dir("robot_pkg") + "/io" + "/titlex2.jpg")


    #==================================================
    ## @fn load_mapimg
    ## @brief map画像のロード
    ## @param
    ## @return
    #==================================================
    def load_mapimg(self, pos_pix=(0, 0), angle=0.0):
        try:
            self.map_img = cv2.imread(self.data_path + "/map.pgm")
            print("Loading map image with position:", pos_pix, "and angle:", angle)
        except:
            print("Map load error!")
        else:
            self.map_img = cv2.rotate(self.map_img,cv2.ROTATE_90_COUNTERCLOCKWISE)
            #cv2.circle(self.map_img, (pos_pix[0],pos_pix[1]), 6, (255,0,0), thickness = -1)
            pts = np.array(( (int(pos_pix[0]-7*np.sin(angle)), int(pos_pix[1]-7*np.cos(angle))), (int(pos_pix[0]-7.2*np.sin(angle+2.356)), int(pos_pix[1]-7.2*np.cos(angle+2.356))), (int(pos_pix[0] -2*np.sin(angle+3.141)), int(pos_pix[1]-2*np.cos(angle+3.141))), (int(pos_pix[0]-7.2*np.sin(angle-2.356)), int(pos_pix[1]-7.2*np.cos(angle-2.356))) ))
            cv2.fillPoly(self.map_img, [pts], (255,0,0))
            self.map_img = cv2.resize(self.map_img, dsize=None, fx=0.8, fy = 0.8)
            mask = cv2.inRange(self.map_img,(204,204,204),(206,206,206))
            self.map_img = cv2.cvtColor(self.map_img, cv2.COLOR_BGR2BGRA)
            self.map_img[:,:,3] = 128
            self.map_img[mask == 255 , 3] = 0

    #==================================================
    ## @fn main
    ## @brief クラスメイン関数
    ## @param
    ## @return
    #==================================================
    def main(self):
        self.setWindowFlags(QtCore.Qt.Window)
        self.start()
        self.setWindowTitle("Experiment GUI")
        self.show()
        print("Graphic Queue")
        
    #==================================================
    ## @fn shutdown
    ## @brief クラス終了時のシャットダウン処理
    ## @param
    ## @return
    #==================================================
    def shutdown(self):
        self.close()  # ウィンドウを閉じる


#==================================================
# メイン
#==================================================
if __name__ == "__main__":
    try:
        rospy.init_node(os.path.basename(__file__).split(".")[0])
        app = QtWidgets.QApplication(sys.argv)
        gui = GUI(0)
        gui.main()
        rospy.on_shutdown(gui.shutdown) 
        app.exec_()
        rospy.spin()
    except Exception as e:
        rospy.logerr(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        
