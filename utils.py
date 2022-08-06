'''
功能： 发送指定AT命令到设备
'''
 
import serial
import time
import serial.tools.list_ports
import re

# import UserCode



# def at_cmd_parse(cmd):
#     try:
#         pattern = re.findall('{{(.+?)}}',cmd)
#         #self.printf(pattern)
#         new_cmd = cmd
#         for item in pattern:
#             new_cmd = new_cmd.replace('{{'+item+'}}',str(eval('UserCode.'+item)))
#         #self.printf(new_cmd)
#         return new_cmd
#     except Exception as e:
#         self.printf("errno"+e)
#         return 0

def test(self,device,index,list):
    cmd = at_cmd_parse(list[0])
    if cmd == 0:
        self.printf("errno"+e)
        return -2
    self.printf("<-"+cmd)
    device.Send_data(cmd.encode())
    while True:
        try:
            if device.get_recv_status():
                data = device.Read_Line().decode("utf-8")
                if data != '\r\n' :
                    self.printf("->"+data)
                    if len(list) == 3 :
                        if list[1] != 0 :
                            if list[1](self,data) == False:
                                break
                        if list[2] != 0 and data.find(list[2]) != -1:
                            return 0
                    elif len(list) == 2:
                        if list[1] != 0 :
                            if list[1](self,data) == False:
                                break
                        if data.find('OK') != -1 :
                            return 0
                    else :
                        if data.find('OK') != -1 :
                            return 0
                    if data.find('ERROR') != -1 :
                        return -1
        except Exception as e:
            self.printf("errno:"+e)
            return -2
    
bsp_list = ['115200','57600','56000','43000','38400','19200','9600','4800','2400','1200','600','300']
test_times = ['1','5','10','20','40','80','160']
at_cycle_times = ['1','5','10','20','40','80']
at_send_time = ['0','2','4','6','8','10']
def init_com_list() :
    port_list_name = []
    port_list = list(serial.tools.list_ports.comports())
    if len(port_list) <= 0:
        #self.printf("The Serial port can't find!")
        return False,[]
    else:
        for each_port in port_list:
            port_list_name.append(each_port[0])
        #self.printf("COM:"+'['+','.join(port_list_name)+']')
        return True,port_list_name

def FIND_COM(self,com) :
    global port_list_name
    for item in port_list_name :
        if item == com :
            return True
    return False
        
UserFile = './config/Palm-cmd/UserCode.py'

def copy_file(filename):
    ret = False
    try:
        dist = open(UserFile,"w",encoding='utf-8')
    except Exception as e:
        return ret
    src = open(filename, "r", encoding='utf-8')
    s = src.read()
    w = dist.write(s)
    src.close()
    dist.close()
    return True



# def at_test(self,device,check_err) :
#     err_num = 0
#     err_list = []
#     try:
#         for index,item in enumerate(UserCode.cmd_list) :
#             ret = test(self,device,index,item)
#             if ret == -1 :
#                 err_num += 1
#                 err_list.append(item[0])
#                 if check_err :
#                     break
#             if ret == -2 :
#                 break
#             time.sleep(0.5)
#         self.printf("err_num:"+str(err_num))
#         self.printf("err_list:"+'['+','.join(err_list)+']')
#     except Exception as e:
#             self.printf("errno:"+e)
#             return -2
'''
if __name__ == "__main__" :
    at_test(1,'COM118',115200,False)
'''


