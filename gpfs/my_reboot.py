import os
import shutil
import time
import requests
import json
import xlrd

all_dir = "/root/"
file_name = "gps.xlsx"
gps_software = "./gpfs"



headers = {"Connection": "close", "Cache-Control": "max-age=0", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "sec-ch-ua-mobile": "?0", "DNT": "1", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"}



# 获取钱包地址
def init_address():
    xls = xlrd.open_workbook(file_name)
    addresses = xls.sheets()[0].col_values(0)
    return addresses

# 监控掉线重启
def reboot():
    while True:
        bsc = init_address()
        time.sleep(3*60)
        for i in range(len(bsc)):
            try:
                url = "https://api.gpfs.xyz/v1/miners?page=1&limit=20&address=" + bsc[i]
                res = requests.get(url, headers=headers,timeout=60)
                text = json.loads(res.text)
                print(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())))
                print("监测地址："+text['data']['miners'][0]['address'] + "状态:"+text['data']['miners'][0]['state'])
                if text['data']['miners'][0]['state'] != u"在线":
                    p = os.popen('ps -ef | grep '+ bsc[i] +' | grep -v grep')
                    t = p.read().strip()
                    if (t != ''):
                        pid = t.split()[1]
                        print(pid)
                        print('sudo kill '+str(pid))
                        os.system('sudo kill ' + str(pid))

                    dir = all_dir + str(bsc[i])
                    print("正在重启"+ bsc[i])
                    os.system("screen -dmS "+ bsc[i] +" bash -c \"sh "+dir+"/run.sh\"")
                    print("重启完成screen -dmS "+ bsc[i] +" bash -c \"sh "+dir+"/run.sh\"")
            except:
                print("获取错误")

if __name__ == '__main__':
    reboot()