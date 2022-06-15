#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/13 14:29
# @Author  : lianghongwei
# @File    : fw_to_excel+.py
# @Description :
'''
	本脚本能够通过 "display current-configuration" 日志实现H3C防火墙安全策略的表格化。
'''
import re

import chardet
import os
from pandas import DataFrame as df
from styleframe import StyleFrame , Styler
class FwRule_to_Excle(object):
	def __init__(self):
		"""初始参数"""
		self.column = ['ID', 'Source-Zone', 'Destination-Zone', 'Service_name', 'Service', 'S_ip_name', 'S_ip', 'D_ip_name',
				  'D_ip', 'Description', 'Action']
		self.dir = r'C:\Users\lianghongwei-hzgs\Desktop\LOG'
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
				while True:
					if 'display current-configuration' in file.readline():
						break
				file_list = file.read().split('\n#\n')
				file_name = file_n.split('.')[0]
			yield file_name, file_list
	def pp_data(self):
		"""匹配关键信息到字典中"""
		# 匹配对象
		pat_oser = re.compile(r'object-group service (.*) (description .*)?\n \d+ service (\w+) destination (\w+) (\d+)\n*')
		pat_oip = re.compile(r'')
		pat_oipv6 = re.compile(r'')
		# 匹配rule：
		pat_name = re.compile(r'')
		pat_id = re.compile(r'')
		pat_SourceZone = re.compile(r'')
		pat_DestinationZone = re.compile(r'')
		pat_Service_name = re.compile(r'')
		pat_Service = re.compile(r'')
		pat_Sip_name = re.compile(r'')
		pat_Sip = re.compile(r'')
		pat_Dip_name = re.compile(r'')
		pat_Dip = re.compile(r'')
		pat_Sipv6_name = re.compile(r'')
		pat_Sipv6 = re.compile(r'')
		pat_Dipv6_name = re.compile(r'')
		pat_Dipv6 = re.compile(r'')
		pat_desc = re.compile(r'')
		pat_action = re.compile(r'')

		ob_dit = {}
		rule_dit = {}
		for log_file in FwRule_to_Excle().get_info():
			for line in log_file:
				# 匹配对象
				print(line)
				oser = pat_oser.findall('line')
				print(oser)
				# ob_dit[oser[0]] = oser[1]
				oip = pat_oip.findall('line')
				ob_dit
				oipv6 = pat_oipv6.findall('line')
				# 匹配rule：
				name = pat_name.findall('line')
				id = pat_id.findall('line')
				SourceZone = pat_SourceZone.findall('line')
				DestinationZone = pat_DestinationZone.findall('line')
				Service_name = pat_Service_name.findall('line')
				Service = pat_Service.findall('line')
				Sip_name = pat_Sip_name.findall('line')
				Sip = pat_Sip.findall('line')
				Dip_name = pat_Dip_name.findall('line')
				Dip = pat_Dip.findall('line')
				Sipv6_name = pat_Sipv6_name.findall('line')
				Sipv6 = pat_Sipv6.findall('line')
				Dipv6_name = pat_Dipv6_name.findall('line')
				Dipv6 = pat_Dipv6.findall('line')
				desc = pat_desc.findall('line')
				action = pat_action.findall('line')

		pass
	def write_excel(self, writer, out_file):
		"""主程序，将信息写入表格保持"""
		data = df.from_dict(FwRule_to_Excle.pp_data(), orient='index', columns=self.column)
		data.reset_index(inplace=True)
		data.index = data.index + 1
		data.rename(columns={'index': 'Rule_name'}, inplace=True)
		column1 = ['Rule_name'] + self.column
		sf = StyleFrame(data)
		sf.apply_column_style(cols_to_style=self.column,
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

if __name__=='__main__':
	# for i in FwRule_to_Excle().get_info():
	# 	print(i[0])
	FwRule_to_Excle().pp_data()