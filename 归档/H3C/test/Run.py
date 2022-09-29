#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/9/27 20:59
# @Author  : lianghongwei
# @File    : Run.py
# @Software: PyCharm
# @Description :
from FwGetInfo import FwGetInfo
from FwRules_to_excel import FwRules_To_Excle
import datetime

def run():
	for dev_info in FwGetInfo.get_conf():
		FwRules_To_Excle(dev_info).write_excel()

if __name__ == "__main__":
	start_time = datetime.now()
	run()
	end_time = datetime.now()
	FwGetInfo.printSum(end_time - start_time)
