import pandas as pd
import numpy as np
from Functions import *
import os

class Model:
    def __init__(self,csv_price,csv_transactions):
        self.transaction_dataframe = pd.DataFrame(data={'huobi_id' : [], 'product_id' : [], 'datetime': [], 'buy/sell': [], 'price': [], 'quantity': [], 'status': [], 'fiat_balance' : []})
        self.ma_dataframe = pd.DataFrame(data={'datetime': [],'price': [], 'MA5': [], 'MA20': [], 'RSI': [], 'signal': []})
        self.transaction_fee_ratio= 0.0002 #交易费用比率
        self.profit_ratio_threshold = 0.2 #最少赚钱比率
        self.ma1 = 5
        self.ma2 = 20
        self.csv_price = csv_price
        self.csv_transactions = csv_transactions
        self.buy_flag = 0
        csv_price_exists = os.path.isfile(self.csv_price)
        csv_transactions_exists = os.path.isfile(self.csv_transactions)
        if not csv_price_exists:
            self.logPrice(False)
        if not csv_transactions_exists:
            self.logTransactions(False)

    def calculateMA(self,CoinBase):
        kline = CoinBase.get_kline('1min', size=1)
        price = kline['data'][0]['close']
        timestamp = CoinBase.get_timestamp()
        datetime = getTime(timestamp['data'])
        self.ma_dataframe = self.ma_dataframe.append(pd.DataFrame({'datetime': datetime, 'price': price,'MA5':np.nan, 'MA20':np.nan }, index=[0]),ignore_index=True)
        length = self.ma_dataframe.shape[0]
        print("length:", length)
        if length > self.ma1:
            #指数均值
            #self.ma_dataframe['MA5'] = self.ma_dataframe['price'].dropna().shift().fillna(self.ma_dataframe['MA5']).ewm(com=self.ma1).mean()
            #普通均值
            #self.ma_dataframe['MA5'] =self.ma_dataframe['price'].fillna(self.ma_dataframe['MA5']).rolling(self.ma1).mean()
            self.ma_dataframe.ix[length - 1, 'MA5'] = self.ma_dataframe['price'].tail(self.ma1).mean()
        if length > self.ma2:
            # 指数均值
            #self.ema_dataframe['MA20'] = self.ema_dataframe['price'].dropna().shift().fillna(self.ema_dataframe['MA20']).ewm(com=self.ma2).mean()
            #普通均值
            #self.ma_dataframe['MA20'] = self.ma_dataframe['price'].fillna(self.ma_dataframe['MA20']).rolling(self.ma2).mean()
            self.ma_dataframe.ix[length - 1, 'MA20'] = self.ma_dataframe['price'].tail(self.ma2).mean()

    def calculateCrossover(self,CoinBase):
        #Calculate MA crossover and return signal
        length = self.ma_dataframe.shape[0]

        if length>self.ma1:
            # 取出tail的两个数据，也就是最新的数据
            MA5 = self.ma_dataframe['MA5'].tail(2).reset_index(drop=True)
            MA20 = self.ma_dataframe['MA20'].tail(2).reset_index(drop=True)

            # 价格上轨
            upper = MA20[1] + MA20[1] * self.profit_ratio_threshold
            # 价格下轨
            lower = MA20[1] - MA20[1] * self.profit_ratio_threshold

            #获得当前价格和数量
            account = CoinBase.get_balance()
            for line in account['data']['list']:
                if line['currency'] == 'btc' and line['type'] == 'trade':
                    cur_quantity = float(line['balance'])  # 获得当前币的数量
                    break
            kline = CoinBase.get_kline('1min', size=1)
            cur_price = kline['data'][0]['close']

            #if last_transaction['buy/sell'] == 'buy':#如果上次买入，这次赚钱的话就卖
            if self.buy_flag == 1:
                # 获得上次交易信息
                last_transaction = self.transaction_dataframe.tail(1)
                profit = cur_price * cur_quantity * (1 - self.transaction_fee_ratio) - last_transaction['price'] * last_transaction['quantity']
                expect_profit = last_transaction['price'] * last_transaction['quantity'] * self.profit_ratio_threshold
                if (MA5[1] <= MA20[1]) & (MA5[0] >= MA20[0]) & (profit.item() > expect_profit.item()):
                    signal = {'signal': True, 'value': 'sell'}
                    self.buy_flag = 0
                else:
                    signal = {'signal': False, 'value': None}
            #elif last_transaction['buy/sell'] == 'sell':#如果上次是卖出，要决定这次是否买入,是不是要预期一下这次如果买入的话走势或者收益？？todo
            elif self.buy_flag==0 :
                if (MA5[1] >= MA20[1]) & (MA5[0] <= MA20[0]):
                    signal = {'signal': True, 'value': 'buy'}
                    self.buy_flag = 1
                else:
                    signal = {'signal': False, 'value': None}

            self.ma_dataframe.loc[self.ma_dataframe.index[length-1], 'signal'] = signal['value']
            self.logPrice(True)
            print(self.ma_dataframe.tail(1))
            return signal
        else:
            self.logPrice(True)
            print(self.ma_dataframe.tail(1))

    def calculateRSI(self, period):
        #Calculate RSI and add to dataframe
        length = self.ma_dataframe.shape[0]
        if length>period:
            delta = self.ma_dataframe['price'].dropna().apply(float).diff()
            dUp, dDown = delta.copy(), delta.copy()
            dUp[dUp < 0] = 0
            dDown[dDown > 0] = 0
            RollUp = dUp.rolling(window=period).mean()
            RollDown = dDown.rolling(window=period).mean().abs()
            RS = RollUp / RollDown
            RSI = 100.0 - (100.0 / (1.0 + RS))
            self.ma_dataframe['RSI'] = RSI


    def logPrice(self, append):
        #Log price to CSV
        if (append):
            columns = ['datetime','price', 'MA5', 'MA20', 'RSI', 'signal']
            self.ma_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', mode='a',sep=',', index=False, header=False, columns=columns)
        else:
            self.ma_dataframe.tail(1).to_csv(self.csv_price, encoding='utf-8', sep=',',index=False, header=True)
    def logTransactions(self, append):
        #Log transactions to CSV
        if (append):
            columns = ['huobi_id' , 'product_id' , 'datetime', 'buy/sell', 'price', 'quantity', 'status', 'fiat_balance' ]
            self.transaction_dataframe.tail(1).to_csv(self.csv_transactions, encoding='utf-8', mode='a',sep=',', index=False, header=False,  columns= columns)
        else:
            self.transaction_dataframe.tail(1).to_csv(self.csv_transactions, encoding='utf-8', sep=',',index=False, header=True)




