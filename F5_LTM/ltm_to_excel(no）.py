#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:32
# @Author  : lianghongwei
# @File    : ltm_to_excel(no）.py
# @Description :
'''
	本脚本能够通过 "" 日志实现F5_LTM的表格化。
		梁洪伟
		2022-5-17
'''
import re
import chardet
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler
#
# 定义全局变量
# key = {1:'ltm monitor',2,'ltm pool',3:'ltm profile client-ssl',4:'ltm profile http',5:'ltm profile one-connect',6:'ltm profile server-ssl',7:'ltm profile tcp',8:'ltm snatpool',9:'ltm virtual'}
# addr = re.compile(r'\d+\.\d+\.\d+\.\d+')
# key = ('list all-properties','ltm monitor','ltm pool','ltm profile client-ssl','ltm profile http','ltm profile server-ssl','ltm profile tcp','ltm snatpool','ltm virtual')

# key3 = ('    cert','    chain','    key','    mode',)
# key4 = ('    insert-xforwarded-for',)
# key5 = ('    cert','    chain','    key','    mode',)# key3 = ('    cert','    chain','    key','    mode',)
# # key4 = ('    insert-xforwarded-for',)
# # key5 = ('    cert','    chain','    key','    mode',)
# ltm['ltm_profile_client_ssl'] = {}
# ltm['ltm_profile_http'] = {}
# ltm['ltm_profile_server_ssl'] = {}
key = ('list ltm all-properties', 'ltm monitor', 'ltm pool', 'ltm snatpool', 'ltm virtual')
key_s = []
key_ss = []
# key1 = ('    recv ', '    send', '    interval', '    timeout',)
key1 = ('    recv ', re.compile(r'\s{4}send\s{1}'), re.compile(r'\s{4}interval\s{1}'), re.compile(r'\s{4}timeout\s\d{2}\s'),)
key2 = ('    load-balancing-mode', '        1', '    state', '    monitor', '    partition',)
key3 = (r'        1', '    partition',)
key4 = ('    address-status', '    creation-time', '    destination', '    enabled', '    ip-protocol',
        '    last-modified-time', '    partition', '        Cookie', re.compile(r'\s{4}pool\s'), '        http-XFF', '.com',
        '        pool ', '    vs-index ',)
ltm = {}
ltm['ltm_monitor'] = {}
ltm['ltm_pool'] = {}
ltm['ltm_snatpool'] = {}
ltm['ltm_virtual'] = {}
# '''ltm_xq = {'VS类型': 'none', '申请人': 'none', 'F5区域名称': 'none', 'VS名称': 'none', '应用类型*': 'none', '域名': 'none',
#           'VS服务地址': 'none', 'VS服务端口*': 'none', 'POOL名称': 'none', 'member地址(需负载的服务器)': 'none', 'member端口': 'none',
#           '负载均衡算法*': 'none', '会话保持类型*': 'none', '会话保持时间*': 'none', '长连接与长连接时间*': 'none', '长连接时间': 'none',
#           '是否需要透传源地址*': 'none', 'SNAT名称': 'none', 'SNAT地址分配': 'none', '并发数评估': 'none', '健康检查名称': 'none',
#           '探测类型*': 'none', '检查条件*': 'none', '': 'none', '成功返回值*': 'none', '探测包发送间隔*': 'none', '探测包重传次数*': 'none',
#           '最大响应时间*': 'none', '其他特殊需求': 'none'}'''
#
# ltm_xq = {'VS类型': [], '申请人': [], 'F5区域名称': [], 'VS名称': [], '应用类型*': [], '域名': [],
#           'VS服务地址': [], 'VS服务端口*': [], 'POOL名称': [], 'member地址(需负载的服务器)': [], 'Pool_member地址状态': [], 'member端口': [],
#           '负载均衡算法*': [], '会话保持类型*': [], '会话保持时间*': [], '长连接与长连接时间*': [], '长连接时间': [],
#           '是否需要透传源地址*': [], 'SNAT名称': [], 'SNAT地址分配': [], '并发数评估': [], '健康检查名称': [],
#           '探测类型*': [], '检查条件*': [], '成功返回值*': [], '探测包发送间隔*': [], '探测包重传次数*': [],
#           '最大响应时间*': [], '其他特殊需求': [], 'vs启用': [], 'vs状态': [], 'vs创建时间': [], 'vs最后修改时间': [], '证书': [], 'Vs_index': []}
#
column = ['VS类型', '申请人', 'F5区域名称', 'VS名称', '应用类型*', '域名', 'VS服务地址', 'VS服务端口*', 'POOL名称', \
		  'member地址(需负载的服务器)', 'Pool_member地址状态', 'member端口', '负载均衡算法*', '会话保持类型*', '会话保持时间*', \
		  '长连接与长连接时间*', '长连接时间', '是否需要透传源地址*', 'SNAT名称', 'SNAT地址分配', '并发数评估', '健康检查名称', \
		  '探测类型*', '检查条件*', '成功返回值*', '探测包发送间隔*', '探测包重传次数*', '最大响应时间*', '其他特殊需求', 'vs启用', \
		  'vs状态', 'vs创建时间', 'vs最后修改时间', '证书', 'Vs_index']
ltm_xq = {}
for i in column:
	ltm_xq[i] = []
# 输入日志和保存文件信息
log_file = input('Please enter the name of the F5_LTM device log file(Default is conf):') or 'conf'
out_file = input('Please enter the name of the output table(Default is F5_LTM):') or 'F5_LTM'
if '.log' not in log_file:
	log_file = '{}.log'.format(log_file)
if '.xlsx' not in log_file:
	out_file = '{}.xlsx'.format(out_file)
# 查看日志编码，并打开文件至首行
encod = ''
with open(log_file, 'rb') as f:
	encod = chardet.detect(f.read(200000))['encoding']
file = open(log_file, 'r', encoding=encod)
file.seek(0)
# 定位每个节点的字节位置
y = 'string'
for x in key:
	while x not in y:
		y = file.readline()
	else:
		key_s.append(file.tell())
file.readlines()
key_s.append(file.tell())
# print(key_s)
# 计算每个节点的字节数量
# print(len(key_s))
# for i in range(len(key_s) - 1, 0, -1):
# 	x = key_s[i] - key_s[i - 1]
# 	key_ss.append(x)
# print(key_ss)
#
#
# 对数据进行格式化写入字典中。
#
#
file.seek(key_s[1] - 100)
#
for line in file.readlines():
	# 健康检查
	if key[1] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		ltm_monitor = line[-1]
		ltm_monitor_type = line[-2]
		ltm['ltm_monitor'][ltm_monitor] = [ltm_monitor_type]
	elif key1[0] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		ltm_monitor_recv = line[-1]
		ltm['ltm_monitor'][ltm_monitor].append(ltm_monitor_recv)
	elif key1[1].match(line):
		line = line.rstrip(' {\n')
		line = line.split(' ')
		try:
			ltm_monitor_send = line[6]
		except IndexError:
			ltm_monitor_send = line[5]
		ltm['ltm_monitor'][ltm_monitor].append(ltm_monitor_send)
	elif key1[2].match(line):
		line = line.rstrip(' {\n')
		line = line.split(' ')
		interval = line[-1]
		ltm['ltm_monitor'][ltm_monitor].append(interval)
	elif key1[3].match(line):
		line = line.rstrip(' {\n')
		line = line.split(' ')
		timeout = line[-1]
		ltm['ltm_monitor'][ltm_monitor].append(timeout)
	# 地址池pool
	elif key[2] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		ltm_pool = line[-1]
		ltm['ltm_pool'][ltm_pool] = {}
		ltm['ltm_pool'][ltm_pool]['members_address'] = 'none'
		ltm['ltm_pool'][ltm_pool]['address_state'] = 'none'
		ltm['ltm_pool'][ltm_pool]['members_port'] = 'none'
		ltm['ltm_pool'][ltm_pool]['load_balancing_mode'] = 'none'
		ltm['ltm_pool'][ltm_pool]['pool_monitor'] = 'none'
		ltm['ltm_pool'][ltm_pool]['partition'] = 'none'
	elif key2[0] in line:
		line = line.rstrip(' \n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_pool'][ltm_pool]['load_balancing_mode'] = a
	elif key2[1] in line:
		if ':' in line and 'i' not in line and 'o' not in line:
			line = line.rstrip(' {\n')
			line = line.lstrip(' ')
			line = line.split(':')
			a = line[0]
			p = line[1]
			if ltm['ltm_pool'][ltm_pool]['members_address'] == 'none':
				ltm['ltm_pool'][ltm_pool]['members_address'] = a
			else:
				ltm['ltm_pool'][ltm_pool]['members_address'] = ltm['ltm_pool'][ltm_pool]['members_address'] + chr(
					10) + a
			ltm['ltm_pool'][ltm_pool]['members_port'] = p
	elif key2[2] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		try:
			if ltm['ltm_pool'][ltm_pool]['address_state'] == 'none':
				ltm['ltm_pool'][ltm_pool]['address_state'] = a
			else:
				ltm['ltm_pool'][ltm_pool]['address_state'] = ltm['ltm_pool'][ltm_pool]['address_state'] + chr(10) + a
		except NameError:
			pass
	elif key2[3] in line:
		line = line.rstrip('\n')
		line = line.split('monitor ')
		a = line[-1]
		try:
			ltm['ltm_pool'][ltm_pool]['pool_monitor'] = a
		except NameError:
			pass
	elif key2[4] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		try:
			ltm['ltm_pool'][ltm_pool]['partition'] = a
		except NameError:
			pass
	# SNAT池
	elif key[3] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		snat_pool = line[-1]
		ltm['ltm_snatpool'][snat_pool] = 'none'
	elif key3[0] in line:
		# print(line)
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		if ltm['ltm_snatpool'][snat_pool] == 'none':
			ltm['ltm_snatpool'][snat_pool] = a
		else:
			ltm['ltm_snatpool'][snat_pool] = ltm['ltm_snatpool'][snat_pool] + chr(10) + a
	# vs
	elif key[4] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		vs = line[-1]
		ltm['ltm_virtual'][vs] = {}
		ltm['ltm_virtual'][vs]['address_status'] = 'none'
		ltm['ltm_virtual'][vs]['creation_time'] = 'none'
		ltm['ltm_virtual'][vs]['vs_addr'] = 'none'
		ltm['ltm_virtual'][vs]['vs_port'] = 'none'
		ltm['ltm_virtual'][vs]['vs_status'] = 'disabled'
		ltm['ltm_virtual'][vs]['ip_protocol'] = 'none'
		ltm['ltm_virtual'][vs]['last_modified_time'] = 'none'
		ltm['ltm_virtual'][vs]['partition'] = 'none'
		ltm['ltm_virtual'][vs]['Cookie'] = 'none'
		ltm['ltm_virtual'][vs]['vs_pool'] = 'none'
		ltm['ltm_virtual'][vs]['http_XFF'] = 'none'
		ltm['ltm_virtual'][vs]['ssl_ca'] = 'none'
		ltm['ltm_virtual'][vs]['source_address_translation'] = 'none'
		ltm['ltm_virtual'][vs]['vs_index'] = 'none'
	elif key4[0] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['address_status'] = a
	elif key4[1] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['creation_time'] = a
	elif key4[2] in line:
		line = line.rstrip('\n')
		line = re.split(' |:',line)
		a = line[-2]
		b = line[-1]
		try:
			ltm['ltm_virtual'][vs]['vs_addr'] = a
			ltm['ltm_virtual'][vs]['vs_port'] = b
		except NameError:
			pass
	elif key4[3] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		try:
			ltm['ltm_virtual'][vs]['vs_status'] = a
		except NameError:
			pass
	elif key4[4] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['ip_protocol'] = a
	elif key4[5] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['last_modified_time'] = a
	# elif key4[6] in line:
	# 	print(line)
	# 	line = line.rstrip('\n')
	# 	line = line.split(' ')
	# 	a = line[-1]
	# 	try:
	# 		ltm['ltm_virtual'][vs]['partition'] = a
	# 	except NameError:
	# 		continue
	elif key4[7] in line:
		line = line.rstrip(' {\n')
		line = line.split('_')
		a = line[-1]
		ltm['ltm_virtual'][vs]['Cookie'] = a
	elif key4[8].match(line):
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		try:
			ltm['ltm_virtual'][vs]['vs_pool'] = a
		except NameError:
			pass
	elif key4[9] in line:
		line = line.rstrip(' {\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['http_XFF'] = a
	elif key4[10] in line or 'side' in line:
		line = line.rstrip('\n')
		line = line.rstrip(' {')
		line = line.split(' ')
		a = line[-1]
		try:
			if ltm['ltm_virtual'][vs]['ssl_ca'] == 'none':
				ltm['ltm_virtual'][vs]['ssl_ca'] = a
			else:
				ltm['ltm_virtual'][vs]['ssl_ca'] = ltm['ltm_virtual'][vs]['ssl_ca'] + chr(10) + a
		except NameError:
			pass
	elif key4[11] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		try:
			ltm['ltm_virtual'][vs]['source_address_translation'] = a
		except NameError:
			pass
	elif key4[12] in line:
		line = line.rstrip('\n')
		line = line.split(' ')
		a = line[-1]
		ltm['ltm_virtual'][vs]['vs_index'] = a
#
file.close()
#
# print(ltm)
# print(ltm['ltm_monitor'])
# print(ltm['ltm_pool'])
# print(ltm['ltm_snatpool'])
# print(ltm['ltm_virtual'])
#
# print(len(ltm))
# print(len(ltm['ltm_monitor']))
# print(len(ltm['ltm_pool']))
# print(len(ltm['ltm_snatpool']))
# print(len(ltm['ltm_virtual']))

# 整理表格
for c in ltm['ltm_virtual'].keys():
	ltm_xq['VS名称'].append(c)
	ltm_xq['F5区域名称'].append(ltm['ltm_virtual'][c]['partition'])
	ltm_xq['VS服务地址'].append(ltm['ltm_virtual'][c]['vs_addr'])
	ltm_xq['VS服务端口*'].append(ltm['ltm_virtual'][c]['vs_port'])
	ltm_xq['POOL名称'].append(ltm['ltm_virtual'][c]['vs_pool'])
	ltm_xq['vs启用'].append(ltm['ltm_virtual'][c]['vs_status'])
	ltm_xq['vs状态'].append(ltm['ltm_virtual'][c]['address_status'])
	ltm_xq['vs创建时间'].append(ltm['ltm_virtual'][c]['creation_time'])
	ltm_xq['vs最后修改时间'].append(ltm['ltm_virtual'][c]['last_modified_time'])
	ltm_xq['证书'].append(ltm['ltm_virtual'][c]['ssl_ca'])
	ltm_xq['SNAT名称'].append(ltm['ltm_virtual'][c]['source_address_translation'])
	ltm_xq['会话保持时间*'].append(ltm['ltm_virtual'][c]['Cookie'])
	ltm_xq['是否需要透传源地址*'].append(ltm['ltm_virtual'][c]['http_XFF'])
	ltm_xq['Vs_index'].append(ltm['ltm_virtual'][c]['vs_index'])
	if ltm['ltm_virtual'][c]['vs_pool'] in ltm['ltm_pool']:
		ltm_xq['member地址(需负载的服务器)'].append(ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['members_address'])
		ltm_xq['member端口'].append(ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['members_port'])
		ltm_xq['负载均衡算法*'].append(ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['load_balancing_mode'])
		ltm_xq['健康检查名称'].append(ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor'])
		ltm_xq['Pool_member地址状态'].append(ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['address_state'])
		if ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor'] in ltm['ltm_monitor']:
			ltm_xq['探测类型*'].append(
				ltm['ltm_monitor'][ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor']][0])
			ltm_xq['检查条件*'].append(
				ltm['ltm_monitor'][ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor']][3])
			ltm_xq['成功返回值*'].append(
				ltm['ltm_monitor'][ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor']][2])
			ltm_xq['探测包发送间隔*'].append(
				ltm['ltm_monitor'][ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor']][1])
			ltm_xq['最大响应时间*'].append(
				ltm['ltm_monitor'][ltm['ltm_pool'][ltm['ltm_virtual'][c]['vs_pool']]['pool_monitor']][4])
	else:
		ltm_xq['member地址(需负载的服务器)'].append('none')
		ltm_xq['member端口'].append('none')
		ltm_xq['负载均衡算法*'].append('none')
		ltm_xq['健康检查名称'].append('none')
		ltm_xq['Pool_member地址状态'].append('none')
		ltm_xq['探测类型*'].append('none')
		ltm_xq['检查条件*'].append('none')
		ltm_xq['成功返回值*'].append('none')
		ltm_xq['探测包发送间隔*'].append('none')
		ltm_xq['最大响应时间*'].append('none')
	# print(ltm_xq)
#
#写入表格：
# data = df.from_dict(rule_sheet,orient='index',columns=column)
data = df.from_dict(ltm_xq, orient='index').T
# data = df(ltm_xq).T
data.reset_index(inplace=True)
data.rename(columns={'index': '序号'}, inplace=True)
data.index = data.index + 1
# print(data)
# column1 = ['Rule_name'] + column
sf = StyleFrame(data)
sf.apply_column_style(cols_to_style=column,
                      styler_obj=Styler(horizontal_alignment='left'),
                      style_header=False)
writer = StyleFrame.ExcelWriter(out_file)
sf.to_excel(
	excel_writer=writer,
	sheet_name=out_file,
	best_fit=column,
	columns_and_rows_to_freeze='B2',
	row_to_add_filters=0,
)
writer.save()
writer.close()
