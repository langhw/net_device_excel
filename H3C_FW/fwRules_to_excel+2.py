#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2022/6/13 14:29
# @Author  : lianghongwei
# @File    :
# @Description :
'''
	本脚本能够通过 "display current-configuration" 日志实现H3C防火墙安全策略的表格化。
'''
import re
import chardet
import os
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler
from datetime import datetime


class FwRule_to_Excle(object):
    def __init__(self):
        """初始参数"""
        self.column = ['ID', 'Source-Zone', 'Destination-Zone', 'S_ip_name', 'S_ip', 'D_ip_name', 'D_ip',
                       'Service_name', 'Protocol', 'Port', 'Description', 'Action', 'State']
        self.dir = r'C:\Users\lianghongwei-hzgs\Desktop\LOG'
        self.log = 'JG'
        if not os.path.exists(self.log): os.mkdir(self.log)
        self.logtime = datetime.now().strftime('%Y-%m-%d_%H')
        self.dirpath = os.path.join(self.log, self.logtime + '_FWrules.xlsx')

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
                    else:
                        break
                file_list = file.read().split('\n#\n')
                file_name = file_n.split('.')[0]
            yield file_name, file_list

    def pp_data(self):
        """匹配关键信息到字典中"""
        # 定义匹配地址对象
        pd_object_a_n = re.compile(r'object-group (?:ip|ipv6) address (.*)')
        pd_object_a = re.compile(r'(?: \d+ network (?:host address|subnet|host name|range) (.*))+')
        # 定义匹配服务对象
        pd_object_s_n = re.compile(r'object-group service (.*)')
        # pd_object_s = re.compile(r'(?: \d+ service (\w+) destination (\w+) (\d+))+')
        pd_object_s = re.compile(r'(?: \d+ service (\w+) destination (.*))+')
        # 定义匹配安全策略
        pd_rule_name = re.compile(r'(\d+) name (.*)')
        pd_rule_desc = re.compile(r'  description (.*)')
        pd_rule_action = re.compile(r'  action (\w+)')
        pd_rule_state = re.compile(r'  (disable)')
        pd_rule_sz = re.compile(r'  source-zone (\w+)')
        pd_rule_dz = re.compile(r'  destination-zone (\w+)')
        pd_rule_si = re.compile(r'  source-ip (.*)')
        pd_rule_di = re.compile(r'  destination-ip (.*)')
        pd_rule_s = re.compile(r'  service (.*)')
        #
        for file in self.get_info():
            file_name = file[0]
            ob_a_t = {'any': 'any'}  # 对象地址字典
            ob_s_t = {'any': ['any', 'any']}  # 对象服务字典
            rule_t = {}  # 安全策略字典
            for line in file[1]:
                if 'object-group ip address' in line or 'object-group ipv6 address' in line:
                    ob_a_n = pd_object_a_n.findall(line)[0]  # 找到地址对象的名称
                    ob_a = pd_object_a.findall(line)  # 找到地址对象的地址信息
                    n = 0
                    if len(ob_a) != 0:
                        while n < len(ob_a):
                            if n == 0:
                                ob_a_t[ob_a_n] = ob_a[n]
                            else:
                                ob_a_t[ob_a_n] = ob_a_t[ob_a_n] + chr(10) + ob_a[n]
                            n += 1
                    else:
                        ob_a_t[ob_a_n] = 'None'
                elif 'object-group service' in line:
                    ob_s_n = pd_object_s_n.findall(line)[0]  # 找到服务对象的名称
                    ob_s = pd_object_s.findall(line)  # 找到服务对象的服务信息，包括协议类型，协议指定，协议端口号
                    ob_s_t[ob_s_n] = []  # 服务对象为列表，0是协议，1是端口
                    n = 0
                    if len(ob_s) != 0:
                        while n < len(ob_s):
                            if n == 0:
                                ob_s_t[ob_s_n].append(ob_s[n][0])
                                ob_s_t[ob_s_n].append(ob_s[n][1])
                            else:
                                ob_s_t[ob_s_n][0] = ob_s_t[ob_s_n][0] + chr(10) + ob_s[n][0]
                                ob_s_t[ob_s_n][1] = ob_s_t[ob_s_n][1] + chr(10) + ob_s[n][1]
                            n += 1
                    else:
                        ob_s_t[ob_s_n].append('None')
                        ob_s_t[ob_s_n].append('None')
                elif 'security-policy ip' in line:
                    rule_line = line.split(' rule ')
                    for rule in rule_line[1:]:
                        n1 = n2 = n3 = n4 = n5 = 0
                        rule_id = pd_rule_name.findall(rule)[0][0]
                        rule_name = pd_rule_name.findall(rule)[0][1]
                        rule_desc = pd_rule_desc.findall(rule)
                        rule_action = pd_rule_action.findall(rule)
                        rule_state = pd_rule_state.findall(rule)
                        rule_sz = pd_rule_sz.findall(rule)
                        rule_dz = pd_rule_dz.findall(rule)
                        rule_si = pd_rule_si.findall(rule)
                        rule_di = pd_rule_di.findall(rule)
                        rule_s = pd_rule_s.findall(rule)
                        #
                        if len(rule_desc) != 0:
                            rule_desc = rule_desc[0]
                        else:
                            rule_desc = ''
                        if len(rule_action) != 0:
                            rule_action = rule_action[0]
                        else:
                            rule_action = 'Drop'
                        if len(rule_state) != 0:
                            rule_state = rule_state[0]
                        else:
                            rule_state = 'enable'
                        if len(rule_sz) == 0:
                            rule_sz = ['any']
                        if len(rule_dz) == 0:
                            rule_dz = ['any']
                        if len(rule_si) == 0:
                            rule_si = ['any']
                        if len(rule_di) == 0:
                            rule_di = ['any']
                        if len(rule_s) == 0:
                            rule_s = ['any']
                        #
                        while n1 < len(rule_sz):
                            if n1 == 0:
                                rule_sz_m = rule_sz[n1]
                            else:
                                rule_sz_m = rule_sz_m + chr(10) + rule_sz[n1]
                            n1 += 1
                        while n2 < len(rule_dz):
                            if n2 == 0:
                                rule_dz_m = rule_dz[n2]
                            else:
                                rule_dz_m = rule_dz_m + chr(10) + rule_dz[n2]
                            n2 += 1
                        while n3 < len(rule_si):
                            if n3 == 0:
                                rule_si_m = [rule_si[n3], ob_a_t[rule_si[n3]]]
                            else:
                                rule_si_m[0] = rule_si_m[0] + chr(10) + '-' * 10 + chr(10) + rule_si[n3]
                                rule_si_m[1] = rule_si_m[1] + chr(10) + '-' * 10 + chr(10) + ob_a_t[rule_si[n3]]
                            n3 += 1
                        while n4 < len(rule_di):
                            if n4 == 0:
                                rule_di_m = [rule_di[n4], ob_a_t[rule_di[n4]]]

                            else:
                                rule_di_m[0] = rule_di_m[0] + chr(10) + '-' * 10 + chr(10) + rule_di[n4]
                                rule_di_m[1] = rule_di_m[1] + chr(10) + '-' * 10 + chr(10) + ob_a_t[rule_di[n4]]
                            n4 += 1
                        while n5 < len(rule_s):
                            if rule_s[n5] not in ob_s_t:
                                ob_s_t[rule_s[n5]] = ['Predefined', rule_s[n5]]
                            if n5 == 0:
                                rule_s_m = [rule_s[n5], ob_s_t[rule_s[n5]][0], ob_s_t[rule_s[n5]][1]]
                            else:
                                rule_s_m[0] = rule_s_m[0] + chr(10) + '-' * 10 + chr(10) + rule_s[n5]
                                rule_s_m[1] = rule_s_m[1] + chr(10) + '-' * 10 + chr(10) + ob_s_t[rule_s[n5]][0]
                                rule_s_m[2] = rule_s_m[2] + chr(10) + '-' * 10 + chr(10) + ob_s_t[rule_s[n5]][1]
                            n5 += 1
                        #
                        rule_t[rule_name] = []
                        rule_t[rule_name].append(rule_id)
                        rule_t[rule_name].append(rule_sz_m)
                        rule_t[rule_name].append(rule_dz_m)
                        rule_t[rule_name].append(rule_si_m[0])
                        rule_t[rule_name].append(rule_si_m[1])
                        rule_t[rule_name].append(rule_di_m[0])
                        rule_t[rule_name].append(rule_di_m[1])
                        rule_t[rule_name].append(rule_s_m[0])
                        rule_t[rule_name].append(rule_s_m[1])
                        rule_t[rule_name].append(rule_s_m[2])
                        rule_t[rule_name].append(rule_desc)
                        rule_t[rule_name].append(rule_action)
                        rule_t[rule_name].append(rule_state)
            yield file_name, rule_t

    def write_excel(self):
        """主程序，将信息写入表格保持"""
        start_time = datetime.now()
        writer = StyleFrame.ExcelWriter(self.dirpath)
        for pp in self.pp_data():
            data = df.from_dict(pp[1], orient='index', columns=self.column)
            data.reset_index(inplace=True)
            data.index = data.index + 1
            data.rename(columns={'index': 'Rule_name'}, inplace=True)
            column1 = ['Rule_name'] + self.column
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
        end_time = datetime.now()
        print('-' * 50)
        print('>>>>所有已经执行完成，总共耗时{:0.2f}秒.<<<'.format((end_time - start_time).total_seconds()))


if __name__ == '__main__':
    FwRule_to_Excle().write_excel()
