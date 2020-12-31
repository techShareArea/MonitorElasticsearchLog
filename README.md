#### 前言
此工程项目是为了把java相关项目存储在es的error日志提取出来，并通过钉钉机器人告警相关开发人员，实现及时发现问题，及时处理问题的功能效果

#### es索引格式
- 索引格式为
head-env-app-datetime

|   head   |   env   |           app         | datetime |
|:--------:|:-------:|:---------------------:|:--------:|
|  xxxxxx  |   xxx   |           xxxx        | 20201111 |

#### 存储数据
所使用的数据库为python3自身所带的sqlite3数据库

#### 部署
ELK请自行搭建，这里不再赘述

##### 配置
请自行根据自身情况，把config.py配置文件补充完善

##### 把项目克隆到linux服务器上的相应目录下，并安装项目模块
```
pip3 install -r requirements.txt
```

##### 配置定时任务
```
cat >> /etc/crontab <<-EOF
5/* * * * * root /usr/bin/python3 xxxx(setup.py文件的絕對路徑)
```

##### 钉钉告警
- 请自行配置钉钉告警机器人

告警的相关信息如下
```
您的应用日志出现错误,请及时处理:
app ==> xxx-xxx
env ==> dev
level ==> ERROR
logger_name ==> xxx
@timestamp ==> 2020-11-11T03:19:38.576Z
message ==> xxx
```

#### 结语
欢迎指正，共同进步