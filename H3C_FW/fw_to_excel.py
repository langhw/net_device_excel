#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/5/19 10:29
# @Author  : lianghongwei
# @File    : fw_to_excel.py
# @Description :
'''
	本脚本能够通过 "display current-configuration" 日志实现H3C防火墙安全策略的表格化。
		梁洪伟
		2022-5-13
'''
import chardet
from pandas import DataFrame as df
from styleframe import StyleFrame , Styler
log_file = input('Please enter the name of the H3C device log file(Default is conf):') or 'conf'
out_file = input('Please enter the name of the output table(Default is H3c_FW):') or 'H3c_FW'
if '.log' not in log_file:
	log_file = '{}.log'.format(log_file)
if '.xlsx' not in log_file:
	out_file ='{}.xlsx'.format(out_file)
encod = ''
with open(log_file,'rb') as f:
	encod = chardet.detect(f.read(200000))['encoding']
file = open(log_file,'r',encoding=encod)
file.seek(0)
rule_sheet = {}
object = {}
object_service ={}
for line in file.readlines():
	# if 'object-group ip address' in line:
	if 'object-group ip address' in line or 'object-group ipv6 address' in line:
		line = line.strip('\n')
		line = line.split('address ')
		my1 = line[-1]
		object[my1] = 'none'
		print(my1)
	elif 'network host address' in line or 'network subnet' in line:
		line = line.strip('\n')
		if 'host' in line:
			line = line.split('network host address ')
		else:
			line = line.split('network subnet ')
		my2 = line[-1]

		if object[my1] == 'none':
			object[my1] = my2
		else:
			object[my1] = object[my1] + chr(10) + my2
	if 'object-group service' in line:
		line = line.strip('\n')
		line = line.split('object-group service ')
		s1 = line[-1]
		object_service[s1] = 'none'
	elif 'service tcp destination' in line or 'service udp destination' in line:
		line = line.strip('\n')
		line1 = line.split('destination ')
		line2 = line.split(' ')
		s2 = line1[-1]
		s3 = line2[3]
		if object_service[s1] == 'none':
			object_service[s1] = s3 + '-' + s2
		else:
			object_service[s1] = object_service[s1] + chr(10) + s3 + '-' + s2
	if ' rule ' in line and 'name' in line:
		line = line.strip('\n')
		line = line.split(' ')
		a = line[4]
		rule_sheet[a] = [line[2]]#0 id
		rule_sheet[a].append('any')#1 s_zone
		rule_sheet[a].append('any')#2 d_zone
		rule_sheet[a].append('any')#3 s_n
		rule_sheet[a].append('any')#4 service
		rule_sheet[a].append('any')#5 s_ip
		rule_sheet[a].append('any')#6 source-ip
		rule_sheet[a].append('any')#7 d_ip
		rule_sheet[a].append('any')#8 destination-ip
		rule_sheet[a].append('')#9 description
		rule_sheet[a].append('')#10 active
	elif '  description ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		rule_sheet[a][9] = line[-1]
	elif '  action ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		rule_sheet[a][10] = line[-1]
	elif '  source-zone ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		b = line[-1]
		if rule_sheet[a][1] == 'any':
			rule_sheet[a][1] = b
		else:
			rule_sheet[a][1] = rule_sheet[a][1] + chr(10) + b

	elif '  destination-zone ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		c = line[-1]
		if rule_sheet[a][2] == 'any':
			rule_sheet[a][2] = c
		else:
			rule_sheet[a][2] = rule_sheet[a][2] + chr(10) + c

	elif '  service ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		d = line[-1]
		if rule_sheet[a][3] == 'any':
			rule_sheet[a][3] = d
		else:
			rule_sheet[a][3] = rule_sheet[a][3] + chr(10) + d
	elif '  source-ip ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		e = line[-1]
		if rule_sheet[a][5] == 'any':
			rule_sheet[a][5] = e
		else:
			rule_sheet[a][5] = rule_sheet[a][5] + chr(10) + e
	elif '  destination-ip ' in line:
		line = line.strip('\n')
		line = line.split(' ')
		f = line[-1]
		if rule_sheet[a][7] == 'any':
			rule_sheet[a][7] = f
		else:
			rule_sheet[a][7] = rule_sheet[a][7] + chr(10) + f
file.close()
for rule in rule_sheet:
	if rule_sheet[rule][3] != 'any':
		rule_sheet[rule][4] = ''
		ser = rule_sheet[rule][3].split(chr(10))
		for service in ser:
			try:
				rule_sheet[rule][4] = rule_sheet[rule][4] + chr(10) + object_service[service]
			except KeyError:
				rule_sheet[rule][4] = rule_sheet[rule][4] + chr(10) + service
	if rule_sheet[rule][5] != 'any':
		rule_sheet[rule][6] = ''
		s_ip = rule_sheet[rule][5].split(chr(10))
		for addr in s_ip:
			rule_sheet[rule][6] = rule_sheet[rule][6] + chr(10) + chr(10) + object[addr]
	if rule_sheet[rule][7] != 'any':
		rule_sheet[rule][8] = ''
		d_ip = rule_sheet[rule][7].split(chr(10))
		for addr in d_ip:
			rule_sheet[rule][8] = rule_sheet[rule][8] + chr(10) + chr(10) + object[addr]
# print(rule_sheet)
column = ['ID','Source-Zone','Destination-Zone','Service_name','Service','S_ip_name','S_ip','D_ip_name','D_ip','Description','Action']
data = df.from_dict(rule_sheet,orient='index',columns=column)
data.reset_index(inplace=True)
data.index = data.index + 1
data.rename(columns={'index':'Rule_name'},inplace=True)
# print(data)
column1 = ['Rule_name'] + column
sf = StyleFrame(data)
sf.apply_column_style(cols_to_style=column,
                      styler_obj=Styler(horizontal_alignment='left'),
                      style_header=False)
writer = StyleFrame.ExcelWriter(out_file)
sf.to_excel(
	excel_writer=writer,
	sheet_name=out_file,
	best_fit=column1,
	columns_and_rows_to_freeze='B2',
	row_to_add_filters=0,
)
writer.save()
writer.close()
