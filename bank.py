from transaction import Base
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from checking_account import CheckingAccount
from savings_account import SavingsAccount

class Bank(Base):
    """Bank has accounts and customers."""
    
    __tablename__ = "bank"
    _id = Column(Integer, primary_key=True)
    _accounts = relationship("Account", backref="bank")

    def open_account(self, account_type, session):
        """Open an account of type savings/checking.

        Args: 
            account_type (str): savings or checking
        Returns:
            account_number (int)
        """
        account_number = len(self._accounts) + 1
        if account_type == "checking":
            account = CheckingAccount(account_number)
        elif account_type == "savings":
            account = SavingsAccount(account_number)
        else:
            print(f"Invalid account type {account_type}")
        self._accounts.append(account)
        session.add(account)
        return account_number

    def summary(self):
        """Return a summary of all accounts."""
        for account in self._accounts:
            print(account)

    def select_account(self, account_number):
        """Select an account by account number.
        
        Args:
            account_number (int)
        Returns:
            account (Account) or None
        """
        for account in self._accounts:
            if account.get_account_number() == int(account_number):
                return account
        return None
    
    def get_accounts(self):
        """Return a list of all accounts."""
        return self._accounts