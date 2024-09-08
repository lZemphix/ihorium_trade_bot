from client import Client

class Grids:
    
    def __init__(self, interval: int = 5, symbol: str = 'SOLUSDT') -> None:
        self.interval = interval
        self.symbol = symbol
        self.cli = Client(symbol=self.symbol, 
                       interval=self.interval)

    def set_grids(self, grids: int = 5) -> list[float]:
        grids_place = []
        df = (self.cli.get_kline_dataframe()).astype(float)
        max_ = df.close.max()
        low_ = df.close.min()
        diff_grids = round(((max_ + 4) - (low_ - 4)) / grids, 2)
        for grid in range(grids):
            grids_place.append(float(round(grid*diff_grids + low_ - 4, 2)))
        return grids_place, diff_grids
        
    @staticmethod
    def find_closest_values(grid, target):
        
        left = 0
        right = len(grid)-1

        left, right = 0, len(grid) - 1
        
        while left <= right:
            mid = (left + right) // 2
            mid_value = grid[mid]
            
            if mid_value == target:
                return grid[mid - 1] if mid > 0 else None, grid[mid + 1] if mid < len(grid) - 1 else None
            elif mid_value < target:
                left = mid + 1
            else:
                right = mid - 1
        
        lower = grid[right] if right >= 0 else None
        upper = grid[left] if left < len(grid) else None
        print(grid)
        return lower, upper

    def write_grids(self):
        with open('src/grids.grd', 'w') as f:
            grid_num = 0
            for grid in self.set_grids(grids=30)[0]:
                grid_num += 1
                f.write(f'{str(grid)}' + '\n')
            

    @staticmethod
    def test():
        with open('src/grids.grd', 'r') as f:
            __filtered_grids = []
            grids = f.readlines()
            for grid in grids:
                __filtered_grids.append(float(grid.replace('\n', '')))
            return __filtered_grids


grd = Grids()
if __name__ == '__main__':
    try:
        # Grids().write_grids()
        # Grids().test()
        print(grd.find_closest_values(grd.test(), 128))
    except Exception as e:
        print(e)