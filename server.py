"""
1、创建 socket.socket()
2、绑定地址和端口号
3、监听客户端请求
4、接受客户端的请求，并为之开辟一个线程来处理他的业务逻辑。
"""
import socket
import threading
import time
from PyQt5 import QtCore

    
class ServerThread(QtCore.QThread):
    strOut = QtCore.pyqtSignal(str)

    def __init__(self,ip,port):
        super().__init__()
        #设置工作状态与初始num数值
        self.working = False  
        self.socket_server = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
        #二、绑定地址和端口号
        self.socket_server.bind((ip,port))
        #三、监听客户端请求
        self.socket_server.listen()
        self.sock = -1

    def Stop(self):
        #线程状态改变与线程终止
        print('stop')
        self.working = False
        time.sleep(1)
        self.socket_server.close()
        #self.exit(0)
        
    
    def Start(self):
        #线程状态改变与线程终止
        self.working = True
        #self.setDaemon(True)
        self.start()
    
    def Send(self,data):
        if self.sock != -1:
            try:
                self.sock.send(data.encode('utf-8'))
            except Exception as err:
                print('send error',err)
                return False
                
    def get_status(self):
        return self.working

    def run(self):
        print("runing")
        (self.sock,self.addr) = self.socket_server.accept()
        while self.working == True:
            try:
                data =self.sock.recv(1024).decode('utf-8')
                if data == "":
                    continue
                #print("-----------服务端start--------")
                #print('recv：'+data)
                self.strOut.emit(data)
                #print("-----------服务端end--------")
                #sock.send((value+value).encode('utf-8'))
            except Exception as e:
                #self.printf()
                data = "+error:"+str(e)
                self.strOut.emit(data)
                break    