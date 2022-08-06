"""
1、创建一个socket连接，得到一个client端
"""
import socket
import time

class Client():
    def __init__(self):
        self.socket_client = socket.socket(family=socket.AF_INET,type=socket.SOCK_STREAM)
        self.cmdType = 0 #0,+cmd，+cmdz，1：+urc,2:+exit
        self.flag = 0
        self.count = 0
        self.retry_count = 0
        
    def init_param(self):
        self.flag = 0
        self.count = 0
        
    def Connect(self,port=8889):
        try:
            self.socket_client.connect(("127.0.0.1",port))
            return True
        except Exception as e:
            print('error:',e)
            return False

    def printf(self,*args):
        now = time.strftime("[%H:%M:%S]", time.localtime())
        #self.Send('+urc:'+' '.join(*args))
        print(now, *args)
    
    def get_send_type(self):
        return self.cmdType
        
    def Send(self,data):
        if data.find('+exit') != -1:
            self.cmdType = 2
        try:
            self.socket_client.send(data.encode('utf-8'))
            time.sleep(0.1)
            return True
        except Exception as err:
            print('send error',err)
            return False
            
    def Recv(self,len=1024):
        try:
            return True,self.socket_client.recv(1024).decode('utf-8')
        except Exception as err:
            print('recv error',err)
            return False,''
        
    def Close(self):
        self.socket_client.close()

