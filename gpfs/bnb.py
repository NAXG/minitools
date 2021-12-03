import json
import requests
import xlrd
from web3 import Web3

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org'))

my_address = "xxxxx"#钱包地址
private_secret = "xxxx"#钱包私钥


file_name = "gps.xlsx"  #转账地址存储文件



## 获取钱包地址
def get_addresses():
    xls = xlrd.open_workbook(file_name)
    addresses = xls.sheets()[0].col_values(0)
    return addresses

# 获取钱包拥有bnb币
def blance(my_address):
    my_bnb = float(w3.fromWei(w3.eth.get_balance(my_address), 'ether'))
    print("钱包地址:{0} 拥有BNB币:{1}".format(my_address,my_bnb))
    return my_bnb


# 计算平均每个账号获得多少币，手续费多少
def branch_bnb(baoliu):
    bnb = blance(my_address)
    number = len(get_addresses())
    bnb = bnb - baoliu
    gas = number * 0.000105  
    bnb_number = bnb - gas
    bnb_number = bnb_number / number
    return bnb_number,gas


def get_count(my_address):
    nonce = w3.eth.get_transaction_count(my_address)
    return nonce

# 转账
def send_address(to_address,Value):
    rawTx = {
            "from" : my_address,
            "to" : to_address,
            "gasPrice" : w3.toHex(w3.toWei(5, "Gwei")),
            "gas" : w3.toHex(210000),
            "value" : w3.toHex(w3.toWei(Value, "ether")),
            "nonce" : get_count(my_address),
            }
    signed_txn = w3.eth.account.sign_transaction(rawTx,private_secret)
    txn_hash = w3.toHex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))
    print("地址:{0}\t交易hash:{1}".format(to_address,txn_hash))
    try:
        status = w3.eth.wait_for_transaction_receipt(txn_hash,timeout=20)['status']
        if status:
            print("交易成功")
    except:
        print("status报错")

if __name__ == '__main__':
    #默认保留 0.002 用于容错
    baoliu = 0.0002
    to_bnb = branch_bnb(baoliu)
    Value = to_bnb[0]
    gas = to_bnb[1]
    print("地址:{0} 保留:{1}用于容错".format(my_address,baoliu))
    print("每个账号约获得:{0}手续费约共{1}".format(Value,gas))
    #nonce = get_count(my_address)
    for to_address in get_addresses():
        send_address(w3.toChecksumAddress(to_address),Value)
        #nonce += 1