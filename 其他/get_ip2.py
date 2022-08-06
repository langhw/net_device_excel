import re, os
from datetime import datetime

def get_ip():
    with open('hw_ip.txt', encoding='utf-8') as f:
        ip_list = []
        # pa_ip = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
        pa_ip = re.compile(r'\d{1,3}(?:\.\d{1,3}){1,3}')
        for line in f.readlines():
            line = line.strip()
            # result = re.findall('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', line)
            result = pa_ip.findall(line)
            ip_list = ip_list + result
        return ip_list
def format_ip():
    ip_format_list = []
    ip_format_list_f = []
    n = 0
    new_file = open('new_hw_ip.txt', 'a+', encoding='utf-8')
    new_file_f = open('new_hw_ip_f.txt', 'a+', encoding='utf-8')
    for ip in get_ip():
        if ip not in ip_format_list and ip not in ip_format_list_f:
            if len(ip.split('.')) == 4:
                ip_format_list.append(ip)
                new_file.write(ip + '\n')
                n += 1
                if n%200 == 0:
                    new_file.write('-*'*5 + '(200 IP)' + '-*'*5 + '\n')
            else:
                ip_format_list_f.append(ip)
                new_file_f.write(ip + '\n')
    new_file.close()
    new_file_f.close()
    return ip_format_list, ip_format_list_f
if __name__ == '__main__':
    start_time = datetime.now()
    os.chdir(r'C:\Users\lianghongwei-hzgs\Documents\hw')
    if os.path.exists('new_hw_ip.txt'):
        os.remove('new_hw_ip.txt')
    if os.path.exists('new_hw_ip_f.txt'):
        os.remove('new_hw_ip_f.txt')
    format_ip()
    os.startfile('new_hw_ip.txt')
    if os.path.getsize('new_hw_ip_f.txt') != 0:
        os.startfile('new_hw_ip_f.txt')
    end_time = datetime.now()
    print('-' * 50)
    print('>>>>所有已经执行完成，总共耗时{:0.2f}秒.<<<'.format((end_time - start_time).total_seconds()))