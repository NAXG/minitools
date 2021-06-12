import requests
import json
import xlrd
import pandas as pd
import time 
from apscheduler.schedulers.blocking import BlockingScheduler

file_name = "gps.xlsx"


def init_address():
    xls = xlrd.open_workbook(file_name)
    addresses = xls.sheets()[0].col_values(0)
    print("一共有 " + str(len(addresses)) + " 地址")
    return addresses


def main():
    burp0_url = "https://api.gpfs.xyz:443/v1/rewards?page=1&limit=50"
    burp0_headers = {"Connection": "close", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "Accept": "application/json, text/javascript, */*; q=0.01", "DNT": "1", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36", "Origin": "https://scan.gpfs.xyz", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://scan.gpfs.xyz/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"}
    res = requests.get(burp0_url, headers=burp0_headers)
    res_json = res.json()
    datas = res_json["data"]["rewards"]
    df = pd.DataFrame(datas)
    df1 = df[["address","amount","created_at"]]
    for i in init_address():
        df2 = df1[df1["address"].str.contains(i)]
        df2 = df2.reset_index(drop=True)
        if not df2.empty:
            print("{0}\t{1}\t{2}".format(str(df2.at[0,"address"]),str(df2.at[0,"amount"]),str(df2.at[0,"created_at"])))
            dingding(str(df2.at[0,"address"]),str(df2.at[0,"amount"]),str(df2.at[0,"created_at"]))



def dingding(address, amount, created_at):
    baseUrl = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxx"
    HEADERS = {
            "Content-Type": "application/json ;charset=utf-8 "
        }

    timeStamp = int(created_at)
    timeArray = time.localtime(timeStamp)
    otherStyleTime = time.strftime("%Y--%m--%d %H:%M:%S", timeArray)
    message = "地址:【{0}】\n爆块:【{1}】\n时间:【{2}】".format(address,amount,otherStyleTime)
    stringBody ={
        "msgtype": "text",
        "text": {"content": message},
        "at": {
        #"atMobiles": ["130xxxxxxxxxx0"],
        }
     }
    MessageBody = json.dumps(stringBody)
    result = requests.post(url=baseUrl, data=MessageBody, headers=HEADERS)
    print(result.text)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(main, 'interval', minutes=10)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass