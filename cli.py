from bank import Bank
import sys
from datetime import datetime
import decimal 
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError
import logging
from transaction import Base
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker

class BankCLI:
    """Command-line interface for the bank."""

    def __init__(self):
        # the current account that is selected
        self._selected_account = None

        # create a database session
        self._session = Session()

        # get the bank object from the database
        self._bank = self._session.query(Bank).first()

        # if the bank object does not exist in the database, create a new one
        if not self._bank:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        else:
            logging.debug("Loaded from bank.db")

        self._choices = {
            "1": self._open_account,
            "2": self._summary,
            "3": self._select_account,
            "4": self._add_transaction,
            "5": self._list_transactions,
            "6": self._interest_and_fees,
            "7": self._quit
        }
    
    def _display_menu(self):
        print(
f"""--------------------------------
Currently selected account: {self._selected_account}
Enter command
1: open account
2: summary
3: select account
4: add transaction
5: list transactions
6: interest and fees
7: quit
>""", 
    end="")

    def run(self):
        """Display the menu and respond to choices."""
        while True:
            self._display_menu()
            choice = input()
            action = self._choices.get(choice)
            if action:
                action()
            else:
                print(f"{choice} is not a valid choice")

    def _open_account(self):
        account_type = input("Type of account? (checking/savings)\n>")
        account_number = self._bank.open_account(account_type, self._session) # need to pass in session to open_account
        self._session.commit()
        logging.debug(f"Created account: {account_number}")
        logging.debug("Saved to bank.db")

    def _summary(self):
        self._bank.summary()

    def _select_account(self):
        account_number = input("Enter account number\n>")
        account = self._bank.select_account(account_number)
        if account:
            self._selected_account = account

    def _input_amount(self):
        # keep asking for input until a valid amount is entered
        while True:
            amount = input("Amount?\n>")
            try:
                amount = decimal.Decimal(amount)
                break
            except (decimal.InvalidOperation, ValueError):
                print("Please try again with a valid dollar amount.")
        return amount

    def _input_date(self):
        # keep asking for input until a valid date is entered
        while True:
            date = input("Date? (YYYY-MM-DD)\n>")
            try:
                date = datetime.strptime(date, "%Y-%m-%d").date()
                break
            except ValueError:
                print("Please try again with a valid date in the format YYYY-MM-DD.")
        return date
    
    def _add_transaction(self):
        amount = self._input_amount()
        date = self._input_date()
        try:      
            self._selected_account.add_transaction(amount, date, self._session)
            self._session.commit()
        except AttributeError:
            print("This command requires that you first select an account.")
        except OverdrawError:
            print("This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError as e:
            if e.month_violated:
                print("This transaction could not be completed because this account already has 5 transactions in this month.")
            else:
                print("This transaction could not be completed because this account already has 2 transactions in this day.")
        except TransactionSequenceError as e:
            print("New transactions must be from {} onward.".format(e.latest_date))
        else:
            logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {amount}")
            logging.debug("Saved to bank.db")

    def _list_transactions(self):
        try:
            self._selected_account.list_transactions()
        except AttributeError:
            print("This command requires that you first select an account.")

    def _interest_and_fees(self):
        try:
            # expecting a tuple that returns the status of the interest and fees transactions
            interest_details, fees_details = self._selected_account.apply_interest_and_fees(self._session) # need to pass in session to apply_interest_and_fees
            self._session.commit()
        except AttributeError:
            print("This command requires that you first select an account.")
        except TransactionSequenceError as e:
            month_name = datetime.strptime(str(e.latest_date.month), "%m").strftime("%B")
            print("Cannot apply interest and fees again in the month of {}.".format(month_name))
        else:
            # if interest was applied
            if interest_details[0]:
                logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {interest_details[1]}")
            # if fees was deducted for applying interest on balance below $100 
            if fees_details[0]:
                logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {fees_details[1]}")
            logging.debug("Triggered interest and fees")
            logging.debug("Saved to bank.db")
    def _quit(self):
        sys.exit()
    
if __name__ == "__main__":
    logging.basicConfig(filename='bank.log', level=logging.DEBUG, 
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    
    engine = sqlalchemy.create_engine('sqlite:///bank.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)

    try:
        BankCLI().run()
    except Exception as e:
        print("Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
        logging.error(f"{type(e).__name__}: {repr(str(e))}")