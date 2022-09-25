#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/9/23 21:48
# @Author  : lianghongwei
# @File    : fw_rules.py
# @Software: PyCharm
# @Description :
"""
登录华三防火墙，收集配置信息后将安全策略表格化导出
"""
import os
from datetime import datetime
from multiprocessing.pool import ThreadPool
import logging
import re
import textfsm
import openpyxl
import threading
from netmiko import ConnectHandler as ch
from netmiko.ssh_exception import (NetMikoTimeoutException, AuthenticationException, SSHException)
from prettytable import PrettyTable
# logging.basicConfig(level=logging.DEBUG)

def device_info():
	"""在表格中获取设备登录信息"""
	book = openpyxl.load_workbook('device_info.xlsx')
	sheet = book.active
	for row in sheet.iter_rows(min_row=2, min_col=2, max_col=6):
		if row[0].value is not None:
			continue
		ip = row[2].value
		username = 'admin' if row[3].value is None else row[3].value
		password = 'admin' if row[4].value is None else row[4].value
		info_dict = {'ip': ip,
		             # 'protocol': 'ssh',
		             # 'port': '22',
		             'username': username,
		             'password': password,
		             'device_type': 'hp_comware',
		             }
		yield info_dict
	book.close()


def denglu(dev_info):
	"""ssh登录设备"""
	try:
		conn = ch(**dev_info)
		return conn
	except NetMikoTimeoutException:
		e = "Failed.....{:<15} 连通性问题!".format(dev_info['ip'])
		printPretty(e)
		fail.append(dev_info['ip'])

	except AuthenticationException:
		e = "Failed.....{:<15} 用户名或密码错误!".format(dev_info['ip'])
		printPretty(e)
		fail.append(dev_info['ip'])

	except SSHException:
		e = "Failed.....{:<15} SSH版本不兼容!".format(dev_info['ip'])
		printPretty(e)
		fail.append(dev_info['ip'])

	except Exception as e:
		e = "Failed.....{:<15} connectHandler Error: {}".format(dev_info['ip'], e)
		printPretty(e)
		fail.append(dev_info['ip'])


def get_conf(dev_info):
	"""获取防火墙配置信息"""
	printPretty('设备...{:.<15}...开始执行'.format(dev_info['ip']))

	conn = denglu(dev_info)
	output = ''
	if conn:
		# 获取设备名称并格式化
		# hostname = format_hostname(conn.find_prompt(), dev_info['device_type'])
		hostname = format_hostname(conn.find_prompt())
		try:
			for cmd in cmds:
				output = output + conn.send_command(cmd, strip_prompt=False, strip_command=False,)
			success.append(dev_info['ip'])

		except Exception as e:
			output = f"run Failed...{dev_info['ip']} : {e}"
			printPretty(output)
			fail.append(dev_info['ip'])
		finally:
			# 退出netmiko session
			conn.disconnect()
		return hostname, output

def printPretty(msg):
	"""打印消息"""
	# 在并发的场景中，避免在一行打印出多个结果，不方便查看
	queueLock.acquire()  # 加锁
	print(msg)
	queueLock.release()  # 释放锁


def printSum(self, msg):
	"""打印结果汇总信息"""
	total_devices, success, fail = len(self.success + self.fail), len(self.success), len(self.fail)
	total_time = "{:0.2f}s".format(msg.total_seconds())
	tb = PrettyTable(['设备总数', '成功', '失败', '总耗时'])
	tb.add_row([total_devices, success, fail, total_time])
	print(tb)

def format_hostname(hostname):
	"""格式化主机名称"""
	new_hostname = hostname.split()[0].strip("<>#$() ")
	return new_hostname


def conf_key():
	"""获取配置关键信息"""
	pass


def to_excel():
	"""将关键信息写入表格"""
	pass


def meihua():
	"""美化excel表格"""
	pass


def log_dir():
	"""创建目录"""
	# 判断当前目录是否有LOG文件夹，不存在则创建
	if not os.path.exists('LOG'):
		os.makedirs('LOG')
	return 'LOG'


if __name__ == '__main__':
	# device_file = "巡检模板.xlsx"  # 模板文件
	pool = ThreadPool(5)  # 并发数
	queueLock = threading.Lock()  # 线程锁
	logtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # 时间
	log = log_dir()
	success = []
	fail = []
	cmds = ['disp version']
	for dev in device_info():
		ppp = get_conf(dev)
		print(ppp)
	print('连接失败的{}'.format(fail))

