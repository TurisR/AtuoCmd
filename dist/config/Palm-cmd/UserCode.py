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
}
'''
import re, api

timeout = 10
# url = r'http://api.openweathermap.org/data/2.5/weather?q=shanghai&appid=c592e14137c3471fa9627b44f6649db4&mode=xml&units=metric'
url = 'http://www.baidu.com'
url_len = len(url)


def send_url(device, data, index):
    return api.fuc_handle(device, data, target='CONNECT', send='+cmdz:' + url)


def check(device, data, index, arg):
    ret = api.fuc_handle(device, data, target=arg)
    if ret == api.success:
        return api.next_cmd


# def check_GET(device,data,index) :
#     ret = api.fuc_handle(device,data,target='+HTTPGET:')
#     if ret == api.success:
#         return api.next_cmd


cmd_list = [{'cmd': 'AT+UMV'},
            {'cmd': 'ATE0'},
            {'cmd': 'AT+HTTPCFG=\"responseheader\",0'},
            {'cmd': 'AT+HTTPCFG=\"requestheader\",0'},
            {'cmd': 'AT+HTTPCFG=\"rspout/auto\",1'},
            # {'cmd': 'AT+CGATT=0'},
            # {'cmd': 'AT+CGDCONT=1,IPV4V6'},
            # {'cmd': 'AT+CGATT=1'},
            {'cmd': 'AT+CGPADDR', 'time': 2},
            {'cmd': 'AT+HTTPURL={{url_len}},{{timeout}}', 'fun': send_url, 'time': 5},
            # {'cmd':'AT+HTTPFILEDL=0','fun':check,'succ':'NULL','arg':'+HTTPFILEDL:'},
            {'cmd': 'AT+HTTPGET={{timeout}}', 'fun': check, 'succ': 'NULL', 'arg': '+HTTPGET:', 'time': 2},
            ]
