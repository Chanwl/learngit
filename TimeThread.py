import time
from threading import Event, Thread
from CoinApi import *
from MaModel import *
from Functions import *
class TimedThread(Thread):
    def __init__(self, event, wait_time, symbol,access_key,secret_key,market_url,trade_url, csv_price, csv_transactions):
        Thread.__init__(self)
        self.stopped = event
        self.wait_time = wait_time
        self.symbol=symbol
        self.access_key=access_key
        self.secret_key=secret_key
        self.market_url=market_url
        self.trade_url=trade_url
        #API
        self.CoinBase = CoinbaseExchange(self.symbol,self.access_key, self.secret_key, self.market_url, self.trade_url)
	    #Create model
        self.model = Model(csv_price, csv_transactions)
        self.balance = 14.6394
        self.quantity = 0
        print('Running...')

    def run(self):
        print("Hello")
    	#Run thread until stopped by 'stopFlag' Event, waiting at set intervals
        while not self.stopped.wait(self.wait_time):
        	self.EMACrossover()


    def order(self, type):
        accounts = self.CoinBase.get_accounts()
        acct_id = accounts['data'][0]['id']
        kline = self.CoinBase.get_kline('1min', size=1)
        account=self.CoinBase.get_balance()
        timestamp=self.CoinBase.get_timestamp()
        datetime = getTime(timestamp['data']) # 获得时间，换成自己的api
        buy_price = float(kline['data'][0]['close'])#获得当前价格，换成自己api
        # balance=0
        # for line in account['data']['list']:
        #     if line['currency'] == 'usdt' and line['type'] == 'trade':
        #         balance = float(line['balance'])#获得当前balance，换成自己api
        #         break
        # cur_quantity=0
        # for line in account['data']['list']:
        #     if line['currency'] == 'btc' and line['type'] == 'trade':
        #         cur_quantity = float(line['balance'])  # 获得当前币的数量
        #         break
        # quantity = (balance * (1 - self.model.transaction_fee_ratio)) / buy_price
        # order = CoinBase.buy(product_id, quantity, buy_price) #换成自己api
        if (type == 'sell'):
            print('sell')
            self.balance = self.quantity * buy_price * (1 - self.model.transaction_fee_ratio)
            self.quantity = 0
            print('buy: ', self.quantity)
            print('balance: ', self.balance)
            self.model.transaction_dataframe.loc[self.model.transaction_dataframe.shape[0]] = [id, acct_id, datetime,
                                                                                               'sellUpper', buy_price,
                                                                                               self.quantity, 1,
                                                                                               self.balance]
            # order=self.CoinBase.send_order(cur_quantity,'api','sell-market')
        else:
            self.quantity = (self.balance * (1 - self.model.transaction_fee_ratio)) / buy_price
            self.balance = 0
            print('buy: ', self.quantity)
            print('balance: ',self.balance)
            self.model.transaction_dataframe.loc[self.model.transaction_dataframe.shape[0]] = [id, acct_id, datetime,
                                                                                               'buy', buy_price,
                                                                                               self.quantity, 1,
                                                                                               self.balance]
        #print(self.model.transaction_dataframe)
            # order=self.CoinBase.send_order(balance,'api','buy-market')

        # if order is not None:
        #     id=order['data']
        #     status=order['status']
        #     account = self.CoinBase.get_balance()
        #     for line in account['data']['list']:
        #         if line['currency'] == 'usdt' and line['type'] == 'trade':
        #             balance = float(line['balance'])#获得当前balance，换成自己api
        #             break
        #     if (type == 'sell'):
        #         self.model.transaction_dataframe.loc[self.model.transaction_dataframe.shape[0]] = [id, acct_id, datetime,'sellUpper', buy_price,quantity, status, balance]
        #         self.model.buy_flag = 0
        #     elif(type == 'buy'):
        #         self.model.transaction_dataframe.loc[self.model.transaction_dataframe.shape[0]] = [id, acct_id, datetime,'buy', buy_price,quantity, status,balance]
        #         self.model.buy_flag = 1
        #     self.model.logTransactions(True)
        #     return order
        # else:
        #     return


    def EMACrossover(self):
        print("EMA is run")
        self.model.calculateMA(self.CoinBase)
        self.model.calculateRSI(14)
        signal = self.model.calculateCrossover(self.CoinBase)
        if signal is not None:
            if signal['value'] == 'buy':
                self.order('buy')
            elif signal['value'] == 'sell':
                self.order('sell')
