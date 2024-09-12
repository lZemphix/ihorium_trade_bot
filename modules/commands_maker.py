import os
from typing import Any

class CCreate:
    def __init__(self) -> None:
        self.path = '../setup/test.txt'

    def read_file(self):
        with open(self.path, 'r') as file:
            return file.read()
    
    def update_file(self, data: Any):
        with open(self.path, 'a') as f:
            f.write(f'{data}\n')

    def converter(self):
        """cm1 cm2, cm3 ... cmn"""
        data = str(input('commands:\n\n> '))
        splitted = data.split(', ')
        self.update_file(*splitted)

        print('OK!')
             

create = CCreate()
if __name__ == '__main__':
    # try:
        create.converter()
    # except Exception as e:
        # print(e)