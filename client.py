from pybit.unified_trading import HTTP
from pybit._http_manager import FailedRequestError
import logging
from dotenv import load_dotenv
import os
import pandas as pd

logging.basicConfig(level=logging.INFO, filename='logs/logs.log', filemode='a', format='%(asctime)s, %(levelname)s, %(message)s', datefmt='%d-%m-%Y %H:%M:%S')

load_dotenv()

class Client:
    def __init__(self, symbol: str, interval: int = 5, amount_buy: float = 3.6) -> None:
        """symbol: 'SOLUSDT' for example
        interval: 1,5,10,15,30,60
        amount_buy: min. 3.6
        """
        self.symbol = symbol
        self.interval = interval
        self.amount_buy = amount_buy
        self.API_KEY = os.getenv("API_KEY")
        self.API_KEY_SECRET = os.getenv("API_KEY_SECRET")
        self.accountType = os.getenv("ACCOUNT_TYPE")
        self.client = HTTP(testnet = False, api_key=self.API_KEY, api_secret=self.API_KEY_SECRET)
    
    def get_balance(self):   
        try:
            coin_values: dict[str, dict[float]] = {}
            get_balance = self.client.get_wallet_balance(accountType=self.accountType)['result']['list'][0]['coin']
            for n in range(len(get_balance)):
                coin_values[get_balance[n].get('coin')] = (get_balance[n].get('walletBalance'))
            return coin_values
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"


    def place_buy_order(self) -> None | FailedRequestError:
        try:
            order = self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Buy',
                orderType='Market',
                qty=self.amount_buy,
            )
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def place_sell_order(self) -> FailedRequestError | None:
        try:
            self.amount = (self.get_balance()).get('SOL')
            order = self.client.place_order(
                category='spot',
                symbol=self.symbol,
                side='Sell',
                orderType='Market',
                qty=self.amount
            )
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_kline(self) -> dict | FailedRequestError:
        try:
            kline = self.client.get_kline(symbol=self.symbol, interval=self.interval)
            return kline
        except FailedRequestError as e:
            logging.error(e)
            return f"ErrorCode: {e.status_code}"

    def get_kline_dataframe(self) -> pd.DataFrame:
        dataframe = pd.DataFrame(self.get_kline()['result']['list'])
        dataframe.columns = ['time', 'open', 'high', 'low', 'close', 'volume', 'turnover']
        dataframe.set_index('time', inplace=True)
        dataframe.index = pd.to_numeric(dataframe.index, downcast='integer').astype('datetime64[ms]')    
        dataframe = dataframe[::-1]
        dataframe['close'] = pd.to_numeric(dataframe['close'])
        return dataframe

