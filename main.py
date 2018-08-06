import time
from TimeThread import *
#Custom settings
LOOP_DURATION = 1# Time period (in seconds)
MAX_LOOP_TIME = 10 * 60 * 60 # Max duration to run (in seconds)
SYMBOL="btcusdt"
# KeY
ACCESS_KEY = "204e335a-3208ae52-75d34260-1068a"
SECRET_KEY = "51e0753d-23e60931-1f60f52c-4fa9b"
# API 请求地址
MARKET_URL = "https://api.hadax.com"
TRADE_URL = "https://api.hadax.com"
CSV_PRICE = "./price.csv" # Price CSV name
CSV_TRANSACTIONS = "./transactions.csv" # Transaction CSV name
#Start thread
os.environ['HTTP_PROXY'] = 'http://web-proxy.tencent.com:8080'
os.environ['HTTPS_PROXY'] = 'http://web-proxy.tencent.com:8080'
stopFlag = Event()
thread = TimedThread(stopFlag, LOOP_DURATION,SYMBOL,ACCESS_KEY,SECRET_KEY,MARKET_URL,TRADE_URL, CSV_PRICE, CSV_TRANSACTIONS)
thread.daemon = True
thread.start()
#Set max time to run
time.sleep(MAX_LOOP_TIME)
stopFlag.set()