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
#define
success = 0
goningon = 1
stop = 2
jump =3
##userCode

time_out = 10
url = 'http://www.360.com'
url_len = len(url)
def fun(device,data,index) :
    if data.find('CONNECT') !=-1:
        ret = device.Send("+cmdz:"+url)
        if ret == False:
            return stop
        else:
            return success
    else:
        #条件未满足，继续监听
        return goningon



cmd_list = [{'cmd':'ATE0'},
            {'cmd':'AT + HTTPURL = {{url_len}}, {{time_out}}','fun':fun,'time':2}
            ]

