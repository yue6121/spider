python�����������򣬰����ٶȺ��ѹ���py�ļ�λ��
ubuntu@10.11.35.201,/mnt/data/share/lmm
�ļ��������£�

1.  baidu.py
���ǰٶȵ�������򣬿��Կ�������̣��������һ���ܣ�,��Ŀ¼������
nohup python baidu.py > ./logs/baiduu1.log  2>&1 &
nohup python baidu.py > ./logs/baiduu2.log  2>&1 &
nohup python baidu.py > ./logs/baiduu3.log  2>&1 &
nohup python baidu.py > ./logs/baiduu4.log  2>&1 &
nohup python baidu.py > ./logs/baiduu5.log  2>&1 &
��ʾ����5�����̣���ʵ���Կ��ĸ��࣬��Ϊ�ٶȲ����������ص���ҳ��/mnt/data/share/lmm/baidu�£��Զ�����Ϊ�ļ��б���������������ҳ��
Mongo��Ϊdata.baidu

2.  sogou.py
�����ѹ��������������һ���˿ڻ����������Ŀǰֻ��һ��������
nohup python sogou.py > ./logs/sogou.log  2>&1 &
��������killall python�Ͱ����е����ܵ�python���̶�ɱ���ˣ����ص���ҳ��/mnt/data/share/lmm/sogou�£��Զ�����Ϊ�ļ��б���������������ҳ��
Mongo��Ϊdata.sogou

3.  parse_baidu.py
��baidu�ļ��������е���ҳ���½�����Mongo�⡣��Ϊdata.baidunew
nohup python parse_baidu.py 20160304 > ./logs/baidu1.log  2>&1 &
nohup python parse_baidu.py 20160305 > ./logs/baidu2.log  2>&1 &
                            ���������Ҫ�����baidu�ļ����µ��ļ�������
							
4.  parse_sogou.py
��sogou�ļ��������е���ҳ���½�����Mongo�⡣��Ϊdata.sogounew
nohup python parse_sogou.py 20160303 > ./logs/sogou1.log  2>&1 &
nohup python parse_sogou.py 20160304 > ./logs/sogou1.log  2>&1 &
                            ���������Ҫ�����sogou�ļ����µ��ļ�������
							
5.  sogou_insert.py
��mysqlץȡ������µ�δץȡ����ַ.
�޸�for qid in range(4075000,5075000):�е�4075000��5075000�Ϳ��Խ�����֮�����ַ����⡣

6.  baidu_insert.py
��mysqlץȡ������µ�δץȡ����ַ.
�޸�for qid in range(100,101100):�е�100��101100�Ϳ��Խ�����֮�����ַ����⡣
����baidu�з�ɢץȡ���ƣ�����������Բ��á�


ץȡ��ַMysql���ݿ�����.
���ݿ�λ��10.11.35.201:3306,�˺�root,����12345678.
1.  baidu
�ٶ���ַ���ݿ�Ϊspider.baidu,�ֶ�����:
use spider;
create table baidu(id bigint unsigned not null auto_increment,umd5 varchar(50) not null,url varchar(500) not null,spider bool, primary key(id)) default charset=utf8 ;
alter table baidu add unique(umd5);
alter table baidu add index index_name(spider);
2.  sogou
�Ͱٶ����ƣ�
use spider;
create table sogou(id int unsigned not null auto_increment,umd5 varchar(50) not null,url varchar(500) not null,spider bool, primary key(id)) default charset=utf8 ;
alter table sogou add unique(umd5);
alter table sogou add index index_name(spider);


��������Mongo���ݿ����
���ݿ�λ��10.11.35.201:27017
baidu������ҳ�������ݴ���data.baidunew,�����������data.baidu
sogou������ҳ�������ݴ���data.sougonew,�����������data.sogou


������ҳ���ֶ����ƣ�...��ʾ��ͬ��վ��ȡ�Ĳ�ͬ���֣�
{"_id":ObjectId,
"url":string,
"question_title":string,
"quetion_content":string,
"answers":[{"text":string,"quality":{"num_support":int,"num_oppose":int,"user_info":{"gradeIndex":int,"grAnswerNum":int,"goodRate":int,...},...}},{}....],
"similar_quetions":[string,string...],
"class_tag":string,
"insert_time":string,
"question_quality":{"ask_time":string,...}}




