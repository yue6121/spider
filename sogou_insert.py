# -*- coding: utf-8 -*-
"""
Created on Wed Mar 02 10:01:56 2016

@author: kk
"""

import MySQLdb
import md5

server_ip = '10.11.35.201'
conn= MySQLdb.connect(host=server_ip,port = 3306,user='root',passwd='12345678',db ='spider',)

for qid in range(4075000,5075000):
    url = "http://wenwen.sogou.com/z/q"+str(qid)+".htm"
    m1 = md5.new()   
    m1.update(url)   
    umd5 = m1.hexdigest()
    cur = conn.cursor()
    insert_str = "insert ignore into sogou values(null,\""+umd5+"\",\""+url+"\",false)"
    aa = cur.execute(insert_str)
    cur.close()
    conn.commit()
    print url,aa
    

conn.close()
