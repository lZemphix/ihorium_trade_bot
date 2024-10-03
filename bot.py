from datetime import datetime
import json
import ta, time
from modules.laps_config import laps
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
        self.smart_trade = self.get_config().get('smartTrade')
        
        self.orders = OrdersEdit()
        self.account = Account()
        self.market = Market()
        self.graph = Graph()
        self.laps = laps
        self.notify = SendNotify(True) if self.send_notify else SendNotify(False)

        self.sell_position = False
        self.bot_status = True
        self.nem_notify_status = False
        self.sell_notify_status = True
        
    @staticmethod
    def get_config() -> dict:
        with open('config/bot_config.json', 'r') as f:
            return json.load(f)

    def not_enough_money_notify(self) -> None:
        #Ready
        self.notify.warning('Not enough money!')
        print('Not enough money!')
        self.nem_notify_status = True
    
    def sell_notify(self) -> None:
        if not self.orders.get_open_orders() and self.sell_notify_status == True:
            try:
                close_price = self.orders.avg_order() + self.stepSell
                self.notify.sold(f'Bot close the position at {close_price}')
            except ZeroDivisionError:
                self.notify.sold('bot close the position')

            self.sell_notify_status = False
            self.laps.add(self.laps.calculate_profit())

    def first_buy(self) -> int:
        #Ready
        df = self.graph.get_kline_dataframe()
        df_4h = self.graph.get_kline_dataframe_4h()
        balance = self.account.get_balance()
        price_now = self.market.get_actual_price()

        if ta.momentum.rsi(df.close).iloc[-1] < self.RSI and \
            float(balance.get('USDT')) > self.amount_buy and \
                ((ta.momentum.rsi(df_4h.close).iloc[-1] <= 55) if self.smart_trade else True):

                self.market.place_buy_order()
                time.sleep(3)
                last_order = self.orders.get_last_order()
                self.orders.add(last_order)

                sell_price = self.orders.avg_order() + self.stepSell
                self.market.place_sell_order(sell_price)
                self.sell_position = True
                self.sell_notify_status = True

                print(f'first_buy {price_now}')
                logging.info(f'Next buy at {price_now - self.stepBuy} or sell at {price_now + self.stepBuy}') 
                self.notify.bought(f'The bot bought at price {price_now}')

    def averaging(self) -> None:
        df = self.graph.get_kline_dataframe()
        df_4h = self.graph.get_kline_dataframe_4h()
        price_now = self.market.get_actual_price()

        if ta.momentum.rsi(df.close).iloc[-1] < self.RSI:
            if (self.orders.get_last_order()- price_now) > self.stepBuy and\
                ((ta.momentum.rsi(df_4h.close).iloc[-1] <= 55) if self.smart_trade else True):
                #Ready (need to be tested)
                self.market.place_buy_order()
                time.sleep(3)

                self.orders.add(self.orders.get_last_order())
                print(f'averating {price_now}')
                self.notify.bought(f'The bot bought again at price ~{price_now}')
                logging.info(f'Buy again at {price_now}')
                self.nem_notify_status = False

                self.market.cancel_order()

                sell_price = self.orders.avg_order() + self.stepSell
                self.market.place_sell_order(sell_price)
                self.sell_position = True
                self.sell_notify_status = True

    def add_profit(self):
        
        with open('config/profit.json', 'r') as f:
            try:
                config = json.load(f)
                last_date = datetime.strptime(config.get('SOLUSDT')[-1].get('date'), '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - last_date).total_seconds() > 86400:
                    get_balance = self.account.get_balance()
                    balance_usdt =float( get_balance.get('USDT'))
                    balance_sol = float(get_balance.get('SOL')) * self.market.get_actual_price()
                    balance = round(balance_sol + balance_usdt, 2)
                    new_day = {
                        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'balance': balance,
                        'laps': self.laps.qty(),
                        'profit': round(balance - config.get('SOLUSDT')[-1].get('balance'), 2)
                    }
                    config.get('SOLUSDT').append(new_day)
                    with open('config/profit.json', 'w') as f:
                        json.dump(config, f, indent=4)
            except:
                get_balance = self.account.get_balance()
                balance_usdt =float( get_balance.get('USDT'))
                balance_sol = float(get_balance.get('SOL')) * self.market.get_actual_price()
                balance = round(balance_sol + balance_usdt, 2)
                first_day = {'SOLUSDT': [{
                        'date': f"{datetime.now().strftime('%Y-%m-%d')} 23:59:00",
                        'balance': balance,
                        'laps': 0,
                        'profit': 0.0
                    }]}
                with open('config/profit.json', 'w') as f:
                        json.dump(first_day, f, indent=4)
            self.laps.clear()

    def start(self) -> None:
        """Buy - USDT, sell - SOL"""
        self.notify.bot_status(f'Bot started trading on pair {self.symbol}')
        print('bot was started')
        logging.info('bot was started')
        
        while self.bot_status:
                self.add_profit()
                time.sleep(1)
                self.sell_position = self.orders.get_open_orders()
                if self.sell_position == False:
                    self.sell_notify()
                    self.orders.clear()
                balance = self.account.get_balance()

                #Первая покупка
                if self.orders.get() is not None and self.orders.qty() == 0:
                    self.first_buy()
       
                #Усреднение
                if self.orders.qty() != 0 and float(balance.get('USDT')) > self.amount_buy:                    
                    self.averaging()

                if self.orders.qty() != 0 and float(balance.get('USDT')) < self.amount_buy:
                    if self.nem_notify_status == False:
                            self.not_enough_money_notify()
    
bot = Bot()

config = bot.get_config()