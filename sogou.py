# -*- coding: utf-8 -*-
"""
Created on Tue Mar 01 17:02:46 2016

@author: kk
"""

import MySQLdb
from pymongo import MongoClient
from pyquery import PyQuery as pq
import threading
import requests
import time
import os

server_ip = 'localhost'
client = MongoClient('10.11.35.201', 27017)
db = client.data
col = db.sogou

def parse(idd,url,content):
    #download
    download(content,url)
    doc = pq(content)

    #answers
    answers=[]
    for each in doc('.question-main.satisfaction-answer'):
        answer_c = pq(pq(each)('.answer-con')).text().encode('utf8')
        answer_c = answer_c.strip()
        answer_c = answer_c.replace('\r\n','').replace('\n','')
        if answer_c:
            quality={}
            quality['is_best']=True
            try:
                quality['num_support'] = int(pq(pq(each)('.operate-support')[0]).text())
                quality['num_oppose'] = int(pq(pq(each)('.operate-oppose')[0]).text())
            except:
                quality['num_support'] = -1
                quality['num_oppose'] = -1
            if pq(pq(each)('.user-name')):
                user = {}
                try:
                    user["uid"] = pq(pq(each)('.user-name')).attr("uid").encode('utf8')
                except:
                    user["uid"] = '-1'
                user["userName"] = pq(pq(each)('.user-name')[0]).text().encode('utf8')
                try:
                    user["gradeIndex"] = int(pq(pq(each)('.user-name')).attr("data-user-level"))
                except:
                    user["gradeIndex"] = -1
                quality['user_info'] = user
            answer = {"text":answer_c,"quality":quality}
            answers.append(answer)
    for each in doc('.default-answer'):
        answer_c = pq(pq(each)('.answer-con')).text().encode('utf8')
        answer_c = answer_c.strip()
        answer_c = answer_c.replace('\r\n','').replace('\n','')
        if answer_c:
            quality={}
            quality['is_best']=False
            try:
                quality['num_support'] = int(pq(pq(each)('.operate-support')[0]).text())
                quality['num_oppose'] = int(pq(pq(each)('.operate-oppose')[0]).text())
            except:
                quality['num_support'] = -1
                quality['num_oppose'] = -1
            if pq(pq(each)('.user-name')):
                user = {}
                try:
                    user["uid"] = pq(pq(each)('.user-name')).attr("uid").encode('utf8')
                except:
                    user["uid"] = '-1'
                user["userName"] = pq(pq(each)('.user-name')[0]).text().encode('utf8')
                try:
                    user["gradeIndex"] = int(pq(pq(each)('.user-name')).attr("data-user-level"))
                except:
                    user["gradeIndex"] = -1
                quality['user_info'] = user
            answer = {"text":answer_c,"quality":quality}
            answers.append(answer)
    
    #title
    question_title = doc("#questionTitle").text().encode('utf8')
    question_title = question_title.strip()
    question_title = question_title.replace('\r\n','').replace('\n','')
    #content
    question_content = doc(".question-con").text().encode('utf8')
    question_content = question_content.strip()
    question_content = question_content.replace('\r\n','').replace('\n','')
    #class_tag
    try:
        class_tag = content.split("</a><span class=\"time\">")[0]
        class_tag = class_tag.split("&ch=wty.wtfl\">")[1]
    except:
        return
    #insert_time
    insert_time = time.strftime('%Y-%m-%d %H:%M:%S')
    #question_quality
    question_quality={}
    ask_time=pq(doc('.question-info'))('.time').text().encode('utf8')
    question_quality['ask_time']=ask_time
    if (question_title!='')or(question_content!=''):
        #insert_dict
        insert_dic = {}
        insert_dic['url'] = url
        insert_dic['class_tag'] = class_tag
        insert_dic['question_title'] = question_title
        insert_dic['question_content'] = question_content
        insert_dic['answers'] = answers
        insert_dic['insert_time'] = insert_time
        insert_dic['question_quality'] = question_quality
        #插入mongo
        col.insert(insert_dic)

def download(content,url):
    #dirName = "./sogou/"+time.strftime('%Y%m%d')
    dirName = "/mnt/data/share/lmm/sogou/"+time.strftime('%Y%m%d')
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    fileName = dirName+"/"+url.split("http://wenwen.sogou.com/z/q")[1]
    f = open(fileName,'w')
    f.write(content)
    f.close()

def get_content(idd,url):
    #print 'xxxxxxxx'+url
    #start_1 = time.time()
    #time.sleep(0.3)
    try:
        r = requests.get(url,allow_redirects=False,timeout=15)
    except:
        print 'faild:',url
        #更新
        conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)
        cur = conn.cursor()
        update_str = "update sogou set spider=false where id ="+str(idd)
        cur.execute(update_str)
        cur.close()
        conn.commit()
        conn.close()
    else:
        if r.status_code==200:
            content = r.content
            parse(idd,url,content)
    #end = time.time()
    #print url,(end-start_1)
    


while(True):
    start = time.time()
    idds = []
    urls = []
    conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)
    cur = conn.cursor()
    select_str = "select id,url from sogou where spider=false limit 20 for update"
    aa = cur.execute(select_str)
    info = cur.fetchmany(aa)
    if len(info)==0:
        break
    for ii in info:
        idds.append(ii[0])
        urls.append(ii[1])
    for idd in idds:
        update_str = "update sogou set spider=true where id ="+str(idd)
        cur.execute(update_str)
    cur.close()
    conn.commit()
    conn.close()
    end = time.time()
    print 'select time: ',(end-start)

    threads = []
    for ii in range(0,len(urls)):
        t = threading.Thread(target=get_content,args=(idds[ii],urls[ii],))
        threads.append(t)
        time.sleep(0.2)
        t.start()
    for t in threads:
        t.join()
    end = time.time()
    print 'Once time: ',(end-start)

conn.close()
