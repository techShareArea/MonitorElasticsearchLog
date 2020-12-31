#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   setup.py
@Time    :   2020/12/24 10:15:15
@Author  :   bigfirmament
@Contact :   bigfirmament@163.com
@Desc    :   setup file
''' 

# here put the import lib
from job import run

if __name__ == "__main__":
    excute = run.ExcuteJob()
    excute.excute_job()