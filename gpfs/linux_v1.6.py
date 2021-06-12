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

# 启动挖矿
def linux():
    bsc = init_address()
    for i in range(len(bsc)):
        dir = all_dir + str(bsc[i])
        os.mkdir(dir)
        shutil.copy(gps_software, dir)
        with(open(dir + "/run.sh", "w+")) as f:
            f.write("export IPFS_PATH=" + dir + "/data\n")
            f.write("./gpfs daemon --init" + "\n")
            f.write("./gpfs config Addresses.API /ip4/127.0.0.1/tcp/100"+ str(i) + "\n")
            f.write("./gpfs config Addresses.Gateway /ip4/127.0.0.1/tcp/200" +str(i) + "\n")
            f.write("./gpfs config Addresses.Swarm \'[\"/ip4/0.0.0.0/tcp/40"+str(i)+"\",\"/ip4/0.0.0.0/udp/50"+str(i)+"/quic\"]\' --json" +"\n")
            #f.write("./gpfs config Pubsub.Router floodsub" + "\n")
            f.write("./gpfs daemon --init --miner-address=" + bsc[i] + "\n")
        time.sleep(2)
        os.system("screen -dmS "+ bsc[i] +" bash -c \"sh "+dir+"/run.sh\"")
        print("screen -dmS "+ bsc[i] +" bash -c \"sh "+dir+"/run.sh\"")


if __name__ == '__main__':
    linux()