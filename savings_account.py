from exceptions import OverdrawError, TransactionLimitError
from account import Account
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
import decimal
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

class SavingsAccount(Account):
    """Savings type of bank account."""

    __tablename__ = "savings_account"
    _id = Column(Integer, ForeignKey("account._id"), primary_key=True)
    _fees = Column(Float(asdecimal=True))
    _interest_rate = Column(Float(asdecimal=True))

    __mapper_args__ = {
        "polymorphic_identity" : "saving"
    }
    
    def __init__(self, account_number):
        super().__init__(account_number)
        self._fees = decimal.Decimal(0.0)
        self._interest_rate = decimal.Decimal(0.41 / 100)
        self._type = "saving"

    def add_transaction(self, amount, date, session, ignore_constraints=False):
        """Add a transaction to a savings account after checking the constraints.
        
        Args:
            amount (decimal.Decimal)
            date (datetime.date)
            ignore_constraints (bool): ignore amount constraints if True
        Returns:
            True if successful
        Raises:
            OverdrawError if account has insufficient funds
        """
        if not ignore_constraints and self.get_balance() + amount < 0: 
            raise OverdrawError
        transactions = self.get_transactions()
        month_count, day_count = 0, 0
        if len(transactions) >= 2:
            for t in transactions:
                if t.get_date().month == date.month and t.get_date().year == date.year:
                    month_count += 1
                    if t.get_date().day == date.day:
                        day_count += 1
                if month_count >= 5 or day_count >= 2:
                    # raise exception with boolean arguments to indicate which constraint was violated
                    raise TransactionLimitError(month_count >= 5, day_count >= 2)
        return super().add_transaction(amount, date, session)


    def apply_interest_and_fees(self, session):
        """Apply interest and fees to a savings account."""
        return super().apply_interest_and_fees(self.get_balance() * self._interest_rate, self._fees, session)

    def __str__(self):
        return f"Savings#{self._account_number:09},\tbalance: ${self._balance:,.2f}"