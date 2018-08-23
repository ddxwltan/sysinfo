import pymssql
import datetime
import time
import xlsxwriter
print('服务器报表抓取程序 v1.0\n')
'''
输出数据库中任意一张表，生成Excel2007文件，大于100万会新生成一个excel文件
#定义数据库连接的常量
# 数据库地址curhost
#数据库登陆名curuser
#数据库密码curpassword
#数据库库名curdatabase
#表名tablename
#输出Excel文件名filename
#导出截止时间date
'''
def excel2007(curhost,curuser,curpassword,curdatabase,tablename,filename,date):
    conn1 =  pymssql.connect(host=curhost, user=curuser, password=curpassword, database=curdatabase)
    cur1 = conn1.cursor(as_dict=True)
    #执行数据库查询
    cursql = "select * from %s where date > '%s'" %(tablename,date)
    cur1.execute(cursql)
    print('开始输出Excel,开始时间为',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    #新建Excel对象，指定输出文件的名字和路径，再新建一个sheet，定义格式为加粗
    wb = xlsxwriter.Workbook('%s1.xlsx'%filename)
    ws = wb.add_worksheet()
    style0 = wb.add_format({'bold':1})
    #定义sheet序号和行序号
    pagenum = 2
    rowindex = 2
    #开始对每一行数据进行输出
    for row in cur1:
        if(rowindex % 10000 == 0):
            print('现在已输出%s行' %rowindex,time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        #组合出每一行的输出起始位置
        lineindex = 'A'+str(rowindex)
        #第一行输出表头
        ws.write_row('A1', row.keys(),style0)
        #以行为单位输出数据
        ws.write_row(lineindex, row.values())
        #超出Excel2007限制，新建一个excel继续输出剩下的数据
        if (rowindex % 1048575 == 0):
            wb.close()
            wb = xlsxwriter.Workbook('%s%s.xlsx'%(filename,pagenum))
            ws = wb.add_worksheet()
            rowindex = 2
            pagenum = pagenum + 1
        rowindex = rowindex + 1
    #关闭文件，完成输出
    wb.close()
    print('输出结束，请查看文件，结束时间为',time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
    cur1.close()
    conn1.close()

def datetime_offset_by_month(datetime1, n=1):
    one_day = datetime.timedelta(days=1)
    q, r = divmod(datetime1.month + n, 12)
    datetime2 = datetime.datetime(datetime1.year + q, r + 1, 1) - one_day
    if (datetime1.month != (datetime1 + one_day).month):
        return datetime2
    if (datetime1.day >= datetime2.day):
        return datetime2
    return datetime2.replace(day=datetime1.day)

curhost = '10.1.0.5'
curuser = 'serverinf'
curpassword = 'mtbookserver911..'
curdatabase = 'test'
tablename = 'server'
filename = 'serverinfo'

now = datetime.datetime.now()
# 导出过去三个月的数据
date = datetime_offset_by_month(now, n=-3)

excel2007(curhost,curuser,curpassword,curdatabase,tablename,filename,date)