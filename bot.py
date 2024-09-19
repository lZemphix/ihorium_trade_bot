import json
import ta, time
from client import Account, Market, Graph
import logging
from modules.telenotify import SendNotify
from modules.orders_config import OrdersEdit
from modules.notify_settings import NotifySettings

class Bot:

    def __init__(self, *, symbol: str = 'SOLUSDT', 
                 interval: int = 5, 
                 amount_buy: float = 3.6, 
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
        self.account = Account()
        self.market = Market()
        self.graph = Graph()
        self.notify_send = NotifySettings(True, True, True) #for clean code (if u need, u can use it)

        self.notify = SendNotify(True) if send_notify else SendNotify(False)
        self.sell_position = False
        self.bot_status = True
        self.notify_status = False
        
    @staticmethod
    def get_config() -> dict:
        with open('config/bot_config.json', 'r') as f:
            return json.load(f)
         

    def not_enough_money_notify(self) -> None:
        #Ready
        self.notify.warning('Not enough money!')
        print('Not enough money!')
        self.notify_status = True

    def first_buy(self) -> int:
        #Ready
        df = self.graph.get_kline_dataframe()
        balance = self.account.get_balance()

        if ta.momentum.rsi(df.close).iloc[-1] < 41 and \
            float(balance.get('USDT')) > self.amount_buy:
                price_now = self.market.get_actual_price()

                self.market.place_buy_order()
                time.sleep(3)
                last_order = self.orders.get_last_order()
                self.orders.add(last_order)

                sell_price = self.orders.avg_order() + self.step
                self.market.place_sell_order(sell_price)
                self.sell_position = True

                print(f'first_buy {price_now}')
                logging.info(f'Next buy at {price_now - self.step} or sell at {price_now + self.step}') 
                self.notify.bought(f'The bot bought at price {price_now}')

    def averaging(self) -> None:
        #Ready (need to be tested)
        price_now = self.market.get_actual_price()
        self.market.place_buy_order()
        time.sleep(3)

        self.orders.add(self.orders.get_last_order())
        print(f'averating {price_now}')
        self.notify.bought(f'The bot bought again at price ~{price_now}')
        logging.info(f'Buy again at {price_now}')
        self.notify_status = False

        self.market.cancel_order()

        sell_price = self.orders.avg_order() + self.step
        self.market.place_sell_order(sell_price)
        self.sell_position = True



    def start(self) -> None:
        """Buy - USDT, sell - SOL"""
        self.notify.bot_status(f'Bot started trading on pair {self.symbol}')
        print('bot was started')
        logging.info('bot was started')
        
        while self.bot_status:
                time.sleep(1)
                self.sell_position = self.orders.get_open_orders()

                if self.sell_position == False:
                    self.orders.clear()

                balance = self.account.get_balance()
                price_now = self.market.get_actual_price()
                df = self.graph.get_kline_dataframe()
                
                
                #Первая покупка
                if self.orders.get() is not None and self.orders.qty() == 0:
                    self.first_buy()
       
                #Последующие действия
                if self.orders.qty() != 0 and float(balance.get('USDT')) > self.amount_buy:                    
                        
                    #усреднениe
                    if ta.momentum.rsi(df.close).iloc[-1] < 41:
                        if (self.orders.get_last_order()- price_now) > self.step:
                            self.averaging()

                if self.orders.qty() != 0 and float(balance.get('USDT')) < self.amount_buy:
                    if self.notify_status == False:
                            self.not_enough_money_notify()
    


config = Bot.get_config()

bot = Bot(symbol=config.get('symbol'), 
          interval=config.get('interval'), 
          amount_buy=config.get('amountBuy'),
          step=config.get('step'),
          send_notify=config.get('send_notify'))

if __name__ == '__main__':
    try:
        pass
    except Exception as e:
        print(e)