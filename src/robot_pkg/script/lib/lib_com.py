#!/usr/bin/env python3
# -*- coding: utf-8 -*-


#==================================================
## @file lib_com
## @author Takumi FUJI
## @brief ライブラリクラス
#==================================================




#==================================================
# import
#==================================================
import sys
import roslib
import socket
import serial

sys.path.append(roslib.packages.get_pkg_dir("robot_pkg") + "/script/import")
from common_import import *

#==================================================
# グローバル
#==================================================




#==================================================
## @class LibCom
## @brief 自作ライブラリクラス
#==================================================
class LibCom:
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
        self._lib = {
        }


        #==================================================
        # ROSインタフェース
        #==================================================


        #==================================================
        # イニシャライズ
        #==================================================


        return


    #==================================================
    ## @fn initSocket
    ## @brief ソケット通信を確立する
    ## @param 
    ## @return
    #==================================================
    def initSocket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("172.27.32.1", 52350))  # 自身のIPアドレスとポート番号を指定
        print("waiting...")
        self.sock.listen(5)
        self.clientsocket, self.address = self.sock.accept()
        print(f"Connection from {self.address} has been established!")
        self.clientsocket.settimeout(15)


    #==================================================
    ## @fn readSocket
    ## @brief ソケット通信内容を取得する
    ## @param 
    ## @return
    #==================================================
    def readSocket(self):
        try:
            recvline = self.clientsocket.recv(1024).decode()
            print(recvline)
        except:
            print("Socket timeout...")
            recvline = None
        return recvline


    #==================================================
    ## @fn readSocketConv
    ## @brief ソケット通信内容を取得して上下右左リストに変換
    ## @param ^v><がそれぞれ上下右左に対応
    ## @return
    #==================================================
    def readSocketConv(self):
        try:
            recvline = self.clientsocket.recv(1024).decode()
        except socket.timeout:
            return None
        
        print(recvline)
        if recvline == "^":
            data = [1,0,0,0]
        elif recvline == "v":
            data = [0,1,0,0]
        elif recvline == ">":
            data = [0,0,1,0]
        elif recvline == "<":
            data = [0,0,0,1]
        elif recvline == "exit":
            data = recvline
        else:
            print("Socket error!")
        return data

    #==================================================
    ## @fn openArduino
    ## @brief Arduinoとのシリアル通信を確立する
    ## @param 
    ## @return
    #==================================================
    def openArduino(self):
       self.Ser=serial.Serial('/dev/ttyACM0',9600,timeout=3)
       print(self.Ser.readline())
       #time.sleep(1)
       
       return
    
       
    #==================================================
    ## @fn writeArduino
    ## @brief シリアル通信でArduinoに送信("1"でTTL3秒)
    ## @param 
    ## @return
    #==================================================
    def writeArduino(self, Message):
        try:
            # デバッグ用メッセージ: 送信内容を出力
            print(f"[DEBUG] Sending message to Arduino: {Message}")
            self.Ser.write(Message.encode())  # シリアル通信で送信
            print("[DEBUG] Message sent successfully.")
        except Exception as e:
            # エラーが発生した場合、エラーメッセージを表示
            print(f"[ERROR] Failed to send message: {e}")
        return

        
    #==================================================
    ## @fn closeArduino
    ## @brief シリアル通信を終了する
    ## @param 
    ## @return
    #==================================================
    def closeArduino(self): 
        self.Ser.close()
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
        self.clientsocket.close()
        self.sock.close()
        self.closeArduino()

        return


