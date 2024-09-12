import json
import ta, time
from client import Client
import logging
from modules.notify import Notify, FakeNotify
from modules.orders_config import OrdersEdit

class Bot:

    def __init__(self, *, symbol: str = 'SOLUSDT', 
                 interval: int = 5, 
                 amount_buy: float = 3.6, 
                 buy_crypto: bool = False, 
                 step: float = 0.5,
                 send_notify: bool = False) -> None:
        """If buy_crypto = True, amount_buy will be calculated based on SOL amount. Not stable and not recommended to use!!!\n
        for sending notify u need to download pushbullet app on your mobile and visit their site https://docs.pushbullet.com/#send-sms"""
        print('trying to start...')
        self.symbol = symbol
        self.interval = interval
        self.amount_buy = amount_buy
        self.step = step
        
        self.orders = OrdersEdit()
        self.cli = Client(symbol=self.symbol, interval=self.interval, amount_buy=self.amount_buy)

        self.amount_buy = (float(Client(self.symbol).get_kline_dataframe().close.iloc[-1])*amount_buy)[:4] if buy_crypto else amount_buy
        self.notify = Notify() if send_notify else FakeNotify()
        self.bot_status = True
        self.notify_status = False
        


    def start(self) -> None:
        """Buy - USDT, sell - SOL"""
        self.notify.bot_status(f'Bot started trading on pair {self.symbol}')
        print('bot was started')
        logging.info('bot was started')
        
        while self.bot_status:
                time.sleep(1)
                balance = self.cli.get_balance()
                price_now = self.cli.get_actual_price('spot')
                df = self.cli.get_kline_dataframe()
                
                
                #Первая покупка
                if self.orders.qty() == 0:
                    self.first_buy(self.orders.get(), price_now, balance, df)
       
                #Последующие действия
                if self.orders.qty() != 0 and float(balance.get('USDT')) > self.amount_buy:
                    avg_buy = round(self.orders.avg_order(),2)
                    if (price_now - avg_buy) > self.step:
                        self.close_position(price_now)
                        
                    #усреднениe
                    if ta.momentum.rsi(df.close).iloc[-1] < 43:
                        if (self.orders.get_last_order()- price_now) > self.step:
                            self.averaging(price_now)

                elif self.orders.qty() != 0 and float(balance.get('USDT')) < self.amount_buy:
                    if self.notify_status == False:
                            self.not_enough_money_notify()

    def not_enough_money_notify(self):
        self.notify.balance_status('Not enough money!')
        print('Not enough money!')
        self.notify_status = True

    def averaging(self, price_now: float):
        self.cli.place_buy_order()
        print(f'averating {price_now}')
        self.notify.trade_status(f'The bot bought again at price ~{price_now}')
        logging.debug(f'Buy again at {price_now}')
        self.orders.add(self.orders.get_last_order())
        self.notify_status = False


    def close_position(self, price_now: float) -> tuple[int, bool]:
        self.cli.place_sell_order()
        print(f'close positions {price_now}')
        self.notify.trade_status(f'The bot sold at price ~{price_now}')
        logging.info(f'closing positions for {price_now}')
        self.orders.clear()
        self.notify_status = False

    def first_buy(self, orders_list: list, price_now: float, balance: str, df: str) -> int:
        if ta.momentum.rsi(df.close).iloc[-1] < 43 and \
            float(balance.get('USDT')) > self.amount_buy:
                self.cli.place_buy_order()
                print(f'first_buy {price_now}')
                logging.info(f'buy was succesfuly. Orders: {orders_list}')
                logging.info(f'Next buy at {price_now - self.step} or sell at {price_now + self.step}') 
                self.notify.trade_status(f'The bot bought at price {price_now}')
                self.orders.add(self.orders.get_last_order())

    

with open('config/bot_config.json', 'r') as f:
    config = json.load(f)


bot = Bot(symbol=config.get('symbol'), 
          interval=config.get('interval'), 
          amount_buy=config.get('amountBuy'),
          buy_crypto=config.get('buy_crypto'),
          step=config.get('step'),
          send_notify=config.get('send_notify'))

if __name__ == '__main__':
    try:
        print(OrdersEdit().get_last_order())
    except Exception as e:
        print(e)