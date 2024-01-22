from exceptions import OverdrawError
from account import Account
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
import decimal
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

class CheckingAccount(Account):
    """Checking type of bank account."""

    __tablename__ = "checking_account"
    _id = Column(Integer, ForeignKey("account._id"), primary_key=True)
    _fees = Column(Float(asdecimal=True))
    _interest_rate = Column(Float(asdecimal=True))

    __mapper_args__ = {
        "polymorphic_identity":"checking"
    }

    def __init__(self, account_number):
        super().__init__(account_number)
        self._fees = decimal.Decimal(0.0)
        self._interest_rate = decimal.Decimal(0.08 / 100)
        self._type = "checking"
    
    def add_transaction(self, amount, date, session, ignore_constraints=False):
        """Add a transaction to a checking account after checking the constraints.
        
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
            raise OverdrawError("Account has insufficient funds.")
        return super().add_transaction(amount, date, session)
    
    def apply_interest_and_fees(self, session):
        """Apply interest and fees to a checking account."""
        if self.get_balance() < 100:
            self._fees = decimal.Decimal(5.44)
        else:
            self._fees = decimal.Decimal(0.0)
        return super().apply_interest_and_fees(self.get_balance() * self._interest_rate, self._fees, session)
    
    def __str__(self):
        return f"Checking#{self._account_number:09},\tbalance: ${self._balance:,.2f}"
