class PositionSizer:
    """
    Calculates position sizes based on fixed percentage of equity.
    """
    def __init__(self, position_pct=0.01):
        self.position_pct = position_pct

    def calculate(self, entry_price, current_equity):
        """
        Calculate position size based on current equity and entry price.
        """
        if entry_price == 0:
            return 0
        
        # Calculate capital to allocate (percentage of current equity)
        capital_to_allocate = current_equity * self.position_pct
        
        # Convert capital to position size (shares/units)
        position_size = capital_to_allocate / entry_price
        return position_size
