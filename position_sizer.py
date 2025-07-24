class PositionSizer:
    def __init__(self, position_pct=0.01):
        self.position_pct = position_pct

    def calculate(self, entry_price, current_equity):
        if entry_price == 0:
            return 0
        capital_to_allocate = current_equity * self.position_pct
        position_size = capital_to_allocate / entry_price
        return position_size
