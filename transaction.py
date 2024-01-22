from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, Date, Float, ForeignKey
Base = declarative_base()
class Transaction(Base):
    """A class to record date and amount of deposits/withdrawals"""

    __tablename__ = 'transaction'
    _id = Column(Integer, primary_key=True)
    _account_id = Column(Integer, ForeignKey("account._id"))
    _amount = Column(Float(asdecimal=True))
    _date = Column(Date)

    def __init__(self, date, amount):
        self._amount = amount
        self._date = date
    
    def get_date(self):
        """Return the date of the transaction."""
        return self._date

    def get_amount(self):
        """Return the amount of the transaction."""
        return self._amount
    
    def __str__(self):
        return f"{self._date.strftime('%Y-%m-%d')}, ${self._amount:,.2f}"