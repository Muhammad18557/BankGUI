
class OverdrawError(Exception):
    """Raised when an account is being overdrawn."""
    pass

class TransactionSequenceError(Exception):
    """Raised when transactions are not added in chronological order or applying interest more than once in a month."""
    def __init__(self, date, interest_error=False):
        self.latest_date = date
        self.interest_error = interest_error

class TransactionLimitError(Exception):
    """Raised when trying to add a transaction to a savings account that already has 5 transactions in the this month or 2 transactions in this day."""
    def __init__(self, mc, dc):
        self.month_violated = mc
        self.day_violated = dc