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

def Log_file():
	'''
	输入文件名，将文件进行识别编码并打开文件返回
	:return:
	'''
	## 输入日志文件名称和表格保存的名称：
	log_file = input('Please enter the name of the H3C device log file(Default is conf):') or r'C:\Users\lianghw\Desktop\H3C'
	out_name = input('Please enter the name of the output table(Default is H3C_interface):') or 'H3C_interface'
	if '.log' not in log_file:
		log_file = '{}.log'.format(log_file)
	if '.xlsx' not in log_file:
		out_name = '{}.xlsx'.format(out_name)
	## 查找日志编码，并打开文件
	encod = ''
	with open(log_file, 'rb') as f:
		encod = chardet.detect(f.read(200000))['encoding']
	file_list = ['']
	with open(log_file, 'r', encoding=encod) as file:
		m = len(file.readlines())
		n = m1 = 0
		file.seek(0)
		while m1 <= m:
			cont = file.readline().replace('\n', ' ')
			if not cont:
				file_list.append('')
				n += 1
				m1 += 1
			else:
				file_list[n] = file_list[n] + cont
				m1 += 1
	return file_list
######
def Matching_information():
	'''
	将日志文件逐行分析匹配出需要的信息至字典并返回
	:return:
	'''
	file = Log_file()
	# 定义匹配参数
	pat_interface_name = re.compile(r'(^/w+-/w+/d+$|^/w+-?(/d/)*/d+$)')    #接口名称
	pat_interface_Current_state = re.compile(r'Current state: (/w+)')  # 接口当前状态
	pat_interface_protocol_state = re.compile(r'Line protocol state: (/w+)')  # 接口当前协议状态
	pat_interface_frame_type = re.compile(r'IP packet frame type: (.*?), hardware address: (.*?)')  # 接口类型及MAC
	pat_interface_Description = re.compile(r'Description: (.*?)')  # 接口描述
	pat_interface_Bandwidth = re.compile(r'Bandwidth: (.*?)')  # 接口带宽
	pat_interface_PVID = re.compile(r'PVID: (/d+)')  # 接口本征vlan
	pat_interface_link_type = re.compile(r'Port link-type: (.*?)')  # 接口链路类型
	pat_interface_Media_type = re.compile(r'Media type is (.*?), port hardware type is (.*?)')  # 接口介质类型和硬件类型
	pat_interface_mode = re.compile(r'(.*?) mode, (.*?) mode')  # 接口速率及工作模式
	pat_interface_VLAN_Passing = re.compile(r' VLAN permitted: (.*?)')  # 接口允许通过的vlan号
	pat_interface_encapsulation = re.compile(r' Trunk port encapsulation: (.*?)')  # 接口trunk封装模式
	pat_interface_input = re.compile(r' Last 300 second input: (/d+) packets/sec (/d+) bytes/sec (/d+)%')  # 接口5分钟内进入流量
	pat_interface_output = re.compile(r' Last 300 second output: (/d+) packets/sec (/d+) bytes/sec (/d+)%')  # 接口5分钟内流出流量
	pat_interface_CRC = re.compile(r'	 (/d+) CRC, 0 frame, - overruns, 0 aborts')  # 接口input的crc错误数量
	pat_interface_Peak_input = re.compile(r' Peak input rate: (/d+) bytes/sec, at (.*?) ')  # 接口进入流量峰值
	pat_interface_Peak_output = re.compile(r' Peak output rate: (/d+) bytes/sec, at (.*?) ')  # 接口流出流量峰值
	# 逐行分析关键词，并导入字典：
	# for line in file.readlines():
	for line in file:
		interface_name = pat_interface_name.findall(line)    #接口名称
		H3C_interface['接口名'].append(interface_name)
		interface_Current_state = pat_interface_Current_state.findall(line)  # 接口当前状态
		H3C_interface['当前状态'].append(interface_Current_state)
		interface_protocol_state = pat_interface_protocol_state.findall(line)  # 接口当前协议状态
		H3C_interface['协议状态'].append(interface_protocol_state)
		interface_frame_type = pat_interface_frame_type.findall(line)  # 接口类型及MAC
		H3C_interface['接口类型'].append(interface_frame_type[0])
		H3C_interface['接口MAC'].append(interface_frame_type[1])
		interface_Description = pat_interface_Description.findall(line)  # 接口描述
		H3C_interface['接口描述'].append(interface_Description)
		interface_Bandwidth = pat_interface_Bandwidth.findall(line)  # 接口带宽
		H3C_interface['接口带宽'].append(interface_Bandwidth)
		interface_PVID = pat_interface_PVID.findall(line)  # 接口本征vlan
		H3C_interface['PVID'].append(interface_PVID)
		interface_link_type = pat_interface_link_type.findall(line)  # 接口链路类型
		H3C_interface['链路类型'].append(interface_link_type)
		interface_Media_type = pat_interface_Media_type.findall(line)  # 接口介质类型和硬件类型
		H3C_interface['介质类型'].append(interface_Media_type[0])
		H3C_interface['硬件类型'].append(interface_Media_type[1])
		interface_mode = pat_interface_mode.findall(line)  # 接口速率及工作模式
		H3C_interface['接口速率'].append(interface_mode[0])
		H3C_interface['工作模式'].append(interface_mode[1])
		interface_VLAN_Passing = pat_interface_VLAN_Passing.findall(line)  # 接口允许通过的vlan号
		H3C_interface['允许通过的vlan号'].append(interface_VLAN_Passing)
		interface_encapsulation = pat_interface_encapsulation.findall(line)  # 接口trunk封装模式
		H3C_interface['trunk封装'].append(interface_encapsulation)
		interface_input = pat_interface_input.findall(line)  # 接口5分钟内进入流量
		H3C_interface['5分钟内进入流量packets//sec'].append(interface_input[0])
		H3C_interface['5分钟内进入流量bytes//sec'].append(interface_input[1])
		interface_output = pat_interface_output.findall(line)  # 接口5分钟内流出流量
		H3C_interface['5分钟内流出流量packets//sec'].append(interface_output[0])
		H3C_interface['5分钟内流出流量bytes//sec'].append(interface_output[1])
		interface_Peak_input = pat_interface_Peak_input.findall(line)  # 接口进入流量峰值
		H3C_interface['进入流量峰值bytes//sec'].append(interface_Peak_input[0])
		H3C_interface['进入流量峰值时间'].append(interface_Peak_input[1])
		interface_Peak_output = pat_interface_Peak_output.findall(line)  # 接口流出流量峰值
		H3C_interface['流出流量峰值bytes//sec'].append(interface_Peak_output[0])
		H3C_interface['流出流量峰值时间'].append(interface_Peak_output[1])
		interface_CRC = pat_interface_CRC.findall(line)  # 接口input的crc错误数量
		H3C_interface['input的crc'].append(interface_CRC)
	# file.close()
	return H3C_interface
def Table_conversion():
	'''
	将字典转化为表格并保存文件
	:return:
	'''
if __name__ == '__main__':
	column = ['接口名', '当前状态', '协议状态', '接口类型', '接口MAC', '接口描述', '接口带宽', 'PVID', '链路类型', '介质类型', \
	          '硬件类型', '接口速率', '工作模式', '允许通过的vlan号', 'trunk封装', '5分钟内进入流量packets//sec', \
	          '5分钟内进入流量bytes//sec', '5分钟内流出流量packets//sec', '5分钟内流出流量bytes//sec', \
	          '进入流量峰值bytes//sec', '进入流量峰值时间', '流出流量峰值bytes//sec', '流出流量峰值时间', 'input的crc']
	H3C_interface = {}
	for col in column:
		H3C_interface[col] = []

	print(Matching_information())
