#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:33
# @Author  : lianghongwei
# @File    : ltm_to_excel(yes).py
# @Description :
import re
from pandas import DataFrame as df
import pandas as pd

def vs_list(ltm_virtual_file = 'vs.txt'):
	try:
		file = open(ltm_virtual_file,'r',encoding='utf-8')
	except FileNotFoundError:
		exit('没有找到{}文件，退出程序'.format(ltm_virtual_file))
	file.seek(0)
	w0 = "    partition"
	w1 = "ltm virtual "
	w2 = "    destination"
	w3 = "    ip-protocol"
	w4 = "    pool "
	w5 = "    enabled"
	w5_1 = "    disabled"
	w6 = ".com"
	w7 = "        pool "
	w8 = "_cookie_"
	w9 = "            context "
	ltm_virtual = {}
	for i in file.readlines():
		i = i.replace('{','')
		i = i.replace('\n','')
		if w1 in i:
			name_partation = i.split('/')[1]
			name_virtual = i.split('/')[-1]
			ltm_virtual[name_virtual] = {}
			ltm_virtual[name_virtual]['partition'] = 'none'
			ltm_virtual[name_virtual]['vs_addr'] = 'none'
			ltm_virtual[name_virtual]['vs_port'] = 'none'
			ltm_virtual[name_virtual]['protocol'] = 'none'
			ltm_virtual[name_virtual]['pool'] = 'none'
			ltm_virtual[name_virtual]['status'] = 'none'
			ltm_virtual[name_virtual]['snat_pool'] = 'none'
			ltm_virtual[name_virtual]['ssl_ca'] = []
			ltm_virtual[name_virtual]['cookie_name'] = 'none'
		elif w0 in i:
			partition = i.split(' ')[-1]
			ltm_virtual[name_virtual]['partition'] = partition
		elif w2 in i:
			destinations = re.sub("%10[0-9]:"," ",str(i))
			destination = re.split(' ',destinations)
			destination_addr = destination[-2]
			destination_port = destination[-1]
			ltm_virtual[name_virtual]['vs_addr'] = destination_addr
			ltm_virtual[name_virtual]['vs_port'] = destination_port
		elif w3 in i:
			ip_protocol = i.split(' ')[-1]
			ltm_virtual[name_virtual]['protocol'] = ip_protocol
		elif w4 in i:
			if w7 in i:
				snat = i.split(' ')[-1]
				ltm_virtual[name_virtual]['snat_pool'] = snat
			else:
				pool_name = i.split(' ')[-1]
				ltm_virtual[name_virtual]['pool'] = pool_name
		elif w5 in i:
			status = i.split(' ')[-1]
			ltm_virtual[name_virtual]['status'] = status
		elif w5_1 in i:
			status1 = i.split(' ')[-1]
			ltm_virtual[name_virtual]['status'] = status1
		elif w6 in i:
			ca = i.split('/')[-1]
			ltm_virtual[name_virtual]['ssl_ca'].append(ca)
		elif w9 in i:
			context = i.split(' ')[-1]
			if 'all' != context:
				ltm_virtual[name_virtual]['ssl_ca'].append(context)
		elif w8 in i:
			cookie = i.split('/')[-1]
			ltm_virtual[name_virtual]['cookie_name'] = cookie
		else:
			continue
	file.close()
	return ltm_virtual

def pool_list(ltm_pool_file = 'pool.txt'):
	try:
		file = open(ltm_pool_file,'r',encoding='utf-8')

	except FileNotFoundError:
		exit('没有找到{}文件，退出程序'.format(ltm_pool_file))
	file.seek(0)
	w1 = "ltm pool "
	w2 = "    load-balancing-mode "
	w3 = "        /"
	w4 = "            state "
	w5 = "    monitor "
	w6 = "    partition "
	ltm_pool = {}
	for i in file.readlines():
		i = i.replace('{','')
		i = i.replace('\n','')
		if w1 in i:
			name_pool = i.split(' ')[-2]
			ltm_pool[name_pool] = {}
			ltm_pool[name_pool]['members'] = []
			ltm_pool[name_pool]['load_balancing-mode'] = 'none'
			ltm_pool[name_pool]['monitor'] = 'none'

		elif w2 in i:
			mode = i.split(' ')[-1]
			ltm_pool[name_pool]['load_balancing-mode'] = mode
		elif w3 in i:
			members = re.split(" |/|:",i)
			members_addr = members[-3]
			members_port = members[-2]
			ltm_pool[name_pool]['members'].append(members_addr)
			ltm_pool[name_pool]['members'].append(members_port)
		elif w4 in i:
			state = i.split(' ')[-1]
			ltm_pool[name_pool]['members'].append(state)
		elif w5 in i:
			if "           monitor " not in i:
				monitor = i.split('/')[-1]
				ltm_pool[name_pool]['monitor'] = monitor
		else:
			continue
	file.close()
	return ltm_pool

F5_name = input('请输入F5的名称：\n') or 'F5_ltm'
ltm_virtual_file = input('请输入F5的“list ltm virtual all-properties”命令日志文件位置及名称：\n')
ltm_pool_file = input('请输入F5的“list ltm pool all-properties”命令日志文件位置及名称：\n')
#print("脚本执行中，请稍等……")
if ltm_virtual_file == '':
	ltm_virtual = vs_list()
else:
	ltm_virtual = vs_list(ltm_virtual_file)
if ltm_pool_file == '':
	ltm_pool = pool_list()
else:
	ltm_pool = pool_list(ltm_pool_file)
for key in ltm_virtual:
	try:
		pool = ltm_virtual[key]['pool']
#		ltm_virtual[key]['pool_member'] = ltm_pool[pool]
		ltm_virtual[key].update(ltm_pool[pool])

	except KeyError:
#		ltm_virtual[key]['pool_member'] = 'none'
		pass
	ltm_virtual[key]['snat_pool'] = ltm_virtual[key]['snat_pool'].split('/')[-1]
	ltm_virtual[key]['pool'] = ltm_virtual[key]['pool'].split('/')[-1]

export = F5_name + ".xlsx"
data = df(ltm_virtual).T
writer = pd.ExcelWriter(export)
data.to_excel(writer)
writer.save()
writer.close()
quit("已经生成{}，请查看，谢谢！".format(export))