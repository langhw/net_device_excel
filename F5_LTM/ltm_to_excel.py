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
#ltm_pool
pattern_pooname = re.compile(r'ltm pool /w+//')




# ## 输入LTM日志文件名称和表格保存的名称：

log_file = input('Please enter the name of the F5_LTM device log file(Default is conf):') or 'kfcs_all'
out_file = input('Please enter the name of the output table(Default is F5_LTM):') or 'F5_LTM'
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
# ## 逐行分析关键词，并导入字典：
for line in file.readlines():
        ### 健康检查信息收集：
    if wkey[1] in line:
        a = line[line.index(wkey[1]):line.index(' {')]
        b = line[line.index('{ '):line.index(' send')].replace('{ ', '')
        c = line[line.index('send '):line.index(' time-until-up ')].split('send ')[-1]
        d = line[line.index('time-until-up '):line.index(' }')].rstrip('\n')
        e = b + ' time-until-u' + d
        e_list = e.split(' ')
        monitor_name = a.split('/')[-1]
        monitor_type = a.split(' ')[2]
        ltm_monitor[monitor_name] = {}
        ltm_monitor[monitor_name]['monitor_type'] = monitor_type
        ltm_monitor[monitor_name]['send'] = c
        for n in range(0, int(len(e_list)), 2):
            ltm_monitor[monitor_name][e_list[n]] = e_list[n+1]
    elif wkey[2] in line:
        a1 = line[line.index(wkey[2]):line.index(' { allow')]
        b1 = re.split(r' { | } ', line)
        pool_name = a.split('/')[-1]
        ltm_pool[pool_name] = {}
        ltm_pool[pool_name]['members_address'] = ''
        ltm_pool[pool_name]['members_port'] = ''
        ltm_pool[pool_name]['members_state'] = ''
        ltm_pool[pool_name]['partition'] = ''
        ltm_pool[pool_name]['monitor'] = ''
        print(line)
        for n1 in b1:
            if '/' in n1 and ':' in n1:
                c1 = re.split('/|:', n1)
                if '' in ltm_pool[pool_name]['members_address']:
                    ltm_pool[pool_name]['members_address'] = c1[-2]
                else:
                    ltm_pool[pool_name]['members_address'] = ltm_pool[pool_name]['members_address'] + chr(10) + c1[-2]
                ltm_pool[pool_name]['members_port'] = c1[-1]
            elif ' state ' in n1:
                d1 = n1.split(' ')
                if '' in ltm_pool[pool_name]['members_state']:
                    ltm_pool[pool_name]['members_state'] = d1[-2]
                else:
                    ltm_pool[pool_name]['members_state'] = ltm_pool[pool_name]['members_state'] + chr(10) + d1[-2]
            elif 'partition' in n1:
                e1 = n1.split(' ')
                ltm_pool[pool_name]['partition'] = e1[1]
            elif ltm_pool[pool_name]['partition'] + '/' in n1:
                f1 = n1.split(ltm_pool[pool_name]['partition'] + '/')
                for g1 in f1:
                    if '' in ltm_pool[pool_name]['monitor']:
                        ltm_pool[pool_name]['monitor'] = g1
                    else:
                        ltm_pool[pool_name]['monitor'] = ltm_pool[pool_name]['monitor'] + chr(10) + g1

print(ltm_pool)

