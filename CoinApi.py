import json, requests, datetime
from Utils import *
ACCOUNT_ID = 0
class CoinbaseExchange(CoinbaseExchangeAuth):
    #Class used to perform different actions on the GDAX API
    def __init__(self, symbol,access_key, secret_key, market_url, trade_url):
        super(CoinbaseExchange,self).__init__(access_key, secret_key, market_url, trade_url)
        self.symbol = symbol

    def get_kline(self,period, size=150):
        """
        :param symbol
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param size: 可选值： [1,2000]
        :return:
        """
        params = {'symbol': self.symbol,
                  'period': period,
                  'size': size}

        url = self.market_url + '/market/history/kline'
        return self.http_get_request(url, params)

    def get_accounts(self):
        """
        :return:
        """
        path = "/v1/account/accounts"
        params = {}
        return self.api_key_get(params, path)

    def send_order(self,amount, source, _type, price=0):
        """
        :param amount:
        :param source: 如果使用借贷资产交易，请在下单接口,请求参数source中填写'margin-api'
        :param symbol:
        :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price:
        :return:
        """
        try:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']
        except BaseException as e:
            print('get acct_id error.%s' % e)
            acct_id = ACCOUNT_ID

        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": self.symbol,
                  "type": _type,
                  "source": source}
        if price:
            params["price"] = price

        url = '/v1/order/orders/place'
        return self.api_key_post(params, url)

    def get_balance(self,acct_id=None):
        """
        :param acct_id
        :return:
        """
        global ACCOUNT_ID

        if not acct_id:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']

        url = "/v1/account/accounts/{0}/balance".format(acct_id)
        params = {"account-id": acct_id}
        return self.api_key_get(params, url)

    def get_timestamp(self):
        url = self.market_url + '/v1/common/timestamp'
        return self.zwl(url)
