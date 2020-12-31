#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   run.py
@Time    :   2020/12/23 18:29:56
@Author  :   bigfirmament
@Contact :   bigfirmament@163.com 
@Desc    :   about monitor file
'''

# here put the import lib
import json
import subprocess
import time
import requests
from docs import config
from . import run
from . import MonitorElasticsearchLogDB


class Monitor():
    def __init__(self, head, env, app):
        self.current_time = time.strftime("%Y%m%d")
        self.send_dingding_alert_url = config.send_dingding_alert_url
        self.level = config.level
        self.head = head
        self.env = env
        self.app = app
        self.elastic_user = config.elastic_user
        self.elastic_password = config.elastic_password
        self.elastic_ecs_ip = config.elastic_ecs_ip
        self.elastic_ecs_port = config.elastic_ecs_port
        self.database_filename = config.database_filename
        self.database_table = config.database_table.format(head, env, app)
        self.create_database_table = config.create_database_table

    def excute_command(self, command):
        """
        执行函数中的命令，并返回其输出值
        """
        subp = subprocess.Popen(command,
                                shell=True,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        if subp.poll() != 0:
            return subp.stdout.read()
        else:
            return "failure"

    def create_db_table(self):
        """
        创建数据库
        """
        crate_sql_table = self.create_database_table.format(
            self.database_table)
        crate_db_table = MonitorElasticsearchLogDB.CreateDb(
            database_filename=self.database_filename,
            create_database_table=crate_sql_table)
        crate_db_table.create_table()
        crate_db_table.close_database()

    def insert_table_data(self, insert_table_data):
        """
        插入表数据
        """
        insert_table = MonitorElasticsearchLogDB.CreateDb(
            database_filename=self.database_filename,
            insert_table_data=insert_table_data)
        insert_table.insert_table_datas()
        insert_table.close_database()

    def select_table_data(self, field="*"):
        """
        查询表数据
        """
        select_sql_table_data = "select {0} from {1}".format(
            field, self.database_table)
        select_table = MonitorElasticsearchLogDB.CreateDb(
            database_filename=self.database_filename,
            select_table_data=select_sql_table_data)
        select_table_data = select_table.select_table_datas()
        select_table.close_database()
        return select_table_data

    def get_es_info(self):
        """
        获取索引名(形如applog-dev-cjfc-20201223)的es存储日志信息
        """
        try:
            get_index_command = "curl --user {0}:{1} -XGET \
                http://{2}:{3}/{4}-{5}-{6}-{7}/_doc/_search".format(
                self.elastic_user, self.elastic_password, self.elastic_ecs_ip,
                self.elastic_ecs_port, self.head, self.env, self.app,
                self.current_time)
            get_index_info = json.loads(
                str(Monitor(self.head, self.env,
                            self.app).excute_command(get_index_command),
                    encoding="utf-8"))
            return get_index_info["hits"]["hits"]
        except:
            return "未有索引"

    def get_log_time(self, transform_time_format):
        """
        将es内的@timestamp转换为以s(秒)为单位的数值
        """
        transform_time = transform_time_format.replace("T", " ")[:-5]
        return int(
            time.mktime(time.strptime(transform_time, "%Y-%m-%d %H:%M:%S")))

    def importance_thing_warn(self):
        """
        当0、6、12、18点时，相同的错误日志信息达到3次时，再次进行告警，并提醒处理
        """
        try:
            monitor_time = time.strftime("%H:%M:%S")
            if (monitor_time
                    == "00:00:00") or (monitor_time == "06:00:00") or (
                        monitor_time == "12:00:00") or (monitor_time
                                                        == "18:00:00"):
                select_talbe_timestamp_message_info = list(
                    Monitor(self.head, self.env,
                            self.app).select_table_data()[-3::])
                if (list(select_talbe_timestamp_message_info[0])[-1] == list(
                        select_talbe_timestamp_message_info[1])[-1]) and (
                            list(select_talbe_timestamp_message_info[0])[-1]
                            == list(
                                select_talbe_timestamp_message_info[-1])[-1]):
                    send_dingding_data = "你的应用 ==>> {0}-{1}，\
                                            其错误(ERROR)日志信息 ==>> {2}，\
                                            已出现、联系出现3次，为了保障应用正常运转，\
                                            烦请及时进行处理".format(
                        self.database_table, self.current_time,
                        list(select_talbe_timestamp_message_info[-1])[-1])
                    Monitor(self.head, self.env, self.app).send_dingding_alert(
                        logger_name=None,
                        timestamp=None,
                        message=None,
                        send_dingding_data=send_dingding_data)
        except:
            pass

    def send_dingding_alert(self,
                            logger_name=None,
                            timestamp=None,
                            message=None,
                            send_dingding_data=None):
        headers = {'Content-Type': 'application/json'}
        if send_dingding_data == "None":
            send_dingding_data = "您的应用日志出现错误,请及时处理:\n " + "app ==> " + self.head + '-' + self.app + "\nenv ==> " + self.env + "\nlevel ==> " + self.level + "\nlogger_name ==> " + logger_name + "\n@timestamp ==> " + timestamp + "\nmessage ==> " + message + "\n"
        else:
            send_dingding_data = send_dingding_data
        data = {"msgtype": "text", "text": {"content": send_dingding_data}}
        requests.post(self.send_dingding_alert_url,
                      data=json.dumps(data),
                      headers=headers)

    def alert_info_save_database(self):
        """
        提取含有error级别的日志信息，30分钟内相同的错误日志信息，不存入数据库，不进行告警；
        否则，存入数据库，并告警
        """
        try:
            Monitor(self.head, self.env, self.app).create_db_table()
        except:
            pass
        get_index_info = Monitor(self.head, self.env, self.app).get_es_info()
        Monitor(self.head, self.env, self.app).importance_thing_warn()
        if get_index_info != "未有索引":
            for i in range(len(get_index_info)):
                es_log_level = get_index_info[i]["_source"]["level"]
                if (es_log_level == "ERROR") or (es_log_level == "error"):
                    if self.head == "extern":
                        es_log_logger_name = ""
                    else:
                        es_log_logger_name = get_index_info[i]["_source"][
                            "logger_name"]
                    es_log_timestamp = get_index_info[i]["_source"][
                        "@timestamp"]
                    es_log_message = get_index_info[i]["_source"][
                        "message"].replace("'", "")
                    get_db_info = Monitor(self.head, self.env,
                                          self.app).select_table_data()
                    insert_table_data = "insert into {0} values({1}, '{2}', '{3}\
                        ', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}')".format(
                        self.database_table,
                        len(get_db_info) + 1, self.head, self.env, self.app,
                        self.current_time, self.level, es_log_logger_name,
                        es_log_timestamp, es_log_message)
                    if get_db_info == []:
                        Monitor(self.head, self.env,
                                self.app).insert_table_data(insert_table_data)
                        Monitor(self.head, self.env,
                                self.app).send_dingding_alert(
                                    logger_name=es_log_logger_name,
                                    timestamp=es_log_timestamp,
                                    message=es_log_message,
                                    send_dingding_data="None")
                    else:
                        select_talbe_timestamp_message_info = list(
                            Monitor(self.head, self.env,
                                    self.app).select_table_data(
                                        field="es_timestamp,message")[-1])
                        db_message = select_talbe_timestamp_message_info[-1]
                        db_timestamp = select_talbe_timestamp_message_info[0]
                        if (db_message != es_log_message) and (
                                Monitor(self.head, self.env, self.app).
                                get_log_time(es_log_timestamp) - Monitor(
                                    self.head, self.env,
                                    self.app).get_log_time(db_timestamp) > 0):
                            Monitor(
                                self.head, self.env,
                                self.app).insert_table_data(insert_table_data)
                            Monitor(self.head, self.env,
                                    self.app).send_dingding_alert(
                                        logger_name=es_log_logger_name,
                                        timestamp=es_log_timestamp,
                                        message=es_log_message,
                                        send_dingding_data="None")
                        elif (db_message == es_log_message) and (
                                Monitor(self.head, self.env, self.app
                                        ).get_log_time(es_log_timestamp) -
                                Monitor(self.head, self.env,
                                        self.app).get_log_time(db_timestamp) >
                                1800):
                            Monitor(
                                self.head, self.env,
                                self.app).insert_table_data(insert_table_data)
                            Monitor(self.head, self.env,
                                    self.app).send_dingding_alert(
                                        logger_name=es_log_logger_name,
                                        timestamp=es_log_timestamp,
                                        message=es_log_message,
                                        send_dingding_data="None")
