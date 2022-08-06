'''
功能： 发送指定AT命令到设备
'''
 
import serial
import time,sys
import serial.tools.list_ports
import re
from client import Client
import UserCode,api

success=0
stop = -2
goingon=-1



port = int(sys.argv[1])
check_err = sys.argv[2]
test_times = int(sys.argv[3])
test_cmd_index = int(sys.argv[4])

curr_cmd = ''
curr_cmd_index = 1

def at_cmd_parse(device,cmd):
    try:
        pattern = re.findall('{{(.+?)}}',cmd)
        #device.printf(pattern)
        new_cmd = cmd
        for item in pattern:
            new_cmd = new_cmd.replace('{{'+item+'}}',str(eval('UserCode.'+item)))
        #device.printf(new_cmd)
        return new_cmd
    except Exception as e:
        device.printf("异常报错："+e)
        return stop

def test(device,index,item):
    global curr_cmd
    if 'cmd' not in item:
        return stop
    curr_cmd = at_cmd_parse(device,item['cmd'])
    if curr_cmd == stop:
        device.printf("err：",e)
        return stop
    if 'time' in item:
        time.sleep(item['time'])
    device.printf("<-",curr_cmd)
    ret = device.Send("+cmd:"+curr_cmd)
    if ret == False:
        return stop
    fun_flag = 0
    device.init_param()
    while True:
        try:
            ret,data = device.Recv()
            if ret == False:
                return stop
            if data == "":
                continue
            if data != '\r\n' :
                device.printf("->",data.replace('\r\n',''))
                if fun_flag == 0 and 'fun' in item:
                    if 'arg' in item :
                        ret = item['fun'](device, data, index, item['arg'])
                    else:
                        ret = item['fun'](device,data, index)

                    if ret == api.stop:
                        return stop
                    elif ret == api.success:
                        #break
                        fun_flag=1
                        device.retry_count = 0
                    elif ret == api.jump:
                        global curr_cmd_index
                        if 'jump' in item:
                            curr_cmd_index = item['jump']
                        else:
                            curr_cmd_index = 0
                        #print('curr_cmd_index',curr_cmd_index)
                        return goingon
                    elif ret == api.next_cmd:
                        device.retry_count = 0
                        return success
                        
                if 'quit' in item:
                    if data.find(item['quit']) != -1 :
                        return stop
                if 'succ' in item:
                    if data.find(item['succ']) != -1 :
                        if 'fun' in item:
                            if fun_flag == 0:
                                return goingon
                            else:
                                return success
                        else:
                            return success
                else:
                    if data.find('OK') != -1 :
                        if 'fun' in item:
                            if fun_flag == 0:
                                return goingon
                            else:
                                return success
                        else:
                            return success
                        
                if 'err' in item:
                    if data.find(item['err']) != -1 :
                        return goingon
                else:
                    if data.find('ERROR') != -1 :
                        return goingon
        except Exception as e:
            device.printf("error：",e)
            return stop




def at_test(device,check_err,times) :
    err_num = 0
    err_list=[]

    global curr_cmd_index
    index = test_cmd_index
    device.printf('start test index:', index)
    cmd_list_len = len(UserCode.cmd_list)
    while index < cmd_list_len :
        ret = test(device, index, UserCode.cmd_list[index])
        if ret == goingon or ret == stop:
            err_num += 1
            err_list.append(curr_cmd)
            if check_err == False:
                ret = stop
                break
            elif  ret == stop:
                break
        #time.sleep(0.5)
        index += curr_cmd_index
        curr_cmd_index = 1
    if device.get_send_type() != 2:
        err_list = list(set(err_list))
        err_num = len(err_list)
        times += 1
        err_num_info = '[times:'+str(times)+']'+'err_num:'
        err_list_info = '[times:'+str(times)+']'+'err_list:'
        device.printf(err_num_info,err_num)
        device.printf(err_list_info,err_list)

        device.Send("+urc:"+err_num_info+str(err_num))
        device.Send("+urc:"+err_list_info+"["+','.join(err_list)+']')
    return ret



'''
if __name__ == "__main__" :
    print('port:',port)
    print('check_err:',check_err)
    print('test_times:',test_times)
    print('test_cmd_index:',test_cmd_index)

'''
if __name__ == "__main__" :
    device = Client()
    ret = device.Connect(port)
    device.printf('start connect:index:'+str(test_cmd_index)+',times:'+str(test_times))
    if ret:
        for i in range(test_times) :
            ret = at_test(device,check_err,i)
            if ret == stop :
                break
            #time.sleep(0.5)
        if device.get_send_type() != 2:
            device.printf('stop connect')
            device.Send("+exit:0,"+str(i+1))
        device.Close()
