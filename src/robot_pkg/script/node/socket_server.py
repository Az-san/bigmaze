#coding: utf-8
#Author: Takumi FUJI
#info:   windowsからの司令をubuntuでソケット通信を介して受信するモジュール


import socket

class BMISocket():
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(("172.27.32.1", 52350))  # 自身のIPアドレスとポート番号を指定
        print("waiting...")
        self.sock.listen(5)
        self.clientsocket, self.address = self.sock.accept()
        print(f"Connection from {self.address} has been established!")
    
    def read(self):
        recvline = self.clientsocket.recv(1024).decode()
        print(recvline)
        return recvline
        
    def readConv(self):
        recvline = self.clientsocket.recv(1024).decode()
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
 
    def __del__(self):
        self.clientsocket.close()
        self.sock.close()

if __name__ == '__main__':
    Skt = BMISocket()
    while True:
        data = Skt.read()
        if data == "exit":
            break
    print("Socket ended.")
        
