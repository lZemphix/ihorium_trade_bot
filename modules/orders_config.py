from typing import Any
from client import Client
from exceptions import exceptions as e


class OrdersEdit:

    def __init__(self, path: str = 'config/orders.txt') -> None:
       self.path = path
       self.cli = Client('SOLUSDT')

    def get_last_order(self) -> float:
        if self.cli.get_orders().get('result').get('list')[0].get('side') == 'Buy':
            last_order = self.cli.get_orders().get('result').get('list')[0].get('avgPrice')
            return float(last_order)
        else:
            raise e.OrderException('Last order has a side "Sell"')

    def add(self, data: Any) -> str:
        with open(self.path, 'a') as f:
            f.write(f'{str(data)}\n')
        return 'Succesful!'
    
    def clear(self) -> str:
        with open(self.path, 'w') as f:
            pass
        return 'Succesful!'
    
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
    
    def avg_order(self) -> float:
        avg = sum(self.get()) / self.qty()
        return avg
    

orders = OrdersEdit()

if __name__ == '__main__':
    try:
        print(orders.avg_order())
    except Exception as e:
        print(e)
