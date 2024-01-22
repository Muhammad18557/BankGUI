from transaction import Transaction, Base
import datetime
from exceptions import TransactionSequenceError
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
import decimal
decimal.getcontext().rounding = decimal.ROUND_HALF_UP

class Account(Base):
    """Bank account class"""

    __tablename__ = "account"

    _id = Column(Integer, primary_key=True)
    _bank_id = Column(Integer, ForeignKey("bank._id"))

    _transactions = relationship("Transaction", backref="account")
    _type = Column(String)
    _account_number = Column(Integer)
    _balance = Column(Float(asdecimal=True))
    _latest_interest_date = Column(Date)
    
    __mapper_args__ = {
        'polymorphic_identity':'account', 
        'polymorphic_on': _type
    }
    
    def __init__(self, account_number=None):
        self._balance = decimal.Decimal(0.0)
        self._account_number = account_number
    
    def get_transactions(self):
        """Return a list of transactions."""
        return self._transactions
    
    def get_balance(self):
        """Return the current balance."""
        return self._balance

    def get_account_number(self):
        """Return the account number."""
        return self._account_number

    def add_transaction(self, amount, date, session):
        """Add a transaction.
        
        Args:
            amount (decimal.Decimal)
            date (datetime.date)
        Returns:
            True if successful
        Raises:
            TransactionSequenceError if date is before latest transaction date
        """
        if self._transactions:
            latest_date = max(t.get_date() for t in self._transactions)
            if date < latest_date:
                raise TransactionSequenceError(latest_date)
        new_transaction = Transaction(date, amount)
        self._transactions.append(new_transaction)
        self._balance += amount
        session.add(new_transaction)
        return True

    def list_transactions(self):
        """List all transactions sorted by date."""
        transactions = self._transactions
        transactions.sort(key=lambda t: t.get_date())
        [print(t) for t in transactions]
    
    def apply_interest_and_fees(self, interest, fees, session):
        """Apply interest and fees by adding relevant calculated transactions.
        
        Args:
            interest (decimal.Decimal): interest rate
            fees (decimal.Decimal): fees
        Returns:
            ((applied_interest, interest), (applied_fees, fees)) (tuple of tuples)
        """
        applied_interest, applied_fees = False, False
        if self._transactions:
            latest_transaction_date = max(t.get_date() for t in self._transactions)
        if self._latest_interest_date and self._latest_interest_date >= latest_transaction_date:
            raise TransactionSequenceError(latest_transaction_date)
        month, year = self._transactions[-1].get_date().month, self._transactions[-1].get_date().year
        last_day = {1: 31, 2: 28, 3: 31, 4: 30, 5:31, 6: 30, 7: 31, 8: 31, 9: 30, 10:31, 11: 30, 12: 31}
        last_date_of_month = datetime.datetime.strptime(str(year) + "-" + str(month) + "-" + str(last_day[month]), "%Y-%m-%d").date()
        res = self.add_transaction(interest, last_date_of_month, session, True)
        if fees > 0:
            res = self.add_transaction(-1 * fees, last_date_of_month, session, True)
            applied_fees = True
        if res:
            self._latest_interest_date = last_date_of_month
            applied_interest = True
        return ((applied_interest, interest), (applied_fees, -1 * fees))