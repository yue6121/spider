# -*- coding: utf-8 -*-
"""
Created on Mon Mar 28 17:30:36 2016

@author: kk
"""

from pyquery import PyQuery as pq
import time
import os
import sys
from pymongo import MongoClient

client = MongoClient('10.11.35.201', 27017)
db = client.data
col = db.sogounew


def parse_doc(dir_name,file_name):
    f = open(dir_name+'/'+file_name)
    try:
        content = f.read()
    finally:
        f.close()
    doc = pq(content)
    url = 'http://wenwen.qq.com/z/q'+file_name

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
        col.insert(insert_dic)


#dir_name='F:\\spider\\p2p\\sogou\\20160314'
dir_name='/mnt/data/share/lmm/sogou/'+sys.argv[1]
ii=0
for file_name in os.listdir(dir_name):
    ii = ii+1
    print ii,file_name
    try:
    	parse_doc(dir_name,file_name)
    except:
	print 'parse_doc error',ii,file_name
