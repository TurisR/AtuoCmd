'''
def fun(device,data,index)
device.print() :在log打印，在log文件中可以看出
device.Send(str):发送字符串str, 命令模式： +cmd:发送内容
                                       +cmdz:发送内容,会自动发送ctrl+z
                                       +exit:time,index 经过time秒后，测试第index条命令
                                       +urc:数据打印在AutoCMD工具中
data :为device返回的一行结果
index :表示当前执行命令的index

{
'cmd': 'ATE0', #命令名称
'fun': fun,    #命令处理函数
'succ': 'OK',  #成功结束命令标志，不定义，默认‘OK’
'err': 'ERROR',#错误结束命令标志,不定义，默认‘ERROR’
'quit': 'ERROR',#错误结束命令并退出测试标志，不定义，不进行检测处理
'time': 2,#延迟2秒发送该命令
'jump':-1#命令跳转，0为当前命令，-1为上一条命令，1为下一条指令，要结合自定义fun返回值jump使用，不定义默认为0
'arg' :fun传入参数
}
'''

import re, api

##AT+COPS?
def check_net(device, data, index):
    # +COPS: 0,2,"46011",7
    ret = api.fuc_handle(device, data, target='+COPS: 0,2')
    if ret == api.success:
        return api.success
    else:
        return api.fuc_retry(device, data, 10)

def check_mqtt_open(device, data, index):
    ret = api.fuc_handle(device, data, target='+MQTTOPEN:0,0')
    if ret == api.success:
        return api.success
    else:
        return api.fuc_retry(device, data, 0, succ='NULL')

def check_mqtt_login(device, data, index):
    ret = api.fuc_handle(device, data, target='MQTTCONN:0,0,0')
    if ret == api.success:
        return api.success
    else:
        return api.fuc_retry(device, data, 0, succ='NULL',send='+cmd:AT+MQTTCLOSE=0')

def update(device, data, index, time):
    ret = api.fuc_handle(device, data, target='OK')
    if ret == api.success:
        return api.fuc_reset(device, time, index + 1)
    else:
        return api.fuc_retry(device, data, 0)

def check_version(device, data, index, version):
    ret = api.fuc_handle(device, data, target=version)
    if ret == api.success:
        return api.success
    else:
        return api.fuc_retry(device, data, 0)


old_version = '2022.03.04_1230'
new_version = '2022.03.04_1830'
#ctwing
ct_url = '\"mqtt.ctwing.cn\"'
ct_port = 1883
ct_device_id = '\"15138225***\"'
ct_password = '\"6FEVlhR8qBlw8EWWlC4qKtj07OrdEUjqNnwt94VcM9Y\"'
ct_taskid = 3876

#命令列表
cmd_list = [{'cmd': 'ATE0'},
            {'cmd': 'AT+CGMR', 'fun': check_version, 'arg': old_version},
            {'cmd': 'AT+COPS?', 'fun': check_net, 'time': 2},
            # ctwing 
            {'cmd': 'AT+MQTTOPEN=0,{{ct_url}},{{ct_port}}', 'fun': check_mqtt_open, 'time': 2},
            {'cmd': 'AT+MQTTCONN=0,{{ct_device_id}},{{ct_device_id}},{{ct_password}}', 'time': 2, 'fun': check_mqtt_login},
            {'cmd': 'AT+CTWINGPOSTVER', 'fun': update, 'arg':180, 'time': 2},
            {'cmd': 'AT+CGMR', 'fun': check_version, 'arg': new_version},
            ]
