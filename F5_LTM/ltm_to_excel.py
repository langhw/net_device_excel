#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:15
# @Author  : lianghongwei
# @File    : ltm_to_excel.py
# @Description :
'''脚本功能作用：
    1、将F5_LTM的list信息表格化
    2、能够收集的信息包括ltm monitor,ltm pool,ltm snatpool,ltm virtual等模块
脚本使用说明：
    LTM日志收集方法：
        1、进入tmos模式下：
        tmsh
        2、进入根目录()：
        cd /
        3、收集ltm所有partition信息成行展示：
        list ltm recursive all-properties one-line
    需要用的python库：
        re,chardet,pandas,numpy,styleframe,os,file,
'''

import re
import chardet
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler
import numpy as np


# ## 定义全局变量：

wkey = ('list ltm recursive all-properties one-line', 'ltm monitor ', 'ltm pool ', 'ltm snatpool ', 'ltm virtual ')
ltm_monitor = {}
ltm_pool = {}
ltm_snatpool = {}
ltm_virtual = {}
ltm_all = {}
column = ['VS类型', '申请人', 'F5区域名称', 'VS名称', '应用类型*', '域名', 'VS服务地址', 'VS服务端口*', 'POOL名称', \
		  'member地址(需负载的服务器)', 'Pool_member地址状态', 'member端口', '负载均衡算法*', '会话保持类型*', '会话保持时间*', \
		  '长连接与长连接时间*', '长连接时间', '是否需要透传源地址*', 'SNAT名称', 'SNAT地址分配', '并发数评估', '健康检查名称', \
		  '探测类型*', '检查条件*', '成功返回值*', '探测包发送间隔*', '探测包重传次数*', '最大响应时间*', '其他特殊需求', 'vs启用', \
		  'vs状态', 'vs创建时间', 'vs最后修改时间', '证书', 'Vs_index']
# ## 输入LTM日志文件名称和表格保存的名称：
log_file = input('Please enter the name of the F5_LTM device log file(Default is conf):') or r'C:\Users\lianghw\Documents\pythonxx\kfcs_all'
out_file = input('Please enter the name of the output table(Default is F5_LTM):') or r'C:\Users\lianghw\Documents\F5_LTM'
if '.log' not in log_file:
	log_file = '{}.log'.format(log_file)
if '.xlsx' not in log_file:
	out_file = '{}.xlsx'.format(out_file)

# ## 查找日志编码，并打开文件至list信息位置

encod = linshi = ''
with open(log_file, 'rb') as f:
	encod = chardet.detect(f.read(200000))['encoding']
file = open(log_file, 'r', encoding=encod)
while wkey[0] not in linshi:
	linshi = file.readline()
else:
	linshi = file.tell()
file.seek(linshi - 100)

#定义ltm_monitor匹配参数
pat_ltm_monitor_name = re.compile(r'ltm monitor (\w+) \w+/(.*?) {') #匹配ltm monitor 的名称和类型
pat_ltm_monitor_interval = re.compile(r' interval (\d+) ') #匹配ltm monitor 的间隔时间
pat_ltm_monitor_partition = re.compile(r' partition (\w+) ') #匹配ltm monitor 的partition
pat_ltm_monitor_recv = re.compile(r' recv (\w*) ') #匹配ltm monitor 的recv
pat_ltm_monitor_send = re.compile(r' send "GET (.*? ) " ') #匹配ltm monitor 的send
pat_ltm_monitor_timeout = re.compile(r' timeout (\d*) ') #匹配ltm monitor timeout
#定义ltm_pool匹配参数
pat_ltm_pool_name = re.compile(r'ltm pool \w+/(.*?) {') #匹配ltm pool 名称
pat_ltm_pool_loadbalancingmode = re.compile(r' load-balancing-mode (.*?) ') #匹配ltm pool 负载模式
pat_ltm_pool_ip = re.compile(r' \w+/(\d+\.\d+\.\d+\.\d+):(.*?) { address ') #匹配ltm pool ip 和 端口 多个
pat_ltm_pool_ip_state = re.compile(r' state (.*?) fqdn ') #匹配ltm pool state
pat_ltm_pool_monitor = re.compile(r'monitor \w*/(.*?) ') #匹配ltm pool monitor
pat_ltm_pool_partition = re.compile(r' partition (\w*) ') #匹配ltm pool partition
#定义ltm_snatpool匹配参数
pat_ltm_snatpool_name = re.compile(r'ltm snatpool \w+/(.*?) {') #匹配ltm snatpool 名称
pat_ltm_snatpool_ip = re.compile(r'members { \w+/(\d+\.\d+\.\d+\.\d+) }') #匹配ltm snatpool ip
pat_ltm_snatpool_partition = re.compile(r' partition (\w+) ') #匹配ltm snatpool partition
#定义ltm_virtual匹配参数
pat_ltm_virtual_name = re.compile(r'ltm virtual \w+/(.*?) {') #匹配ltm virtual 名称
pat_ltm_virtual_addressstatus = re.compile(r' address-status (\w+) ') #匹配ltm virtual address-status
pat_ltm_virtual_ip = re.compile(r' destination \w+/(\d+\.\d+\.\d+\.\d+)%\d+:(.*?) (\w+) ') #匹配ltm virtual 地址，端口和启用状态。
pat_ltm_virtual_partition = re.compile(r' partition (\w+) ') #匹配ltm virtual partition
pat_ltm_virtual_cookie = re.compile(r' persist { \w+/GDCS_cookie_(\w+) ') #匹配ltm virtual cookie时间
pat_ltm_virtual_pool = re.compile(r' pool \w+/(.*?) ') #匹配ltm virtual pool
pat_ltm_virtual_sat = re.compile(r'source-address-translation { pool \w+/(.*?) ') #匹配ltm virtual source-address-translation
pat_ltm_virtual_profiles = re.compile(r' profiles { Common/(.*?) { context clientside } Common/(.*?) { context serverside } Common/(.*?) { context all } ') #匹配ltm virtual profiles
pat_ltm_virtual_index = re.compile(r' vs-index (\d+) ') #匹配ltm virtual index

# ## 逐行分析关键词，并导入字典：
for line in file.readlines():
	#健康检查信息收集：
	if wkey[1] in line:
		#ltm monitor 的名称和类型
		ltm_monitor_name = pat_ltm_monitor_name.findall(line)
		ltm_monitor[ltm_monitor_name[0][1]] = [ltm_monitor_name[0][0]]
		#ltm monitor 的间隔时间
		ltm_monitor_interval = pat_ltm_monitor_interval.findall(line)
		ltm_monitor[ltm_monitor_name[0][1]].append(ltm_monitor_interval[0])
		#ltm monitor 的partition
		ltm_monitor_partition = pat_ltm_monitor_partition.findall(line)
		# print(ltm_monitor_partition)
		ltm_monitor[ltm_monitor_name[0][1]].append(ltm_monitor_partition[0])
		#ltm monitor 的recv
		ltm_monitor_recv = pat_ltm_monitor_recv.findall(line)
		ltm_monitor[ltm_monitor_name[0][1]].append(ltm_monitor_recv[0])
		#ltm monitor 的send
		ltm_monitor_send = pat_ltm_monitor_send.findall(line)
		if len(ltm_monitor_send) == 0:
			ltm_monitor[ltm_monitor_name[0][1]].append('none')
		else:
			ltm_monitor[ltm_monitor_name[0][1]].append(ltm_monitor_send[0])
		#ltm monitor timeout
		ltm_monitor_timeout = pat_ltm_monitor_timeout.findall(line)
		ltm_monitor[ltm_monitor_name[0][1]].append(ltm_monitor_timeout[0])
	# pool信息收集：
	elif wkey[2] in line:
		# ltm pool 名称
		ltm_pool_name = pat_ltm_pool_name.findall(line)
		ltm_pool[ltm_pool_name[0]] = []
		# ltm pool 负载模式
		ltm_pool_loadbalancingmode = pat_ltm_pool_loadbalancingmode.findall(line)
		ltm_pool[ltm_pool_name[0]].append(ltm_pool_loadbalancingmode[0])
		# ltm pool ip 和 端口 ip状态  多个
		ltm_pool_ip = pat_ltm_pool_ip.findall(line)
		ltm_pool_ip_state = pat_ltm_pool_ip_state.findall(line)
		if len(ltm_pool_ip) == 0:
			ltm_pool[ltm_pool_name[0]].append('none')
			ltm_pool[ltm_pool_name[0]].append('none')
			ltm_pool[ltm_pool_name[0]].append('none')
		elif len(ltm_pool_ip) == 1:
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip[0][0])
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip[0][1])
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip_state[0])
		else:
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip[0][0])
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip[0][1])
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_ip_state[0])
			for n in range(1, len(ltm_pool_ip)):
				ltm_pool[ltm_pool_name[0]][1] = ltm_pool[ltm_pool_name[0]][1] + chr(10) + ltm_pool_ip[n][0]
				# ltm_pool[ltm_pool_name[0]][2] = ltm_pool[ltm_pool_name[0]][2] + chr(10) + ltm_pool_ip[n][1]
				ltm_pool[ltm_pool_name[0]][3] = ltm_pool[ltm_pool_name[0]][3] + chr(10) + ltm_pool_ip_state[n]
		# ltm pool monitor
		ltm_pool_monitor = pat_ltm_pool_monitor.findall(line)
		if len(ltm_pool_monitor) == 0:
			ltm_pool[ltm_pool_name[0]].append('none')
		else:
			ltm_pool[ltm_pool_name[0]].append(ltm_pool_monitor[0])
		# ltm pool partition
		ltm_pool_partition = pat_ltm_pool_partition.findall(line)
		ltm_pool[ltm_pool_name[0]].append(ltm_pool_partition[0])
		# print(ltm_pool[ltm_pool_name[0]])
	# ltm_snatpool 信息收集：
	elif wkey[3] in line:
		# ltm snatpool 名称
		ltm_snatpool_name = pat_ltm_snatpool_name.findall(line)
		ltm_snatpool[ltm_snatpool_name[0]] = []
		# ltm snatpool ip
		ltm_snatpool_ip = pat_ltm_snatpool_ip.findall(line)
		ltm_snatpool[ltm_snatpool_name[0]].append(ltm_snatpool_ip[0])
		# ltm snatpool partition
		ltm_snatpool_partition =pat_ltm_snatpool_partition.findall(line)
		ltm_snatpool[ltm_snatpool_name[0]].append(ltm_snatpool_partition[0])
		# print(ltm_snatpool[ltm_snatpool_name[0]])
	# ltm_virtual 信息收集：
	elif wkey[4] in line:
		# ltm virtual 名称
		ltm_virtual_name = pat_ltm_virtual_name.findall(line)
		ltm_virtual[ltm_virtual_name[0]] = []
		# ltm virtual address-status
		ltm_virtual_addressstatus = pat_ltm_virtual_addressstatus.findall(line)
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_addressstatus[0])
		# ltm virtual 地址，端口和启用状态。
		ltm_virtual_ip = pat_ltm_virtual_ip.findall(line)
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_ip[0][0])
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_ip[0][1])
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_ip[0][2])
		# 匹配ltm virtual partition
		ltm_virtual_partition = pat_ltm_virtual_partition.findall(line)
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_partition[0])
		# 匹配ltm virtual cookie时间
		ltm_virtual_cookie = pat_ltm_virtual_cookie.findall(line)
		if len(ltm_virtual_cookie) == 0:
			ltm_virtual[ltm_virtual_name[0]].append('none')
		else:
			ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_cookie[0])
		# 匹配ltm virtual pool
		ltm_virtual_pool = pat_ltm_virtual_pool.findall(line)
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_pool[0])
		# 匹配ltm virtual source-address-translation
		ltm_virtual_sat = pat_ltm_virtual_sat.findall(line)
		if len(ltm_virtual_sat) == 0:
			ltm_virtual[ltm_virtual_name[0]].append('none')
		else:
			ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_sat[0])
		# # 匹配ltm virtual profiles
		# ltm_virtual_profiles = pat_ltm_virtual_profiles.findall(line)
		# ltm_virtual[pat_ltm_virtual_name[0]].append(ltm_virtual_profiles[0])
		# 匹配ltm virtual index
		ltm_virtual_index = pat_ltm_virtual_index.findall(line)
		ltm_virtual[ltm_virtual_name[0]].append(ltm_virtual_index[0])
		# print(ltm_virtual[ltm_virtual_name[0]])
