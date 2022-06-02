#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/1 14:49
# @Author  : lianghongwei
# @File    : H3C_interface_to_excel.py
# @Software: PyCharm
# @Description :
'''脚本功能作用：
    1、将H3C交换机接口信息信息表格化
    2、能够收集的信息包括等接口名称、状态、带宽、流量大小等信息
脚本使用说明：
    H3C交换机接口日志收集方法：
        screen-length disable
        display interface
    需要用的python库：
        re,chardet,pandas,numpy,styleframe,os,file,
'''
import re
import chardet
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler

def Log_file(log_file):
	'''
	将文件进行识别编码并打开文件按照空行分组返回列表
	:return:
	'''
	## 查找日志编码，并打开文件
	encod = ''
	with open(log_file, 'rb') as f:
		encod = chardet.detect(f.read(200000))['encoding']
	with open(log_file, 'r', encoding=encod) as file:
		while True:
			if 'display interface' in file.readline():
				break
		file_list = file.read().split('\n\n')
	return file_list
######
def Matching_information(H3C_interface, log_file):
	'''
	将日志文件逐行分析匹配出需要的信息至字典并返回
	:return:
	'''
	file_list = Log_file(log_file)
	# 定义匹配参数
	pat_interface_name = re.compile(r'^(\w+-?\w+(?:\d+/)*\d+).*', re.S)    #接口名称
	pat_interface_Current_state = re.compile(r'Current state: (.*?)\n', re.S)  # 接口当前状态
	pat_interface_protocol_state = re.compile(r'Line protocol state: (\w+)\n', re.S)  # 接口当前协议状态
	pat_interface_frame_type = re.compile(r'IP packet frame type: (.*?), hardware address: (.*?)\n', re.S)  # 接口类型及MAC
	pat_interface_Description = re.compile(r'Description: (.*?)\n', re.S)  # 接口描述
	pat_interface_Bandwidth = re.compile(r'Bandwidth: (.*?)\n', re.S)  # 接口带宽
	pat_interface_PVID = re.compile(r'PVID: (\d+)\n', re.S)  # 接口本征vlan
	pat_interface_link_type = re.compile(r'Port link-type: (.*?)\n', re.S)  # 接口链路类型
	pat_interface_Media_type = re.compile(r'Media type is (.*?), port hardware type is (.*?)\n', re.S)  # 接口介质类型和硬件类型
	pat_interface_mode = re.compile(r'(.*?)-speed mode, (.*?) mode')  # 接口速率及工作模式
	pat_interface_VLAN_Passing = re.compile(r' VLAN permitted: (.*?)\n', re.S)  # 接口允许通过的vlan号
	pat_interface_encapsulation = re.compile(r' Trunk port encapsulation: (.*?)\n', re.S)  # 接口trunk封装模式
	pat_interface_input = re.compile(r' Last 300 second input: (\d+) packets/sec (\d+) bytes/sec (\d+)%\n', re.S)  # 接口5分钟内进入流量
	pat_interface_output = re.compile(r' Last 300 second output: (\d+) packets/sec (\d+) bytes/sec (\d+)%\n', re.S)  # 接口5分钟内流出流量
	pat_interface_CRC = re.compile(r'	 (\d+) CRC, 0 frame, - overruns, 0 aborts\n', re.S)  # 接口input的crc错误数量
	pat_interface_Peak_input = re.compile(r' Peak input rate: (\d+) bytes/sec, at (.*?)\n', re.S)  # 接口进入流量峰值
	pat_interface_Peak_output = re.compile(r' Peak output rate: (\d+) bytes/sec, at (.*?)\n', re.S)  # 接口流出流量峰值
	pat_interface_ip = re.compile(r'Internet address: (\d+\.\d+\.\d+\.\d+/\d+) \(primary\)\n', re.S)  # 接口IP
	# 逐行分析关键词，并导入字典：
	for line in file_list:
		interface_name = pat_interface_name.findall(line)    #接口名称
		if len(interface_name) != 0:
			H3C_interface['接口名'].append(interface_name[0])
			interface_Current_state = pat_interface_Current_state.findall(line)  # 接口当前状态
			if len(interface_Current_state) == 1:
				H3C_interface['当前状态'].append(interface_Current_state[0])
			else:
				H3C_interface['当前状态'].append('none')
			interface_protocol_state = pat_interface_protocol_state.findall(line)  # 接口当前协议状态
			if len(interface_protocol_state) == 1:
				H3C_interface['协议状态'].append(interface_protocol_state[0])
			else:
				H3C_interface['协议状态'].append('none')
			interface_frame_type = pat_interface_frame_type.findall(line)  # 接口类型及MAC
			if len(interface_frame_type) == 1:
				H3C_interface['接口类型'].append(interface_frame_type[0][0])
				H3C_interface['接口MAC'].append(interface_frame_type[0][1])
			else:
				H3C_interface['接口类型'].append('none')
				H3C_interface['接口MAC'].append('none')
			interface_Description = pat_interface_Description.findall(line)  # 接口描述
			H3C_interface['接口描述'].append(interface_Description[0])
			interface_Bandwidth = pat_interface_Bandwidth.findall(line)  # 接口带宽
			if len(interface_Bandwidth) == 1:
				H3C_interface['接口带宽'].append(interface_Bandwidth[0])
			else:
				H3C_interface['接口带宽'].append('none')
			interface_PVID = pat_interface_PVID.findall(line)  # 接口本征vlan
			if len(interface_PVID) == 1:
				H3C_interface['PVID'].append(interface_PVID[0])
			else:
				H3C_interface['PVID'].append('none')
			interface_link_type = pat_interface_link_type.findall(line)  # 接口链路类型
			if len(interface_link_type) == 1:
				H3C_interface['链路类型'].append(interface_link_type[0])
			else:
				H3C_interface['链路类型'].append('none')
			interface_Media_type = pat_interface_Media_type.findall(line)  # 接口介质类型和硬件类型
			if len(interface_Media_type) == 1:
				H3C_interface['介质类型'].append(interface_Media_type[0][0])
				H3C_interface['硬件类型'].append(interface_Media_type[0][1])
			else:
				H3C_interface['介质类型'].append('none')
				H3C_interface['硬件类型'].append('none')
			interface_mode = pat_interface_mode.findall(line)  # 接口速率及工作模式
			if len(interface_mode) == 1:
				H3C_interface['接口速率'].append(interface_mode[0][0])
				H3C_interface['工作模式'].append(interface_mode[0][1])
			else:
				H3C_interface['接口速率'].append('none')
				H3C_interface['工作模式'].append('none')
			interface_VLAN_Passing = pat_interface_VLAN_Passing.findall(line)  # 接口允许通过的vlan号
			if len(interface_VLAN_Passing) == 1:
				H3C_interface['允许通过的vlan号'].append(interface_VLAN_Passing[0])
			else:
				H3C_interface['允许通过的vlan号'].append('none')
			interface_encapsulation = pat_interface_encapsulation.findall(line)  # 接口trunk封装模式
			if len(interface_encapsulation) == 1:
				H3C_interface['trunk封装'].append(interface_encapsulation[0])
			else:
				H3C_interface['trunk封装'].append('none')
			interface_input = pat_interface_input.findall(line)  # 接口5分钟内进入流量
			interface_output = pat_interface_output.findall(line)  # 接口5分钟内流出流量
			if len(interface_input) != 0:
				H3C_interface['5分钟内进入流量packets/sec'].append(interface_input[0][0])
				H3C_interface['5分钟内进入流量bytes/sec'].append(interface_input[0][1])
				H3C_interface['5分钟内流出流量packets/sec'].append(interface_output[0][0])
				H3C_interface['5分钟内流出流量bytes/sec'].append(interface_output[0][1])
			else:
				H3C_interface['5分钟内进入流量packets/sec'].append('none')
				H3C_interface['5分钟内进入流量bytes/sec'].append('none')
				H3C_interface['5分钟内流出流量packets/sec'].append('none')
				H3C_interface['5分钟内流出流量bytes/sec'].append('none')
			interface_Peak_input = pat_interface_Peak_input.findall(line)  # 接口进入流量峰值
			interface_Peak_output = pat_interface_Peak_output.findall(line)  # 接口流出流量峰值
			if len(interface_Peak_input) != 0:
				H3C_interface['进入流量峰值bytes/sec'].append(interface_Peak_input[0][0])
				H3C_interface['进入流量峰值时间'].append(interface_Peak_input[0][1])
				H3C_interface['流出流量峰值bytes/sec'].append(interface_Peak_output[0][0])
				H3C_interface['流出流量峰值时间'].append(interface_Peak_output[0][1])
			else:
				H3C_interface['进入流量峰值bytes/sec'].append('none')
				H3C_interface['进入流量峰值时间'].append('none')
				H3C_interface['流出流量峰值bytes/sec'].append('none')
				H3C_interface['流出流量峰值时间'].append('none')
			interface_CRC = pat_interface_CRC.findall(line)  # 接口input的crc错误数量
			if len(interface_CRC) == 1:
				H3C_interface['input的CRC'].append(interface_CRC[0])
			else:
				H3C_interface['input的CRC'].append('none')
			interface_ip = pat_interface_ip.findall(line)  # 接口IP
			if len(interface_ip) == 1:
				H3C_interface['IP'].append(interface_ip[0])
			else:
				H3C_interface['IP'].append('none')

	# file.close()
	return H3C_interface
def Table_conversion(column, out_file):
	'''
	将字典转化为表格并保存文件
	:return:
	'''
	info = Matching_information(H3C_interface, log_file)
	data = df.from_dict(info, orient='index').T
	data.reset_index(inplace=True)
	data.rename(columns={'index': '序号'}, inplace=True)
	data.index = data.index + 1
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
if __name__ == '__main__':
	column = ['接口名', '当前状态', '协议状态', '接口类型', 'IP', '接口MAC', '接口描述', '接口带宽', 'PVID', '链路类型', '介质类型',
	          '硬件类型', '接口速率', '工作模式', '允许通过的vlan号', 'trunk封装', '5分钟内进入流量packets/sec',
	          '5分钟内进入流量bytes/sec', '5分钟内流出流量packets/sec', '5分钟内流出流量bytes/sec',
	          '进入流量峰值bytes/sec', '进入流量峰值时间', '流出流量峰值bytes/sec', '流出流量峰值时间', 'input的CRC']
	H3C_interface = {}
	for col in column:
		H3C_interface[col] = []
	## 输入日志文件名称和表格保存的名称：
	log_file = input('Please enter the name of the H3C device log file(Default is conf):') or r'C:\Users\lianghongwei-hzgs\Desktop\H3C'
	out_name = input('Please enter the name of the output table(Default is H3C_interface):') or 'H3C_interface'
	if '.log' not in log_file:
		log_file = '{}.log'.format(log_file)
	if '.xlsx' not in log_file:
		out_name = '{}.xlsx'.format(out_name)

	# print(Matching_information(H3C_interface))
	# Matching_information(H3C_interface, log_file)
	Table_conversion(column, out_name)