python代码的爬虫程序，包括百度和搜狗，py文件位于
ubuntu@10.11.35.201,/mnt/data/share/lmm
文件介绍如下：

1.  baidu.py
这是百度的爬虫程序，可以开启多进程（多个程序一起跑）,在目录下运行
nohup python baidu.py > ./logs/baiduu1.log  2>&1 &
nohup python baidu.py > ./logs/baiduu2.log  2>&1 &
nohup python baidu.py > ./logs/baiduu3.log  2>&1 &
nohup python baidu.py > ./logs/baiduu4.log  2>&1 &
nohup python baidu.py > ./logs/baiduu5.log  2>&1 &
表示开启5个进程，其实可以开的更多，因为百度不封网，下载的网页在/mnt/data/share/lmm/baidu下，自动以天为文件夹保存所有爬过的网页。
Mongo表为data.baidu

2.  sogou.py
这是搜狗的爬虫程序，由于一个端口会封网，所以目前只开一个进程跑
nohup python sogou.py > ./logs/sogou.log  2>&1 &
定期清理，killall python就把所有的在跑的python进程都杀死了，下载的网页在/mnt/data/share/lmm/sogou下，自动以天为文件夹保存所有爬过的网页。
Mongo表为data.sogou

3.  parse_baidu.py
将baidu文件夹下所有的网页重新解析入Mongo库。表为data.baidunew
nohup python parse_baidu.py 20160304 > ./logs/baidu1.log  2>&1 &
nohup python parse_baidu.py 20160305 > ./logs/baidu2.log  2>&1 &
                            这个是输入要处理的baidu文件夹下的文件夹名称
							
4.  parse_sogou.py
将sogou文件夹下所有的网页重新解析入Mongo库。表为data.sogounew
nohup python parse_sogou.py 20160303 > ./logs/sogou1.log  2>&1 &
nohup python parse_sogou.py 20160304 > ./logs/sogou1.log  2>&1 &
                            这个是输入要处理的sogou文件夹下的文件夹名称
							
5.  sogou_insert.py
向mysql抓取表添加新的未抓取的网址.
修改for qid in range(4075000,5075000):中的4075000和5075000就可以将他们之间的网址都入库。

6.  baidu_insert.py
向mysql抓取表添加新的未抓取的网址.
修改for qid in range(100,101100):中的100和101100就可以将他们之间的网址都入库。
由于baidu有发散抓取机制，所以这个可以不用。


抓取网址Mysql数据库的设计.
数据库位于10.11.35.201:3306,账号root,密码12345678.
1.  baidu
百度网址数据库为spider.baidu,字段如下:
use spider;
create table baidu(id bigint unsigned not null auto_increment,umd5 varchar(50) not null,url varchar(500) not null,spider bool, primary key(id)) default charset=utf8 ;
alter table baidu add unique(umd5);
alter table baidu add index index_name(spider);
2.  sogou
和百度类似：
use spider;
create table sogou(id int unsigned not null auto_increment,umd5 varchar(50) not null,url varchar(500) not null,spider bool, primary key(id)) default charset=utf8 ;
alter table sogou add unique(umd5);
alter table sogou add index index_name(spider);


解析数据Mongo数据库设计
数据库位于10.11.35.201:27017
baidu本地网页解析数据存在data.baidunew,在线爬虫存在data.baidu
sogou本地网页解析数据存在data.sougonew,在线爬虫存在data.sogou


解析网页的字段类似，...表示不同网站提取的不同部分：
{"_id":ObjectId,
"url":string,
"question_title":string,
"quetion_content":string,
"answers":[{"text":string,"quality":{"num_support":int,"num_oppose":int,"user_info":{"gradeIndex":int,"grAnswerNum":int,"goodRate":int,...},...}},{}....],
"similar_quetions":[string,string...],
"class_tag":string,
"insert_time":string,
"question_quality":{"ask_time":string,...}}




