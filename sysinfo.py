# coding:utf-8
import os
import time
import win32event, pywintypes, win32api
import sys
import socket
import psutil
import time
import pymssql
#以下是为了pyinstaller在打包的时候对于包含了pymssql包的exe能运行
import _mssql
import decimal
import uuid
_mssql.__version__
decimal.__version__
uuid.ctypes.__version__

#检测重复运行就退出
ERROR_ALREADY_EXISTS = 183
sz_mutex = "test_mutex"
hmutex = win32event.CreateMutex(None, pywintypes.FALSE,sz_mutex)
if (win32api.GetLastError() == ERROR_ALREADY_EXISTS):
    print("Program is running...")
    os.system('pause')
    sys.exit(0)
else:
    time.sleep(2)
    print ("Now program is starting...")

#系统信息
syslist = []
#硬盘分区信息
diskinfo = []
#达到阈值之后进行警告
warn = 70
#数据库连接
conn1 = pymssql.connect(host='10.1.0.5', user='sa', password='abcd12345678', database='test')
# conn1 = pymssql.connect(host='127.0.0.1', user='sa', password='abcd12345678', database='royalty')
cur1 = conn1.cursor(as_dict=True)

def get_host_ip():
    """
    查询本机ip地址,通过UDP封包的形式
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#获取系统信息
def Sysinfo():
    Boot_Start = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(psutil.boot_time()))
    syslist.append(Boot_Start)
    time.sleep(0.5)
    Cpu_usage = psutil.cpu_percent()
    syslist.append(Cpu_usage)
    RAM = int(psutil.virtual_memory().total / (1024 * 1024))
    syslist.append(RAM)
    RAM_percent = psutil.virtual_memory().percent
    syslist.append(RAM_percent)
    Net_sent = psutil.net_io_counters().bytes_sent / (1024 * 1024)
    syslist.append(Net_sent)
    Net_spkg = psutil.net_io_counters().packets_sent
    syslist.append(Net_spkg)
    Net_recv = psutil.net_io_counters().bytes_recv / (1024 * 1024)
    syslist.append(Net_recv)
    Net_rpkg = psutil.net_io_counters().packets_recv
    syslist.append(Net_rpkg)
    users_count = len(psutil.users())
    users_list = ",".join([u.name for u in psutil.users()])
    BFH = r'%'
    print("当前的IP地址为: ", get_host_ip())
    print("当前的主机名为: ", socket.gethostname())
    print("开机时间: ", Boot_Start)
    print(u"当前有%s个用户，分别是 %s" % (users_count, users_list))
    print("当前CPU使用率%s%s" % (Cpu_usage, BFH))
    print("物理内存：%dMB\t使用率：%s%s" % (RAM, RAM_percent, BFH))
    print("网卡发送：%d MB\t网卡发送包数：%d个" % (Net_sent, Net_spkg))
    print("网卡接收：%d MB\t网卡接收包数：%d个" % (Net_recv, Net_rpkg))
    # for net in psutil.net_if_addrs():
    #     print('网卡：', net)
    # print(psutil.disk_partitions())
    for sysdisk in psutil.disk_partitions():
        if sysdisk[3] != 'cdrom':
            print("磁盘:%s 总容量:%dG 剩余容量:%dG 磁盘使用率:%s%%" % \
                              (sysdisk[0], (psutil.disk_usage(sysdisk[1])[0]/(1024*1024*1024)), \
                               (psutil.disk_usage(sysdisk[1])[2]/(1024*1024*1024)), psutil.disk_usage(sysdisk[1])[3]))
    print()#增加空行

if __name__ == "__main__":
    while True:
        Sysinfo()
        ip = get_host_ip()
        logname = 'systemlog' + time.strftime("%Y-%m",time.localtime(time.time())) + '.log'
        sysdate = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time()))
        sysname = socket.gethostname()
        sysfile = open(logname, "a+")
        sysfile.write('\n----------------' + sysdate + '---------------\n')
        sysfile.write("当前的IP地址为：" + ip + '\n')
        sysfile.write("当前的主机名为：" + sysname + '\n')
        sysfile.write("开机时间：" + syslist[0] + '\n')
        sysfile.write("当前CPU使用率：" + str(syslist[1]) + '%' + '\n')
        sysfile.write("物理内存：%dMB\t物理内存使用率：%d%%\n" % (syslist[2],syslist[3]))
        sysfile.write("网卡发送:%dMB\t网卡发送包数:%d个\n" % (syslist[4],syslist[5]))
        sysfile.write("网卡接收:%dMB\t网卡接收包数:%d个\n" % (syslist[6],syslist[7]))
        disklist=0
        for disk in psutil.disk_partitions():
            #排除光驱
            if disk[3] != 'cdrom':
                diskname = disk[0]
                diskvol = psutil.disk_usage(disk[1])[0]/(1024*1024*1024)
                diskfree = psutil.disk_usage(disk[1])[2]/(1024*1024*1024)
                diskrate = psutil.disk_usage(disk[1])[3]
                sysfile.write("磁盘:%s 总容量:%dG 剩余容量:%dG 磁盘使用率:%s%%\n" % (diskname, diskvol, diskfree, diskrate))
                diskinfo.append([diskname, diskvol, diskfree, diskrate])
                # print(diskinfo[0][1])
                disklist = disklist + 1
        #系统当前支持5个分区信息，不足的会补0，超过5个分区会无法支持
        for i in range(0,5-disklist,1) :
            diskinfo.append([0,0,0,0])
        # print(diskinfo[4])
        #在此插入数据库
        cursql = "insert into server values('%s','%s','%s','%s',%s,%s,%s,%s,%s,%s,%s,'%s',%s,%s,%s,'%s',%s,%s,%s,\
        '%s',%s,%s,%s,'%s',%s,%s,%s,'%s',%s,%s,%s)" \
                 % (ip,sysdate,sysname,\
                    syslist[0],syslist[1],syslist[2],syslist[3],syslist[4],syslist[5],syslist[6],syslist[7], \
                    diskinfo[0][0], diskinfo[0][1], diskinfo[0][2], diskinfo[0][3], \
                    diskinfo[1][0], diskinfo[1][1], diskinfo[1][2], diskinfo[1][3], \
                    diskinfo[2][0], diskinfo[2][1], diskinfo[2][2], diskinfo[2][3], \
                    diskinfo[3][0], diskinfo[3][1], diskinfo[3][2], diskinfo[3][3], \
                    diskinfo[4][0], diskinfo[4][1], diskinfo[4][2], diskinfo[4][3])
        # print(cursql)
        cur1.execute(cursql)
        conn1.commit()
        sysfile.close()
        # if syslist[3] > warn:
        #     show_reminder()
        time.sleep(60)
