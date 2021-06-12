import requests
import json
import xlrd
from apscheduler.schedulers.blocking import BlockingScheduler


file_name = "gps.xlsx"

def init_address():
    xls = xlrd.open_workbook(file_name)
    addresses = xls.sheets()[0].col_values(0)
    print("一共有 " + str(len(addresses)) + " 地址")
    return addresses

def main(money):
	burp0_url = "https://api.gpfs.xyz:443/v1/miners?page=1&limit=20&address=" + money
	burp0_headers = {"Connection": "close", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "Accept": "application/json, text/javascript, */*; q=0.01", "DNT": "1", "sec-ch-ua-mobile": "?0", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36", "Origin": "https://scan.gpfs.xyz", "Sec-Fetch-Site": "same-site", "Sec-Fetch-Mode": "cors", "Sec-Fetch-Dest": "empty", "Referer": "https://scan.gpfs.xyz/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"}
	try:
		r=requests.get(burp0_url, headers=burp0_headers,timeout=20)
		data = r.json()
		test=data['data']['miners']
	except:
		print("访问超时,跳过1")

	try:
		print("###钱包地址【"+test[0]['address']+"】累计出票【"+test[0]['reward']+"】已兑换【"+test[0]['paid_out']+"】算力【"+test[0]['balance']+"】状态【"+test[0]['state']+"】###")
	except:
		print("访问超时,跳过2")

	return(test[0]['reward'],test[0]['paid_out'],test[0]['balance'],test[0]['state'])



def dingding(reward_sum, paid_out_sum, balance_sum,state_True,state_False):
    baseUrl = "https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxxxxxxxxxxx"
    HEADERS = {
            "Content-Type": "application/json ;charset=utf-8 "
        }
    message = "总出票:{0}\n已兑换{1}\n总算力{2}\n在线数:{3}\n离线数:{4}".format(reward_sum,paid_out_sum,balance_sum,state_True,state_False)
    stringBody ={
        "msgtype": "text",
        "text": {"content": message},
        "at": {
        #"atMobiles": ["130xxxxxxx0"],
        }
     }
    MessageBody = json.dumps(stringBody)
    result = requests.post(url=baseUrl, data=MessageBody, headers=HEADERS)
    print(result.text)

def sc():
	reward_sum = 0
	paid_out_sum= 0
	balance_sum = 0
	state_True = 0
	state_False = 0
	for i in init_address():
		ALL = main(i)
		reward_sum += float(ALL[0])
		paid_out_sum += float(ALL[1])
		balance_sum += float(ALL[2])
		if ALL[3] == u'在线':
			state_True += 1
		else:
			state_False += 1
	dingding(reward_sum,paid_out_sum,balance_sum,state_True,state_False)

if __name__ == '__main__':
    scheduler = BlockingScheduler()
    scheduler.add_job(sc, 'interval', minutes=30)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass