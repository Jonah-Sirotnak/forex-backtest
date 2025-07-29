class RiskManager:
    def __init__(self, stop_loss_pct=0.25, stop_loss_type='fixed'):
        self.stop_loss_pct = stop_loss_pct
        self.stop_loss_type = stop_loss_type

    def get_stop_price(self, entry_price):
        """
        Calculate initial stop loss price below entry.
        """
        return entry_price * (1 - self.stop_loss_pct)

    def update_trailing_stop(self, stop_price, current_high):
        """
        Update trailing stop based on new highs.
        """
        new_stop = current_high * (1 - self.stop_loss_pct)
        return max(stop_price, new_stop)  # Only move up, never down (reference from the book)

    def check_stop(self, current_low, stop_price):
        """
        Check if stop loss was triggered by current low.
        """
        return current_low <= stop_price
    
    def get_stop_loss_type(self):
        """
        Return the stop loss type.
        """
        return self.stop_loss_type
