#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''
@File    :   run.py
@Time    :   2020/12/23 18:29:56
@Author  :   bigfirmament
@Contact :   bigfirmament@163.com
@Desc    :   run file
'''

# here put the import lib
from docs import config
from . import monitor


class ExcuteJob():

    def __init__(self):
        self.head = config.head
        self.env = config.env
        self.app = config.app

    def excute_job(self):
        for head in range(len(self.head)):
            for env in range(len(self.env)):
                for app in range(len(self.app)):
                    monitor.Monitor(self.head[head], self.env[env], self.app[app]).alert_info_save_database()