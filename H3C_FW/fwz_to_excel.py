#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/13 14:29
# @Author  : lianghongwei
# @File    : fw_to_excel+.py
# @Description :
'''
	本脚本能够通过 "screen-length disable  和 display ip routing-table 和 display security-zone" 日志实现H3C防火墙网络的安全区域表格化。
'''
import re
import chardet
import os
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler

class FwZone_to_Excle(object):
	def __init__(self):
		"""初始参数"""
		self.column = ['Interface', 'Zone']
		self.dir = r'C:\Users\lianghongwei-hzgs\Desktop\zon'
	def get_dir(self):
		for log_file in os.listdir(self.dir):
			yield log_file
	def get_info(self):
		"""读取配置文件，并将文件格式化到列表中"""
		for file_n in self.get_dir():
			log_file = os.path.join(self.dir, file_n)
			with open(log_file, 'rb') as f:
				encod = chardet.detect(f.read(200000))['encoding']
			with open(log_file, 'r', encoding=encod) as file:
				# while True:
				# 	if 'display current-configuration' in file.readline():
				# 		break
				file_list = file.read()
				pd_ip = re.compile(r'>display ip routing-table \n.*Interface\n(.*?)\n<', re.DOTALL)
				pd_zone = re.compile(r'>display security-zone \n(.*?)\n\n<', re.DOTALL)
				ip_info = pd_ip.findall(file_list)
				zone_info = pd_zone.findall(file_list)
				file_name = file_n.split('.')[0]
			yield file_name, ip_info, zone_info
	def pp_data(self):
		"""匹配关键信息到字典中"""
		ip_dit = {}
		zone_dit = {}
		pd_z = re.compile(r'Name: (.*?)\n')
		pd_i = re.compile(r'\n  (.*)')
		for line in self.get_info():
			zone_info = line[2][0].split('\n\n')
			for zone in zone_info:
				z = pd_z.findall(zone)
				i = pd_i.findall(zone)
				n = 0
				while n < len(i):
					zone_dit[i[n]] = z[0]
					n += 1
			ip_info = line[1][0].split('\n')
			for ip in ip_info:
				net = ip.split(' ')[0]
				interface = ip.split(' ')[-1]
				if interface in zone_dit:
					ip_dit[net] = [interface, zone_dit[interface]]
			yield line[0], ip_dit
	def write_excel(self, out_file):
		"""主程序，将信息写入表格保持"""
		writer = StyleFrame.ExcelWriter(out_file)
		for pp in self.pp_data():
			data = df.from_dict(pp[1], orient='index', columns=self.column)
			data.reset_index(inplace=True)
			data.index = data.index + 1
			data.rename(columns={'index': 'NetWork'}, inplace=True)
			column1 = ['NetWork'] + self.column
			sf = StyleFrame(data)
			sf.apply_column_style(cols_to_style=self.column,
			                      styler_obj=Styler(horizontal_alignment='left'),
			                      style_header=False)
			sf.to_excel(
				excel_writer=writer,
				sheet_name=pp[0],
				best_fit=column1,
				columns_and_rows_to_freeze='B2',
				row_to_add_filters=0,
			)
			writer.save()
		writer.close()

if __name__ == '__main__':
	FwZone_to_Excle().write_excel('test.xlsx')
	# for i in FwZone_to_Excle().pp_data():
	# 	print(i)