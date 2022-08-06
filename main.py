from PyQt5 import QtCore, QtWidgets, QtGui
import sys, os, re

from view import Ui_MainWindow
from device import Communication, RecvThread
import utils
import time
from io import IOBase

from multiprocessing import Process
import subprocess

from setting_view_rc import Ui_setting_Dialog

from server import ServerThread

ip = '127.0.0.1'
port = 8889
test_cmd_index = 0
port_list = ['8889', '8888', '8887']
current_time = 0
time_step = 1000  # ms
time_step_s = int(time_step / 1000)


def get_time():
    timeStamp = int(time.time())
    # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
    timeArray = time.localtime(timeStamp)
    StyleTime = time.strftime("%Y_%m_%d_%H_%M_%S", timeArray)
    return StyleTime


def cmd_call(file_name, save_file, mode, check_err, times, test_cmd_index):
    # subprocess.call('python ./Palm-cmd/conn.py', creationflags=subprocess.CREATE_NEW_CONSOLE)
    cmd = 'python ./config/Palm-cmd/conn.py' + ' ' + str(port) + ' ' + str(check_err) + ' ' + str(times) + ' ' + str(
        test_cmd_index)
    if save_file:
        ret = subprocess.run(cmd, shell=True, check=True, capture_output=True)
        if ret.returncode == 0:
            f = open(file_name, mode)
            f.write(ret.stdout.decode('utf-8'))
            f.close()
    else:
        subprocess.run(cmd, shell=True, check=True, capture_output=False)
    # print(ret.stdout.decode('utf-8'))


class setting_window(QtWidgets.QDialog, Ui_setting_Dialog):
    def __init__(self):
        super(setting_window, self).__init__()
        self.setupUi(self)
        self.port_comboBox.setEditable(True)
        self.port_comboBox.addItems(port_list)
        # self.show()

    def reject(self):
        self.destroy()

    def accept(self):
        global port
        port = int(self.port_comboBox.currentText())
        print('port', port)
        self.destroy()


class mywindow(QtWidgets.QMainWindow, Ui_MainWindow, Communication):
    def __init__(self):
        super(mywindow, self).__init__()
        self.setupUi(self)
        self.refresh()
        self.file_name = ""
        self.log_file_name = ""
        self.cache_file_name = ''
        self.testRunIndex = 0
        self.write_mode = 'w'
        self.log_fd = object
        self.file_optionen_dir = os.getcwd()
        self.send_pushButton.setEnabled(False)
        self.startTest_pushButton.setEnabled(False)
        self.test_com = 'COM'

        self.bsp_comboBox.setEditable(True)
        # self.comboBox_3.setEditText('115200')
        self.bsp_comboBox.addItems(utils.bsp_list)  # 键、值反转
        self.testTimes_comboBox.setEditable(True)
        # self.comboBox_3.setEditText('115200')
        self.testTimes_comboBox.addItems(utils.test_times)  # 键、值反转
        self.fileDisplay_textEdit.setHidden(True)
        self.link_pushButton.clicked.connect(self.connect)
        self.send_pushButton.clicked.connect(self.send_data)
        self.clearDisplay_pushButton.clicked.connect(self.data_clear)
        self.startTest_pushButton.clicked.connect(self.test_option)
        self.selectFile_pushButton.clicked.connect(self.file_select)
        self.openFile_pushButton.clicked.connect(self.file_option)
        self.saveFile_pushButton.clicked.connect(self.file_save)
        self.refreah_pushButton.clicked.connect(self.refresh)
        self.actionport.triggered.connect(self.setting_show)
        self.clearsend_pushButton.clicked.connect(self.clear_at_send)
        self.testTimes_comboBox_2.addItems(utils.at_send_time)  # 键、值反转
        self.testTimes_comboBox_3.addItems(utils.at_cycle_times)  # 键、值反转
        self.testTimes_comboBox_2.setEditable(True)
        self.testTimes_comboBox_3.setEditable(True)
        self.timer_create()
        self.setWindowIcon(QtGui.QIcon('./config/AutoCMD.png'))

    def clear_at_send(self):
        self.cmd_lineEdit.clear()

    def timer_create(self):
        self.timer = QtCore.QTimer(self)  # 初始化一个定时器
        self.timer.setInterval(time_step)
        # self.timer.start()  # 设置计时间隔并启动；单位毫秒
        self.timer.timeout.connect(self.timer_operate)
        # self.timer.setSingleShot(False)
        # self.timer.singleShot(2000,self.timer_operate)

    def timer_operate(self):
        global current_time
        current_time -= 1
        # self.status_print('start test remain time ',current_time)
        self.status_print('start test remain time ' + str(current_time))
        if current_time == 0:
            if self.link_pushButton.text() == '连接':
                self.refresh()
                self.connect()
            self.timer.stop()
            self.send_pushButton.setEnabled(False)
            if self.link_pushButton.text() == '断开':
                self.start_test(False)
                # self.printf('start test')
            else:
                self.stop_test(True)

    def status_print(self, data):
        self.statusbar.showMessage(data)

    def setting_show(self):
        self.setting = setting_window()
        self.setting.show()

    def printf(self, mypstr):
        content = self.get_curr_time() + mypstr.replace('\r\n', '')
        self.display_textBrowser.append(content)
        self.cursor = self.display_textBrowser.textCursor()
        # 光标移到最后，这样就会自动显示出来
        self.display_textBrowser.moveCursor(self.cursor.End)
        QtWidgets.QApplication.processEvents()
        if isinstance(self.log_fd, IOBase) and self.isSavefile_checkBox.isChecked():
            # print('save')
            self.log_fd.write(content)
            self.log_fd.write('\n')

    def get_curr_time(self):
        timeStamp = int(time.time())
        # 转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
        now = time.strftime("[%H:%M:%S]", time.localtime())
        return now

    def refresh(self):
        ret, com_list = utils.init_com_list()
        self.com_comboBox.clear()
        if len(com_list) > 0:
            self.com_comboBox.addItems(com_list)
        else:
            self.com_comboBox.addItem('COM', 0)
            self.send_pushButton.setEnabled(False)
            self.startTest_pushButton.setEnabled(False)

    def init_log_cfg(self, file_name, _dir):
        fn = os.path.basename(file_name)
        fn = fn.split('.')[0]
        log_file_name = './' + _dir + '/' + fn + '_' + get_time() + '.txt'
        os.makedirs(os.path.dirname(log_file_name), exist_ok=True)
        return log_file_name

    def show_data(self, msg):
        if msg.find('+error:') != -1:
            print('send:', msg)
            self.device.Close()
            self.connect()
            time.sleep(1)
            # if self.startTest_pushButton.text() == '停止测试':
            #     self.stop_test(True)
            return
        if self.startTest_pushButton.text() == '停止测试':
            # print('send:',msg)
            self.server.Send(msg)
        msg = "->" + msg
        self.printf(msg)
        # time.sleep(0.3)

    def get_test_data(self, msg):
        # if self.checkBox_3.isChecked() and msg.find('+debug:'):
        # self.printf(msg)
        if msg.find('+cmd:') != -1:
            self.send_cmd(re.findall('\+cmd:(.+)', msg)[0])
        if msg.find('+cmdz:') != -1:
            self.send_cmdz(re.findall('\+cmdz:(.+)', msg)[0])

        # if  msg.find('+error:') != -1 :
        #    self.stop_test(True)
        if msg.find('+exit:') != -1:
            self.printf(msg)
            t = re.findall('\+exit:(.+)', msg)[0]
            ret = t.split(',')
            global current_time
            current_time = int(int(ret[0]) / time_step_s)
            if int(ret[0]) == 0:
                self.testRunIndex = int(ret[1])
                self.stop_test(True)
            else:
                global test_cmd_index
                test_cmd_index = int(ret[1])
                self.stop_test(False)
                self.test_com = self.com_comboBox.currentText()
                self.timer.start()
                self.send_pushButton.setEnabled(True)

        if msg.find('+urc:') != -1:
            self.printf(re.findall('\+urc:(.+)', msg)[0])

    # 定义槽函数
    def connect(self):
        if self.link_pushButton.text() == '连接':
            if self.startTest_pushButton.text() == '停止测试':
                com = self.test_com
                self.test_com = 'COM'
            else:
                com = self.com_comboBox.currentText()
            bsp = int(self.bsp_comboBox.currentText())
            ret, com_list = utils.init_com_list()
            if com == 'COM' or com not in  com_list:
                self.printf("no device connect...")
                return
            self.printf('open ' + com + ' with ' + str(bsp))
            self.device = Communication(com, bsp, 0.5)
            if self.device.get_status():
                # if self.recv_tread.get_status() == False :
                self.recv_tread = RecvThread(self.device)
                self.recv_tread.strOut.connect(self.show_data)
                self.recv_tread.Start()
                # self.printf("recv tread start...")
                self.printf("device connect success...")
                self.send_pushButton.setEnabled(True)
                self.startTest_pushButton.setEnabled(True)
                # self.status_print('link '+com+' with '+bsp+' success...')
                self.link_pushButton.setText("断开")
            else:
                self.printf("device disconnect...")
                # self.status_print('link ' + com + ' with ' + bsp + ' fail...')
        elif self.link_pushButton.text() == '断开':
            self.recv_tread.Stop()
            time.sleep(1)
            self.device.Close()
            self.link_pushButton.setText("连接")
            self.printf("device disconnect...")
            self.send_pushButton.setEnabled(False)
            self.startTest_pushButton.setEnabled(False)
            # self.status_print('device disconnect...')

    def send_cmd(self, cmd):
        self.printf("<-" + cmd)
        if self.isEnd_checkBox.isChecked() == False:
            cmd += '\r\n'
        self.device.Send_data(cmd)
        if self.isEnd_checkBox_2.isChecked() == True:
            self.device.Sendz()

    def send_cmdz(self, cmd):
        self.printf("<-" + cmd)
        self.device.Send_data(cmd)
        self.device.Sendz()

    def send_data(self):
        if self.link_pushButton.text() == '断开' and self.recv_tread.get_status() == True:
            cmd = self.cmd_lineEdit.text()
            sleep_times = int(self.testTimes_comboBox_2.currentText())
            cycle_times = int(self.testTimes_comboBox_3.currentText())
            if len(cmd) > 0:
                for i in range(cycle_times):
                    if sleep_times != 0:
                        time.sleep(sleep_times)
                    self.send_cmd(cmd)
            else:
                self.printf("no data to send")
        else:
            self.printf("device disconnect...")

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, u'提 示', u'确认退出？', QtWidgets.QMessageBox.Yes,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            if self.link_pushButton.text() == '断开':
                if self.recv_tread.get_status() == True:
                    self.recv_tread.Stop()
                    # time.sleep(1)
                    self.device.Close()
                self.link_pushButton.setText("连接")
                self.printf("device disconnect...")
                # time.sleep(1)
                if self.startTest_pushButton.text() == '停止测试':
                    self.stop_test(True)
            event.accept()
            sys.exit(0)
        else:
            event.ignore()

    def test_option(self):
        if self.startTest_pushButton.text() == '开始测试':
            self.start_test(True)
            self.status_print('test running...')
        elif self.startTest_pushButton.text() == '停止测试':
            self.stop_test(True)

    def start_test(self, isNewTest):
        self.file_name = self.file_textEdit.document().toPlainText()
        if self.file_name == '':
            self.printf("unselect file...")
            return
        if utils.copy_file(self.file_name) == False:
            self.printf("file open fail...")
            return
        self.server = ServerThread(ip, port)
        self.server.strOut.connect(self.get_test_data)
        self.server.Start()
        time.sleep(1)
        isSaveFile = self.isSavefile_checkBox.isChecked()

        if isNewTest:
            self.printf("start test:" + self.file_name)
            if isSaveFile:
                self.cache_file_name = self.init_log_cfg(self.file_name, 'cache')
                self.log_file_name = self.init_log_cfg(self.file_name, 'log')
                self.write_mode = 'w'
                self.log_fd = open(self.log_file_name, 'w')
            global test_cmd_index
            test_cmd_index = 0
        else:
            self.write_mode = 'a'
        test_times = int(self.testTimes_comboBox.currentText())
        check_err = self.isCheckErr_checkBox.isChecked()
        self.process = Process(target=cmd_call, args=(
        self.cache_file_name, isSaveFile, self.write_mode, check_err, test_times, test_cmd_index))
        # 启动子进程
        self.process.daemon = True
        try:
            _str = self.process.start()
            print('ret', _str)
        except Exception as e:
            self.printf("test fail...")
            return
        if isNewTest:
            if isSaveFile:
                self.printf("start test progress:" + 'index:' + str(test_cmd_index) + ",times:" + str(
                    test_times) + ',check_err:' + str(check_err) + ',log_file_name:' + self.log_file_name)
            else:
                self.printf("start test progress:" + 'index:' + str(test_cmd_index) + ",times:" + str(
                    test_times) + ',check_err:' + str(check_err))
        self.send_pushButton.setEnabled(False)
        self.isSavefile_checkBox.setEnabled(False)
        self.startTest_pushButton.setText('停止测试')
        self.status_print('test running start...')

    def stop_test(self, isEndTest):
        self.process.kill()
        time.sleep(0.5)
        self.server.Stop()
        if isEndTest:
            if self.timer.isActive():
                self.timer.stop()
                self.refresh()
                self.connect()
            self.printf("stop test progress:" + 'runIndex:' + str(self.testRunIndex))
            self.status_print('test running end...')
            if isinstance(self.log_fd, IOBase):
                # print('close')
                self.log_fd.close()
                self.log_fd = object
            self.send_pushButton.setEnabled(True)
            self.isSavefile_checkBox.setEnabled(True)
            self.startTest_pushButton.setText('开始测试')
        else:
            if self.recv_tread.get_status() == True:
                # self.recv_tread.Stop()
                # time.sleep(1)
                # self.device.Close()
                # self.link_pushButton.setText("连接")
                print('link')

    def data_clear(self):
        self.display_textBrowser.clear()

    def file_select(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择文件", self.file_optionen_dir, "test Files (*.py *.txt)")
        if file != "":
            self.file_name = file
            # self.printf("test file:"+self.file_name)
            self.file_textEdit.setText(self.file_name)

    def file_save(self):
        fileName = self.file_textEdit.document().toPlainText()
        if fileName == '':
            return
        content = self.fileDisplay_textEdit.document().toPlainText()
        # if content == '':
        #     return
        fd = open(fileName, "w", encoding='utf-8')
        fd.write(content)
        fd.close()

    def file_option(self):
        if self.openFile_pushButton.text() == '打开文件':
            fileName = self.file_textEdit.document().toPlainText()
            if fileName == '':
                return
            try:
                fd = open(fileName, "r", encoding='utf-8')
            except Exception as e:
                self.printf('file open fail...')
                return
            content = fd.read()
            fd.close()
            self.fileDisplay_textEdit.setHidden(False)
            self.fileDisplay_textEdit.setText(content)
            self.openFile_pushButton.setText('关闭文件')
        elif self.openFile_pushButton.text() == '关闭文件':
            self.fileDisplay_textEdit.close()
            self.fileDisplay_textEdit.setHidden(True)
            self.openFile_pushButton.setText('打开文件')


if __name__ == "__main__":
    # multiprocessing.freeze_support()
    app = QtWidgets.QApplication(sys.argv)
    window = mywindow()
    window.show()
    sys.exit(app.exec_())
