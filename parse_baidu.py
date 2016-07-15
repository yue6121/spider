# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 12:06:29 2016

@author: kk
"""

from pyquery import PyQuery as pq
import time
import os
import sys
from pymongo import MongoClient
import re

client = MongoClient('10.11.35.201', 27017)
db = client.data
col = db.baidunew


def parse_doc(dir_name,file_name):
    f = open(dir_name+'/'+file_name)
    try:
        content = f.read()
    finally:
        f.close()
    try:
    	doc = pq(content)
    except:
	print 'pq error'
	return
    url = 'http://zhidao.baidu.com/question/'+file_name

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
            quality['user_info']=users[answer_number]
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
            quality['user_info']=users[answer_number]
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
            quality['user_info']=users[answer_number]
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
            quality['user_info']=users[answer_number]
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
    insert_dic = {}
    if (question_title!='')or(question_content!=''):
        #insert_dict
        insert_dic['url'] = url
        insert_dic['class_tag'] = class_tag
        insert_dic['question_title'] = question_title
        insert_dic['question_content'] = question_content
        insert_dic['answers'] = answers
        insert_dic['insert_time'] = insert_time
        insert_dic['similar_questions'] = similar_questions
        insert_dic['question_quality'] = question_quality
        col.insert(insert_dic)


#dir_name='F:\\spider\\p2p\\baidu\\20160303'
dir_name='/mnt/data/share/lmm/baidu/'+sys.argv[1]
ii=0
for file_name in os.listdir(dir_name):
    ii = ii+1
    print ii,file_name
    try:
    	parse_doc(dir_name,file_name)
    except:
	print 'parse_doc error',ii,file_name
    
