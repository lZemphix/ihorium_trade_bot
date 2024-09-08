import json
import ta, time
from client import Client
from strategy import Grids

class Bot:

    def __init__(self, *, symbol: str, interval: int, amount_buy: float = 3.6, grids: int = 5) -> None:
        self.symbol = symbol
        self.interval = interval
        self.amount_buy = amount_buy
        self.grids, self.grids_diff = Grids(interval=self.interval, 
                         symbol=self.symbol).set_grids(grids=grids)
        
        
        self.cli = Client(symbol=self.symbol, 
                           interval=self.interval,
                           amount_buy=self.amount_buy)

    def activate(self) -> None:
        """Buy - USDT, sell - SOL"""
        print('bot was started')
        bot_status = True
        balance = self.cli.get_balance()
        price_now = self.cli.get_kline_dataframe().close.iloc[-1]
        orders = []
        while bot_status:
                df = self.cli.get_kline_dataframe()
                if orders == []:
                    if ta.momentum.rsi(df.close).iloc[-1] < 45 :
                        if balance.get('USDT') > str(self.amount_buy):
                            self.cli.place_buy_order()
                            orders.append(price_now)
                            print('buy')

                if orders != []:
                    avg_buy = sum(orders) / len(orders)

                    if ta.momentum.rsi(df.close).iloc[-1] < 45 and \
                        (orders[-1] - price_now) > self.grids_diff and \
                            balance.get('USDT') > self.amount_buy:
                        self.cli.place_buy_order()
                        orders.append(price_now)
                        print('buy')

                    if balance.get('USDT') < self.amount_buy:
                        time.sleep(60)
                        print('waiting to sell')
                        
                    if ta.momentum.rsi(df.close).iloc[-1] > 60 and \
                        (price_now - avg_buy) > self.grids_diff:
                        self.cli.place_sell_order()
                        print('sell')
                        orders = []

with open('src/bot_config.json', 'r') as f:
    config = json.load(f)

bot = Bot(symbol=config.get('symbol'), 
          interval=config.get('interval'), 
          amount_buy=config.get('amountBuy'),
          grids=config.get('grids'))
