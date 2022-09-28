# -*- coding: UTF-8 -*-
'''
@Project ：net_device_excel 
@File ：net_dev_xj.py
@Author ：lianghongwei
@Date ：2022/8/15 9:35 
@PRODUCT : PyCharm
'''
import os
import re
import chardet
from pandas import DataFrame as df
from styleframe import StyleFrame, Styler
from datetime import datetime
from openpyxl.reader.excel import load_workbook
from multiprocessing.pool import ThreadPool
from netmiko import ConnectHandler

def get_info():
    """
    获取巡检设备登录信息及巡检命令；
    :return:
    """
    pass
def connect():
    """
    登录网络设备
    :return:
    """
    pass
def cmd_run():
    """
    运行巡检命令，返回结果
    :return:
    """
    pass
def geshihua():
    """
    格式化数据，筛选所需关键信息
    :return:
    """
    dev_xinghao = []
    dev_version = []
    dev_runtime = []
    dev_mem = []
    dev_cpu = []
    dev_env = []
    dev_fan = []
    dev_power = []
    slot_status =[]
    pd_split = re.compile(r'\n<.*>')
    pd_version = re.compile(r'H3C Comware Software, Version (.*), Release')
    pd_runtime = re.compile(r'\n(.*) uptime is (.*)')

    pd_mem = re.compile(r'(Slot \d+):\n.*\nMem:.* (\d+\.\d+%)')

    pd_slot_status = re.compile(r'(\d+)\s+(\S+)\s+(\w+).*')

    pd_slot_cpu = re.compile(r'(\d+)\s+\d+\s+(\d+%)\s+(\d+%)\s+(\d+%)')

    pd_slot_env = re.compile(r' (\d+)\s+(\w+ \d+) (\d+)\s+\d+')

    pd_fan = re.compile(r' (Fan-tray \d):\n Status\s+: (\w+)\n Fan Type\s+: (\S+)')

    pd_power = re.compile(r'\s+(\d+)\s+(\w+)\s+\d+\s+\d+\.\d+\s+\d+\.\d+\s+\d+\.\d+\s+(\S+)')

    for info in log_f():
        info_list = pd_split.split(info[1])
        for line in info_list:
            if 'display version' in line:
                # print(line)
                f_dev_version = pd_version.findall(line)
                f_dev_runtime = pd_runtime.findall(line)
                # print(f_dev_runtime)
                # print(f_dev_version)
                dev_xinghao.append(f_dev_runtime[0][0])
                dev_runtime.append(f_dev_runtime[0][1])
                dev_version.append(f_dev_version[0])
            elif 'display memory' in line:
                f_pd_mem = pd_mem.findall(line)
                dev_mem.append(f_pd_mem)
                # print(f_pd_mem)
            elif 'display device' in line:
                f_pd_slot_status = pd_slot_status.findall(line)
                slot_status.append(f_pd_slot_status)
            elif 'display cpu-usage summary' in line:
                f_pd_slot_cpu = pd_slot_cpu.findall(line)
                # print(f_pd_slot_cpu)
                dev_cpu.append(f_pd_slot_cpu)
            elif 'display environment' in line:
                f_pd_slot_env = pd_slot_env.findall(line)
                dev_env.append(f_pd_slot_env)
                # print(f_pd_slot_env)
            elif 'display fan' in line:
                f_pd_fan = pd_fan.findall(line)
                dev_fan.append(f_pd_fan)
                # print(f_pd_fan)
            elif 'display power' in line:
                f_pd_power = pd_power.findall(line)
                dev_power.append(f_pd_power)
                # print(f_pd_power)

    dev_info = {'xinghao': dev_xinghao, 'version': dev_version, 'runtime': dev_runtime, 'mem': dev_mem, 'cpu': dev_cpu,
                'env': dev_env, 'fan': dev_fan, 'power': dev_power, 'slot': slot_status
                }
    return dev_info
def write_excle():
    """
    将结果保存至表格中
    :return:
    """
    start_time = datetime.now()
    writer = StyleFrame.ExcelWriter('jg.xlsx')
    data = df.from_dict(geshihua(),)
    sf = StyleFrame(data)
    sf.to_excel(
        excel_writer=writer,
        columns_and_rows_to_freeze='B2',
        row_to_add_filters=0,
    )
    writer.save()
    writer.close()
    end_time = datetime.now()
    print('-' * 50)
    print('>>>>所有已经执行完成，总共耗时{:0.2f}秒.<<<'.format((end_time - start_time).total_seconds()))
def log_f():
    """
    临时，打开并读取手动巡检脚本文件
    :return:
    """
    os.chdir(r'C:\Users\lianghongwei-hzgs\Desktop\巡检')
    for log_file in os.listdir():
        with open(log_file, 'rb') as f:
            encod = chardet.detect(f.read(200000))['encoding']
        with open(log_file, 'r', encoding=encod) as file:
            file_list = file.read()
            file_name = log_file.split('.')[0]
        yield file_name, file_list
if __name__=='__main__':
    # write_excle()
    print(geshihua())
    # geshihua()