#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   MonitorElasticsearchLogDB.py
@Time    :   2020/12/24 14:52:45
@Author  :   bigfirmament
@Contact :   bigfirmament@163.com
@Desc    :   sql file
'''

# here put the import lib
import sqlite3


class CreateDb():
    def __init__(self,
                 database_filename=None,
                 database_table=None,
                 create_database_table=None,
                 insert_table_data=None,
                 update_table_data=None,
                 select_table_data=None):
        self.database_filename = database_filename
        self.database_table = database_table
        self.create_database_table = create_database_table
        self.insert_table_data = insert_table_data
        self.update_table_data = update_table_data
        self.select_table_data = select_table_data
        self.conn = sqlite3.connect(database_filename)
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute(self.create_database_table)
        self.conn.commit()

    def insert_table_datas(self):
        self.cur.execute(self.insert_table_data)
        self.conn.commit()

    def update_table_datas(self):
        self.cur.execute(self.update_table_data)
        self.conn.commit()

    def select_table_datas(self):
        self.cur.execute(self.select_table_data)
        self.conn.commit()
        get_table_data = self.cur.fetchall()
        return get_table_data

    def close_database(self):
        self.cur.close()
        self.conn.close()
