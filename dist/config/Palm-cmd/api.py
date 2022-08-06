'''
def fun(device,data,index)
device.print() :在log打印，在log文件中可以看出
device.Send(str):发送字符串str, 命令模式： +cmd:发送内容
                                       +cmdz:发送内容,会自动发送ctrl+z
                                       +exit:time,index 经过time秒后，测试第index条命令
                                       +urc:数据打印在AutoCMD工具中
data :为device返回的一行结果
index :表示当前执行命令的index
'''
import re,json

#define
success = 0 #找到
goingon = 1 #尚未找到
stop = 2    #停止
jump = 3    #跳转
next_cmd = 4#下一条命令
##userCode

#check 元组，解析获得的字符串
#ret_list返回查找到符合条件的字符串列表
#send 找到符合字符串之后发送数据，以'+cmd:','+cmdz:','+urc:'开头
#例如target = '+COPS:',check:{0:'0',1:'2',2:"46011",3:'7'}
#找到返回success，找不到返回goingon
def fuc_handle(device,data,target = None, check = None, ret_list=None, send=None) :
    if data.find(target)!=-1:
        if check != None :
            _str = data[len(target):]
            _str_list = _str.split(',')
            _len = len(_str_list)
            if _len < 2:
                return goingon
            print('str',_str_list)
            json_str = json.dumps(check)
            _json = json.loads(json_str)
            _items = _json.items()
            for key, value in _items:
                if _len >= int(key):
                    if value.strip() != _str_list[int(key)].strip():
                        return goingon 

        if ret_list != None :
            ret_list.append(data)
        
        if send != None:
            device.Send(send)
            if data.find('+exit:')!=-1 :
                return stop
        #找到退出
        return success 
    else:
        return goingon
        
        
def func_timer(times=5):
    index = 0
    while index<times:
        index+=1
        sleep(1)
        
#命令重新测试，retry_times:测试次数              
def fuc_retry(device,data,retry_times,succ='OK',err='ERROR'):
    if data.find(succ) != -1 or data.find(err) != -1:
        if device.retry_count < retry_times:
            device.retry_count += 1
            return jump
        else :
            return stop
    else:
        return goingon

# 命令重新测试，retry_times:测试次数,退出发送数据
def fuc_retryEx(device, data, retry_times, succ='OK', err='ERROR', send = None):
    if data.find(succ) != -1 or data.find(err) != -1:
        if device.retry_count < retry_times:
            device.retry_count += 1
            return jump
        else:
            if send != None:
                device.Send(send)
            return stop
    else:
        return goingon

        #获取从发送命令开始的多少行数据
def fuc_get_line(device,data,lines):
    if device.count < lines:
        device.count += 1
        return goingon 
    else:
        device.count = 0
        lines.append(data)
        return success
        
#获取从发送AT命令  
def fuc_cmd(device,cmd):
    device.Send('+cmd:'+str(cmd))
    return success
    
#获取从发送命令带ctrl+z   
def fuc_cmdz(device,data):
    device.Send('+cmdz:'+str(data))
    return success

#重新断开，经过time秒后重新连接，从index开始测试     
def fuc_reset(device,time,index):
    device.Send('+exit:'+str(time)+','+str(index))
    return stop
    
    