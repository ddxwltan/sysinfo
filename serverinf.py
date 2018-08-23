# coding: utf-8
import os
import sys
import win32event, pywintypes, win32api
import time
import xlrd
import datetime
import getpass
import pymssql
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL

#以下是为了pyinstaller在打包的时候对于包含了pymssql包的exe能运行
import _mssql
import decimal
import uuid
_mssql.__version__
decimal.__version__
uuid.ctypes.__version__
print('服务器信息监测程序 v1.0\n')
#检测重复运行就退出
ERROR_ALREADY_EXISTS = 183
sz_mutex = "sysmail"
hmutex = win32event.CreateMutex(None, pywintypes.FALSE,sz_mutex)
if (win32api.GetLastError() == ERROR_ALREADY_EXISTS):
    print("程序已经运行，请退出之后重新运行。")
    os.system('pause')
    sys.exit(0)
else:
    print("程序即将运行，请等待……")
    time.sleep(2)

conn1 = pymssql.connect(host='10.1.0.5', user='serverinf', password='mtbookserver911..', database='test')
# conn1 = pymssql.connect(host='127.0.0.1', user='sa', password='abcd12345678', database='royalty')
cur1 = conn1.cursor(as_dict=True)

def get_xls_data(xlsxname, sheetindex):
    dataresult = []  # 保存从excel表中读取出来的值，每一行为一个list，dataresult中保存了所有行的内容
    result = []  # 是由dict组成的list，是将dataresult中的内容全部转成字典组成的list：result
    # datapath = data_path + '\\' + xlsname
    xls1 = xlrd.open_workbook(xlsxname)
    table = xls1.sheet_by_index(sheetindex)
    for i in range(0, table.nrows):
        dataresult.append(table.row_values(i))
    # 将list转化成dict
    for i in range(1, len(dataresult)):
        temp = dict(zip(dataresult[0], dataresult[i]))
        result.append(temp)
    return result

def warlingmail(psd,subject,text):
    # 设置smtplib所需的参数
    # 下面的发件人，收件人是用于邮件传输的。
    smtpserver = 'smtp.exmail.qq.com'
    username = 'itserver2@xiron.net.cn'
    password = psd
    sender = 'itserver2@xiron.net.cn'
    receiver = ['chengxi@xiron.net.cn']

    msg = MIMEMultipart('mixed')
    msg['Subject'] = subject
    msg['From'] = 'itserver2@xiron.net.cn<itserver2@xiron.net.cn>'
    msg['To'] = ";".join(receiver)
    text_plain = MIMEText(text, 'plain', 'utf-8')
    msg.attach(text_plain)

    #SSL模式发送邮件
    smtp = SMTP_SSL(smtpserver)
    smtp.ehlo(smtpserver)
    # smtp.set_debuglevel(1)
    '''
    登陆成功会返回：(235, b'Authentication successful')
    '''
    if smtp.login(username, password)[0] == 235:
        smtp.sendmail(sender, receiver, msg.as_string())
        return 'Send mail Success!'
    else:
        return 'Logoin Failed!'

'''
计算2个时间的差值，并返回秒
'''
def failtime(date1,date2):
    temp1 = time.strptime(str(date1), "%Y-%m-%d %H:%M:%S")
    temp2 = time.strptime(str(date2), "%Y-%m-%d %H:%M:%S")
    d1 = datetime.datetime(temp1[0], temp1[1], temp1[2], temp1[3], temp1[4], temp1[5])
    d2 = datetime.datetime(temp2[0], temp2[1], temp2[2], temp2[3], temp2[4], temp2[5])
    return (d2-d1).total_seconds()

#密码抓取，密码存放在数据库中
sql = "select password from server where ip = '0.0.0.0'"
cur1.execute(sql)
datapsd = cur1.fetchall()
if datapsd == []:
    print('请确认在内网运行本程序！')
    sys.exit(0)

#密码验证
count = 0
while count < 3:
    pasd = getpass.getpass()
    # pasd = input('password:')
    if pasd != datapsd[0]['password']:
        count = count +1
        print("密码错误，请重新输入：\n")
    elif pasd == datapsd[0]['password']:
        print("密码验证成功！")
        break
if count >= 3:
    print('密码错误次数太多，请确认后再运行软件！')
    sys.exit(0)

if __name__ == "__main__":
    while True:
        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
        print(now + ": checking is starting……")
        gate = get_xls_data('servinfo.xlsx', 0)
        for ip in gate:
            if ip['on/off'] == 0:
                print(now + ': ' + ip['serverip'] + '：跳过检测此服务器！')
                continue
            elif ip['on/off'] == 1:
                # querysql = "select ip,date from server where date > '%s' order by date desc"%('2018-08-21')
                querysql = "select * from server where ip = '%s' order by date desc" % (ip['serverip'])
                cur1.execute(querysql)
                servinfo = cur1.fetchall()
                if servinfo != []:
                    # 检测硬盘占用率
                    hr = ip['hddrate']*100
                    if  servinfo[0]['diskrate1'] >= hr or servinfo[0]['diskrate2'] >= hr or servinfo[0]['diskrate3'] >= hr or\
                        servinfo[0]['diskrate4'] >= hr or servinfo[0]['diskrate5'] >= hr:
                        hddrate = []
                        hddrate.append(str(servinfo[0]['diskrate1']) + '%')
                        hddrate.append(str(servinfo[0]['diskrate2']) + '%')
                        hddrate.append(str(servinfo[0]['diskrate3']) + '%')
                        hddrate.append(str(servinfo[0]['diskrate4']) + '%')
                        hddrate.append(str(servinfo[0]['diskrate5']) + '%')
                        breakinfo = "硬盘空间超出了阈值限制"
                        text = "系统管理员：\n    请注意：Server  %s %s 请立即查看，硬盘使用量为：%s" %(ip['serverip'],breakinfo,str(hddrate))
                        subject = ip['serverip'] + ' HDD used rate is too high! Please check!!'
                        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        print(now + ': Server ' + ip['serverip'] + " 硬盘使用量超过阈值，请立即查看!!!")
                        # 发邮件
                        print(now + ': ' + warlingmail(pasd,subject, text))

                    # 检测CPU占用率
                    if servinfo[0]['cpurate'] >= ip['cpurate']*100:
                        breakinfo = "CPU使用量超出了阈值限制"
                        text = "系统管理员：\n    请注意：Server %s %s 请立即查看，CPU使用量为：%s%%" %(ip['serverip'],breakinfo,servinfo[0]['cpurate'])
                        subject = ip['serverip'] + ' CPU used rate is too high! Please check!!'
                        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        print(now + ': Server ' + ip['serverip'] + " CPU使用量超过阈值，请立即查看!!!")
                        # 发邮件
                        print(now + ': ' + warlingmail(pasd,subject, text))

                    #检测内存占用率
                    if servinfo[0]['memrate'] >= ip['memrate']*100:
                        breakinfo = "内存使用量超出了阈值限制"
                        text = "系统管理员：\n    请注意：Server %s %s 请立即查看，内存使用量为：%s%%"%(ip['serverip'],breakinfo,servinfo[0]['memrate'])
                        subject = ip['serverip'] + ' Memery used rate is too high! Please check!!'
                        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                        print(now + ': Server ' + ip['serverip'] + " 内存使用量超过阈值，请立即查看!!!")
                        # 发邮件
                        print(now + ': ' + warlingmail(pasd,subject, text))

                # 检测离线时间
                if servinfo == []:
                    onlinetime = "2001-09-11 08:20:00"
                    breaktime = failtime(onlinetime, now)
                else:
                    onlinetime = servinfo[0]['date']
                    breaktime = failtime(servinfo[0]['date'],now)
                if breaktime > ip['offline']:
                    ft = {'days': '0', 'hours': '0', 'mins': '0', 'secs': '0'}
                    ft['mins'], ft['secs'] = divmod(breaktime, 60)
                    ft['hours'], ft['mins'] = divmod(ft['mins'], 60)
                    ft['days'], ft['hours'] = divmod(ft['hours'], 24)
                    breakinfo = "已经掉线%d天%d小时%d分%d秒" % (ft['days'], ft['hours'], ft['mins'], ft['secs'])
                    text = "系统管理员：\n    请注意：Server %s %s 请立即查看，最后一次在线时间为：%s%%"%(ip['serverip'],breakinfo,onlinetime)
                    subject = ip['serverip'] + ' is Failed! Please check!!'
                    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                    print(now + ': Server ' + ip['serverip'] + " is missing!!!")
                    #发邮件
                    print(now + ': ' + warlingmail(pasd,subject, text))
        time.sleep(600)