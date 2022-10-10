# -*- coding: UTF-8 -*-
'''
@Project ：net_device_excel 
@File ：函数模块.py
@Author ：lianghongwei
@Date ：2022/10/8 14:03 
@PRODUCT : PyCharm
'''


import paramiko
# 实例化SSHClient
ssh_client = paramiko.SSHClient()
# 自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接 ，此方法必须放在connect方法的前面
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 连接SSH服务端，以用户名和密码进行认证 ，调用connect方法连接服务器
ssh_client.connect(hostname='192.168.137.105', port=22, username='root', password='123456')
# 打开一个Channel并执行命令  结果放到stdout中，如果有错误将放到stderr中
stdin, stdout, stderr = ssh_client.exec_command('df -hT ')
# stdout 为正确输出，stderr为错误输出，同时是有1个变量有值   # 打印执行结果  print(stdout.read().decode('utf-8'))
# 关闭SSHClient连接
ssh_client.close()

## 密钥连接方式：
# 配置私人密钥文件位置
private = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
#实例化SSHClient
ssh_client = paramiko.SSHClient()
#自动添加策略，保存服务器的主机名和密钥信息，如果不添加，那么不再本地know_hosts文件中记录的主机将无法连接
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#连接SSH服务端，以用户名和密码进行认证
ssh_client.connect(
hostname='192.168.137.100',
port=22,
username='root',
pkey=private
)

## sftp使用：
# 实例化一个transport对象
tran = paramiko.Transport(('192.168.137.100', 22))
# 连接SSH服务端，使用password
tran.connect(username="root", password='123456')
# 或使用
# 配置私人密钥文件位置
private = paramiko.RSAKey.from_private_key_file('/root/.ssh/id_rsa')
# 连接SSH服务端，使用pkey指定私钥
tran.connect(username="root", pkey=private)
# 获取SFTP实例
sftp = paramiko.SFTPClient.from_transport(tran)
# 设置上传的本地/远程文件路径
local_path = "/home/1.txt"
remote_path = "/tmp/1.txt"
# 执行上传动作
sftp.put(local_path, remote_path)
# 执行下载动作
sftp.get(remote_path, local_path)
# 关闭Transport通道
tran.close()
