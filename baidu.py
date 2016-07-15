# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 14:01:17 2016

@author: kk
"""

import MySQLdb
from pymongo import MongoClient
import md5
from pyquery import PyQuery as pq
import threading
import requests
import time
import os
import re
import warnings
warnings.filterwarnings("ignore")

server_ip = 'localhost'
client = MongoClient('10.11.35.201', 27017)
db = client.data
col = db.baidu

conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)
url = "http://zhidao.baidu.com"
m1 = md5.new()
m1.update(url)
umd5 = m1.hexdigest()
cur = conn.cursor()
insert_str = "insert ignore into baidu values(null,\""+umd5+"\",\""+url+"\",false)"
aa = cur.execute(insert_str)
cur.close()
conn.commit()
conn.close()

def parse(idd,url,content):
    doc = pq(content)
    #先提取网址
    for each in doc("a"):
        url_add = doc(each).attr('href')
        if url_add and (url_add.startswith('/')):
            url_add = "http://zhidao.baidu.com" +url_add
        if url_add and (".html" in url_add):
            url_add = url_add.split(".html")[0]+".html"
        #if url_add and ((url_add.startswith("http://zhidao.baidu.com/question/")) or (url_add.startswith("http://zhidao.baidu.com/browse/")) or (url_add.startswith("http://zhidao.baidu.com/business/")) or (url_add.startswith("http://zhidao.baidu.com/business/")) or (url_add.startswith("http://zhidao.baidu.com/hangjia/")) or (url_add.startswith("http://zhidao.baidu.com/list/")) or (url_add.startswith("http://zhidao.baidu.com/search?word=")) or (url_add.startswith("http://zhidao.baidu.com/zt/"))):
        if url_add and (url_add.startswith("http://zhidao.baidu.com/question/")) and (url_add.endswith(".html")):
            #符合条件插入到Mysql
            url_add=url_add.encode('utf8')
            m1 = md5.new()   
            m1.update(url_add)   
            umd5 = m1.hexdigest()
            conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)
            cur = conn.cursor()
            insert_str = "insert ignore into baidu values(null,\""+umd5+"\",\""+url_add+"\",false)"
            cur.execute(insert_str)
            cur.close()
            conn.commit()
            conn.close()
    #如果是问题页，添加解析
    if ("http://zhidao.baidu.com/question/" in url) and (".html" in url) and ("class=\"ask-title \"" in content):
        #user_info
        pattern = re.compile(r'= {(.+)};')
        match = pattern.findall(content)
        users = []
        for i in range(0,len(match)):
            user = {}
            pattern_u = re.compile(r'hasComment:"(\d)",')
            if pattern_u.search(match[i]):
                match_u = pattern_u.search(match[i]).groups()[0]
                user['hasComment'] = match_u
            pattern_u = re.compile(r'isAnonymous:"(\d)",')
            if pattern_u.search(match[i]):
                match_u = pattern_u.search(match[i]).groups()[0]
                user['isAnonymous'] = match_u
            else:
                continue
            if match_u=='0':
                pattern_u = re.compile(r'sex:"(\d)",')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['sex'] = match_u
                pattern_u = re.compile(r'isFamous:"(\d)",')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['isFamous'] = match_u
                pattern_u = re.compile(r'gradeIndex:"(\d+)",')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['gradeIndex'] = int(match_u)
                pattern_u = re.compile(r'grAnswerNum:"(\d+)",')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['grAnswerNum'] = int(match_u)
                else:
                    user['grAnswerNum'] = 0
                pattern_u = re.compile(r'goodRate:"(\d+)"')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['goodRate'] = int(match_u)
                else:
                    user['goodRate'] = 0
                pattern_u = re.compile(r'uid:"(\d+)"')
                if pattern_u.search(match[i]):
                    match_u = pattern_u.search(match[i]).groups()[0]
                    user['uid'] = match_u
                pattern_u = re.compile(r'userName:"(\S+)",userNameEnc')
                if pattern_u.search(match[i]):
                    try:
                        match_u = pattern_u.search(match[i].decode('gbk').encode('utf8')).groups()[0]
                        user['userName'] = match_u
                    except:
                        print url,'cannot decode'
            users.append(user)
        
        #answers
        answers = []
        answer_number=0
        if len(doc(".line .content"))==len(users):
            is_eaqul = True
        else:
            is_eaqul = False
        for each in doc(".line .content"):
            answer_c = pq(each)(".best-text").text().encode('utf8')
            answer_c = answer_c.strip()
            answer_c = answer_c.replace('\r\n','').replace('\n','')
            if answer_c:
                quality={}
                quality['is_best']=True
                bgnums = []
                for each in pq(each)(".evaluate"):
                    bgnum = pq(each).attr('data-evaluate')
                    bgnums.append(int(bgnum))
                if(len(bgnums)==2):
                    quality['num_support']=bgnums[0]
                    quality['num_oppose']=bgnums[1]
                else:
                    if is_eaqul:
                        quality['num_support'] = -1
                        quality['num_oppose'] = -1
                    else:
                        continue
                try:
                    quality['user_info']=users[answer_number]
                except:
                    print url,'list index out of range'
                answer = {"text":answer_c,"quality":quality}
                answers.append(answer)
                answer_number = answer_number+1
                continue
            #
            answer_c = pq(each)(".quality-content").text().encode('utf8')
            answer_c = answer_c.strip()
            answer_c = answer_c.replace('\r\n','').replace('\n','')
            if answer_c:
                quality={}
                quality['is_best']=True
                bgnums = []
                for each in pq(each)(".evaluate"):
                    bgnum = pq(each).attr('data-evaluate')
                    bgnums.append(int(bgnum))
                if(len(bgnums)==2):
                    quality['num_support']=bgnums[0]
                    quality['num_oppose']=bgnums[1]
                else:
                    if is_eaqul:
                        quality['num_support'] = -1
                        quality['num_oppose'] = -1
                    else:
                        continue
                try:
                    quality['user_info']=users[answer_number]
                except:
                    print url,'list index out of range'
                answer = {"text":answer_c,"quality":quality}
                answers.append(answer)
                answer_number = answer_number+1
                continue
            #
            answer_c = pq(each)(".recommend-text").text().encode('utf8')
            answer_c = answer_c.strip()
            answer_c = answer_c.replace('\r\n','').replace('\n','')
            if answer_c:
                quality={}
                quality['is_best']=True
                bgnums = []
                for each in pq(each)(".evaluate"):
                    bgnum = pq(each).attr('data-evaluate')
                    bgnums.append(int(bgnum))
                if(len(bgnums)==2):
                    quality['num_support']=bgnums[0]
                    quality['num_oppose']=bgnums[1]
                else:
                    if is_eaqul:
                        quality['num_support'] = -1
                        quality['num_oppose'] = -1
                    else:
                        continue
                try:
                    quality['user_info']=users[answer_number]
                except:
                    print url,'list index out of range'
                answer = {"text":answer_c,"quality":quality}
                answers.append(answer)
                answer_number = answer_number+1
                continue
            #
            answer_c = pq(each)(".con").text().encode('utf8')
            answer_c = answer_c.strip()
            answer_c = answer_c.replace('\r\n','').replace('\n','')
            if answer_c:
                quality={}
                quality['is_best']=False
                bgnums = []
                for each in pq(each)(".evaluate"):
                    bgnum = pq(each).attr('data-evaluate')
                    bgnums.append(int(bgnum))
                if(len(bgnums)==2):
                    quality['num_support']=bgnums[0]
                    quality['num_oppose']=bgnums[1]
                else:
                    if is_eaqul:
                        quality['num_support'] = -1
                        quality['num_oppose'] = -1
                    else:
                        continue
                try:
                    quality['user_info']=users[answer_number]
                except:
                    print url,'list index out of range'
                answer = {"text":answer_c,"quality":quality}
                answers.append(answer)
                answer_number = answer_number+1
                continue

        #title
        question_title = doc(".ask-title").text().encode('utf8')
        question_title = question_title.strip()
        question_title = question_title.replace('\r\n','').replace('\n','')
        #content
        question_content = doc(".q-content").text().encode('utf8')
        question_content = question_content.strip()
        question_content = question_content.replace('\r\n','').replace('\n','')
        #class_tag
        class_tag = ""
        tag_flag = 0
        for each in doc(".question-tag-link"):
            tag = pq(each).text().encode('utf8')
            tag = tag.strip()
            tag = tag.replace('\r\n','').replace('\n','')
            if tag_flag==0:
                if tag:
                    class_tag = tag
                    tag_flag = tag_flag + 1
            else:
                if tag:
                    class_tag = class_tag + ',' + tag
        #insert_time
        insert_time = time.strftime('%Y-%m-%d %H:%M:%S')
        #similar_quetions
        similar_questions=[]
        for each in doc(".related-link"):
            similar_question = pq(each).remove('.ml-5').text().encode('utf8').replace(' ','')
            similar_questions.append(similar_question)
        #question_quality
        question_quality={}
        ask_time=doc(".ask-time").remove('.accuse-enter').remove('.f-pipe').text().encode('utf8')
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
            insert_dic['similar_questions'] = similar_questions
            insert_dic['question_quality'] = question_quality
            #插入mongo
            col.insert(insert_dic)
            #download
            download(content,url)

def download(content,url):
    #dirName = "./baidu/"+time.strftime('%Y%m%d')
    dirName = "/mnt/data/share/lmm/baidu/"+time.strftime('%Y%m%d')
    if not os.path.exists(dirName):
        os.mkdir(dirName)
    fileName = dirName+"/"+url.split("/question/")[1]
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
        print 'faild',url
        #更新
        conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)
        cur = conn.cursor()
        update_str = "update baidu set spider=false where id ="+str(idd)
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
    select_str = "select id,url from baidu where spider=false limit 20 for update"
    aa = cur.execute(select_str)
    info = cur.fetchmany(aa)
    if len(info)==0:
        break
    for ii in info:
        idds.append(ii[0])
        urls.append(ii[1])
    for idd in idds:
        update_str = "update baidu set spider=true where id ="+str(idd)
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
        #time.sleep(0.001)
        t.start()
    for t in threads:
        t.join()
    end = time.time()
    print 'Once time: ',(end-start)

conn.close()
