import json
import requests
import xlrd
from web3 import Web3
from eth_abi import encode_single, encode_abi


headers = {"Connection": "close", "Cache-Control": "max-age=0", "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"", "sec-ch-ua-mobile": "?0", "DNT": "1", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Sec-Fetch-Site": "none", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Accept-Encoding": "gzip, deflate", "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8"}

w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed1.binance.org'))
abi = json.loads('[{"constant": true,"inputs": [{"name": "who", "type": "address"}],"name": "balanceOf","outputs": [{"name": "", "type": "uint256"}],"payable": false,"stateMutability": "view","type": "function"}, {"inputs": [{"internalType": "uint256", "name": "cumulativePayout", "type": "uint256"},{"internalType": "bytes", "name": "issuerSig", "type": "bytes"}],"name": "cashCheque","outputs": [],"stateMutability": "nonpayable","type": "function"}]')
GPS_ADDRESS = w3.toChecksumAddress('0x5e772acf0f20b0315391021e0884cb1f1aa4545c')
GPS_CONTRACT = w3.eth.contract(address=GPS_ADDRESS, abi=abi)


#表格第一列放钱包地址，第二列放私钥
file_name = "62ABI.xlsx"

## 获取钱包地址
def get_addresses():
    xls = xlrd.open_workbook(file_name)
    addresses = xls.sheets()[0].col_values(0)
    private_secret = xls.sheets()[0].col_values(1)
    #print("一共有 " + str(len(addresses)) + " 地址")
    return addresses,private_secret

## 获取拥有的gps
def get_gps(address):
    address = Web3.toChecksumAddress(address)
    return GPS_CONTRACT.functions.balanceOf(address).call()

## 获取交易所需参数
def get_api(address,private_secret):
    private_secret = private_secret
    url = 'https://api.gpfs.xyz/v1/cheque?address=' + address
    res = requests.get(url, headers=headers)
    text = json.loads(res.text)
    amount = text['data']['amount']
    paid_out = text['data']['paid_out']
    signature = text['data']['signature']
    sedsendSigned(address,amount,signature,private_secret)


def get_count(address):
    nonce = w3.toHex(w3.eth.get_transaction_count(address))
    return nonce

def sedsendSigned(address,amount,signature,private_secret):
    amount_16 = w3.toInt(encode_single('uint256', amount))
    signature_16 = w3.toBytes(hexstr=signature)
    data = GPS_CONTRACT.encodeABI(fn_name="cashCheque", args=[amount_16,signature_16])
    rawTx = {
        'from': address,
        'to': GPS_ADDRESS,
        'value': w3.toHex(w3.toWei('0', 'ether')),
        'nonce': get_count(address),
        'gas': w3.toHex(100000),
        'gasPrice': w3.toHex(w3.toWei('5', 'gwei')),
        'data': data
    }
    signed_txn = w3.eth.account.sign_transaction(rawTx,private_secret)
    txn_hash = w3.toHex(w3.eth.send_raw_transaction(signed_txn.rawTransaction))
    print("地址:{0}\t交易hash:{1}".format(address,txn_hash))
    try:
        status = w3.eth.wait_for_transaction_receipt(txn_hash,timeout=20)['status']
        if status:
            print("交易成功")
    except:
        print("报错")


if __name__ == '__main__':
    key = get_addresses()
    for i in range(len(key[0])):
        address = key[0][i]
        private_secret = key[1][i]
        get_api(w3.toChecksumAddress(address),private_secret)