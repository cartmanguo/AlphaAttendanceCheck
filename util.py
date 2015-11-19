#!/usr/bin/env python3
__author__ = 'randy'
import sys
import getopt
import urllib
import http.cookiejar
import logging
import requests
from bs4 import BeautifulSoup
cookie = http.cookiejar.CookieJar()                                        #保存cookie，为登录后访问其它页面做准备
cjhdr  =  urllib.request.HTTPCookieProcessor(cookie)
opener = urllib.request.build_opener(cjhdr)
sessionid_key = 'ASP.NET_SessionId'
emp_code_key = 'EMPCDCODE'
class AttendenceRecord:
    def __init__(self,date,name,status,first_record,last_record):
        self.date = date
        self.name = name
        self.status = status
        self.first_record = first_record
        self.last_record = last_record
def Usage():
    print('使用方法:')
    print('-h: print help message.')
    print('-u user -p password: get attendence data')
def main():
    username = None
    password = None
    opts, args = getopt.getopt(sys.argv[1:], 'hu:p:')
    for op,value in opts:
        if op == '-u':
            username = value
        elif op == '-p':
            password = value
        elif op == '-h':
            Usage()
            exit()
    if username == None:
        print('-u is missing')
        exit()
    elif password == None:
        print('-p is missing')
        exit()
    login(username,password)

def login(user,password):
    try:
        url = "http://intra.cn.alphanetworks.com/login.aspx"
        headers = {'Connection':'Keep-Alive','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ,'Accept-Encoding':'gzip,deflate','Origin':'http://intra.cn.alphanetworks.com'
        ,'Referer':'http://intra.cn.alphanetworks.com/login.aspx','Accept-Language':'zh-cn'
        ,'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56'}
        postdata = {'gotologin':'','UserName': user, 'PassWord': password,
                                   '__VIEWSTATEGENERATOR':'C2EE9ABB',
                                   '__VIEWSTATE':'/wEPDwUINzM4MDQ0MjhkZHjkV3tZEENqFJ6MRGfYl1nhKBFP',
                                   '__EVENTVALIDATION':'/wEWBALzsqWHDwKvruq2CAKyxeCRDwKPpIuUD7cUJb1HG59eyFbHjq3DGdt/WgQ2'}
        session = requests.Session()
        res = session.post(url,headers=headers,data=postdata)
        if res.status_code == 200:
            #print(res.headers,res.status_code,session.cookies.get_dict())
            mycookie = session.cookies.get_dict()
            getAttendenceRecords(mycookie)
    except Exception as e:
        logging.exception(e)

def getAttendenceRecords(my_cookie):
    session = requests.Session()
    session_id = my_cookie[sessionid_key]
    emp_code = my_cookie[emp_code_key]
    cookievalue = sessionid_key+'='+session_id+';'+emp_code_key+'='+emp_code
    url = "http://intra.cn.alphanetworks.com/ATT_List.aspx"
    headers = {'Connection':'Keep-Alive','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        ,'Accept-Encoding':'gzip,deflate','Origin':'http://intra.cn.alphanetworks.com'
        ,'Referer':'http://intra.cn.alphanetworks.com/login.aspx','Accept-Language':'zh-cn'
        ,'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56'
               ,'Cookie':cookievalue}
    recordlist = []
    res = session.get(url,headers=headers)
    soup = BeautifulSoup(res.text,'html.parser')
    records = soup.find_all('tr',attrs={'class':'GridRow_Office2007'})
    for tr in records:
        date = tr.find('a').string
        td = tr.find_all('td')
        record = AttendenceRecord(date,td[1].string.strip(),td[2].find('span').string.strip(),td[3].string.strip(),td[4].string.strip())
        recordlist.append(record)
    records = soup.find_all('tr',attrs={'class':'GridAltRow_Office2007'})
    for tr in records:
        date = tr.find('a').string
        td = tr.find_all('td')
        record = AttendenceRecord(date,td[1].string.strip(),td[2].find('span').string.strip(),td[3].string.strip(),td[4].string.strip())
        recordlist.append(record)
    recordlist.sort(key=lambda r:r.date,reverse=False)
    for record in recordlist:
        print(record.date,record.name,record.status,record.first_record,record.last_record)

if __name__ == '__main__':
    main()