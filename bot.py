import json
import ta, time
from client import Client
from strategy import Grids
import logging
from notify import Notify, FakeNotify

class Bot:

    def __init__(self, *, symbol: str = 'BTCUSDT', 
                 interval: int = 5, 
                 amount_buy: float = 3.6, 
                 buy_crypto: bool = False, 
                 grids: int = 5,
                 send_notify: bool = False) -> None:
        """If buy_crypto = True, amount_buy will be calculated based not on USDT price. Not stable and not recommended to use!!!\n
        for sending notify u need to download pushbullet app on your mobile and visit their site https://docs.pushbullet.com/#send-sms"""
        print('trying to start...')
        self.symbol = symbol
        self.interval = interval
        self.amount_buy = amount_buy
        if buy_crypto:
            self.amount_buy = (float(Client(self.symbol).get_kline_dataframe().close.iloc[-1])*amount_buy)[:4]
        
        self.grids, self.grids_diff = Grids(interval=self.interval, 
                         symbol=self.symbol).set_grids(grids=grids)
        
        self.cli = Client(symbol=self.symbol, 
                           interval=self.interval,
                           amount_buy=self.amount_buy)
        if send_notify:
            self.notify = Notify()
        if not send_notify:
            self.notify = FakeNotify()
        


    def activate(self) -> None:
        """Buy - USDT, sell - SOL"""
        self.notify.bot_status(f'Bot started trading on pair {self.symbol}')
        print('bot was started')
        logging.info('bot was started')
        bot_status = True
        orders = []
        while bot_status:
                time.sleep(3)
                balance = self.cli.get_balance()
                price_now = float(self.cli.get_kline_dataframe().close.iloc[-1])
                df = self.cli.get_kline_dataframe()

                if orders == []:
                    if ta.momentum.rsi(df.close).iloc[-1] < 43:
                        if float(balance.get('USDT')) > self.amount_buy:
                            self.cli.place_buy_order()
                            orders.append(price_now)
                            logging.info(f'buy was succesfuly. Orders: {orders}')
                            logging.info(f'Next buy at {price_now - self.grids_diff} or sell at {price_now + self.grids_diff}') 
                            self.notify.trade_status(f'The bot bought at price {price_now}')
                        else:
                            print('Not enough money. Please, enter lower amount to buy')
                            

                if orders != []:
                    avg_buy = sum(orders) / len(orders)
                    if (price_now - avg_buy) > self.grids_diff:
                        self.cli.place_sell_order()
                        self.notify.trade_status(f'The bot sold at price {price_now}')
                        logging.info('closing positions')
                        orders = []

                    if ta.momentum.rsi(df.close).iloc[-1] < 43 and \
                        (orders[-1] - price_now) > self.grids_diff and \
                            float(balance.get('USDT')) < self.amount_buy:
                        time.sleep(5)
                        self.notify.balance_status('Not enough balance for buy! Waiting to sell')
                        print('waiting to sell')

                    if ta.momentum.rsi(df.close).iloc[-1] < 43 and \
                        (orders[-1] - price_now) > self.grids_diff and \
                            float(balance.get('USDT')) > self.amount_buy:
                        self.cli.place_buy_order()
                        self.notify.trade_status(f'The bot bought again at price {price_now}')
                        logging.debug(f'rsi lower than 45 and placing order again at {price_now}')
                        orders.append(price_now)
                        print('buy again')

with open('src/bot_config.json', 'r') as f:
    config = json.load(f)


bot = Bot(symbol=config.get('symbol'), 
          interval=config.get('interval'), 
          amount_buy=config.get('amountBuy'),
          buy_crypto=config.get('buy_crypto'),
          grids=config.get('grids'),
          send_notify=config.get('send_notify'))
