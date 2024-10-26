import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import json
from client import Account, Market
from typing import Any
from exceptions import exceptions as e

class LapsEdit:

    def __init__(self, path: str = 'config/.laps') -> None:
       self.path = path
       self.account = Account()
       self.market = Market()

    
    def clear(self) -> int:
        with open(self.path, 'w') as f:
            pass
        return 200
    
    def get(self) -> list[float]:
        with open(self.path, 'r') as f:
            filtered_file = []
            file = f.readlines()
            for el in file:
                if el != '':
                    filtered_file.append(float(el.replace('\n', '')))
            return filtered_file
        
    def qty(self) -> int:
        orders = self.get()
        return len(orders)
        
    def avg_lap_profit(self) -> float:
        avg = sum(self.get()) / self.qty()
        return round(avg,3)
    
    def calculate_profit(self) -> float:
        with open('config/bot_config.json', 'r') as f:
            config = json.load(f)
            step = config.get('stepSell')
            coin_price = float(self.market.get_actual_price())
            amount_buy = config.get('amountBuy')
            approx_profit = round((amount_buy/(0.01*(coin_price - step))*(coin_price*0.01)) - amount_buy, 3)
            return approx_profit

    def add(self, data: Any) -> int:
        with open(self.path, 'a') as f:
            f.write(f'{str(data)}\n')
        return 200
    
laps = LapsEdit()

if __name__ == '__main__':
    try:
        print(sum(laps.get()))
    except Exception as e:
        print(e)
