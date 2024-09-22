import json
import ta, time

import ta.momentum
from client import Account, Market, Graph
import logging
from modules.telenotify import SendNotify
from modules.orders_config import OrdersEdit
from modules.notify_settings import NotifySettings

class Bot:

    def __init__(self) -> None:
        print('trying to start...')
        self.symbol = self.get_config().get('symbol')
        self.interval = self.get_config().get('interval')
        self.amount_buy = self.get_config().get('amountBuy')
        self.stepBuy = self.get_config().get('stepBuy')
        self.stepSell = self.get_config().get('stepSell')
        self.send_notify = self.get_config().get('send_notify')
        self.RSI = self.get_config().get('RSI')
        
        self.orders = OrdersEdit()
        self.account = Account()
        self.market = Market()
        self.graph = Graph()
        self.notify_send = NotifySettings(True, True, True) #for clean code (if u need, u can use it)

        self.notify = SendNotify(True) if self.send_notify else SendNotify(False)
        self.sell_position = False
        self.bot_status = True
        self.notify_status = False
        self.smart_trade = self.get_config().get('smartTrade')
        
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
        df_4h = self.graph.get_kline_dataframe_4h()
        balance = self.account.get_balance()

        if ta.momentum.rsi(df.close).iloc[-1] < self.RSI and \
            float(balance.get('USDT')) > self.amount_buy and \
                ((ta.momentum.rsi(df_4h.close).iloc[-1] <= 55) if self.smart_trade else True):
                price_now = self.market.get_actual_price()

                self.market.place_buy_order()
                time.sleep(3)
                last_order = self.orders.get_last_order()
                self.orders.add(last_order)

                sell_price = self.orders.avg_order() + self.stepSell
                self.market.place_sell_order(sell_price)
                self.sell_position = True

                print(f'first_buy {price_now}')
                logging.info(f'Next buy at {price_now - self.stepBuy} or sell at {price_now + self.stepBuy}') 
                self.notify.bought(f'The bot bought at price {price_now}')

    def averaging(self) -> None:
        df = self.graph.get_kline_dataframe()
        df_4h = self.graph.get_kline_dataframe_4h()

        if ta.momentum.rsi(df.close).iloc[-1] < self.RSI:
            if (self.orders.get_last_order()- price_now) > self.stepBuy and\
                ((ta.momentum.rsi(df_4h.close).iloc[-1] <= 55) if self.smart_trade else True):
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

                sell_price = self.orders.avg_order() + self.stepSell
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
                
                # умная тоговля
                

                #Первая покупка
                if self.orders.get() is not None and self.orders.qty() == 0:
                    self.first_buy()
       
                #Усреднение
                if self.orders.qty() != 0 and float(balance.get('USDT')) > self.amount_buy:                    
                    self.averaging()

                if self.orders.qty() != 0 and float(balance.get('USDT')) < self.amount_buy:
                    if self.notify_status == False:
                            self.not_enough_money_notify()
    


config = Bot.get_config()

bot = Bot(symbol=config.get('symbol'), 
          interval=config.get('interval'), 
          amount_buy=config.get('amountBuy'),
          stepBuy=config.get('step'),
          send_notify=config.get('send_notify'))

if __name__ == '__main__':
    try:
        pass
    except Exception as e:
        print(e)