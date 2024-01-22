from bank import Bank
import sys
from datetime import datetime
import decimal
from exceptions import OverdrawError, TransactionSequenceError, TransactionLimitError
import logging
from transaction import Base
import sqlalchemy
from sqlalchemy.orm.session import sessionmaker
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from custom import TransactionStack, SummaryStack
from tkcalendar import Calendar, DateEntry
from checking_account import CheckingAccount
from savings_account import SavingsAccount

class BankGUI:
    """A GUI for the Bank"""
    def __init__(self):
        self._selected_account = None
        self._session = Session()
        self._bank = self._session.query(Bank).first()

        if self._bank:
            logging.debug("Loaded from bank.db")
        else:
            self._bank = Bank()
            self._session.add(self._bank)
            self._session.commit()
            logging.debug("Saved to bank.db")
        
        self._root_window_init()
        self._menu_frame_init()
        self._choices_frames_init()
        
        self._transactions = []
        self._accounts = []

        self._summary()

        self._root_window.mainloop()
    
    def _root_window_init(self):
        """Initialize the root window."""
        self._root_window = tk.Tk()
        self._root_window.title("MY BANK")
        self._root_window.geometry("750x500")
        ttk.Style(self._root_window).theme_use("clam")
        self._root_window.report_callback_exception = handle_exception
        self._root_window.grid_columnconfigure(0, weight=1)

    def _menu_frame_init(self):
        """Initialize the menu frame with three options: open acount, add transaction, interest and fees."""
        self._menu_frame = tk.Frame(self._root_window)
        self._menu_frame.grid(row=0, column=0, columnspan=3, sticky=tk.EW)

        self._menu_frame.grid_columnconfigure(0, weight=1)
        self._menu_frame.grid_columnconfigure(1, weight=1)
        self._menu_frame.grid_columnconfigure(2, weight=1)

        self._open_account_button = ttk.Button(self._menu_frame, width=20, text="open account", command=self._open_account_gui)
        self._open_account_button.grid(row=0, column=0, padx=7, pady=10, ipadx=3, ipady=4)
        self._add_transaction_button = ttk.Button(self._menu_frame, width=20, text="add transaction", command=self._add_transaction_gui)
        self._add_transaction_button.grid(row=0, column=1, padx=7, pady=10, ipadx=3, ipady=4)
        self._interest_and_fees_button = ttk.Button(self._menu_frame, width=20, text="interest and fees", command=self._interest_and_fees)
        self._interest_and_fees_button.grid(row=0, column=2, padx=7, pady=10, ipadx=3, ipady=4)

    def _choices_frames_init(self):
        """Initialize the frames for the menu options."""
        self._open_account_frame = tk.Frame(self._root_window)
        self._summary_frame = tk.Frame(self._root_window)
        self._add_transaction_frame = tk.Frame(self._root_window)
        self._list_transactions_frame = tk.Frame(self._root_window)

        self._summary_frame.grid(row=2, column=0, sticky=tk.NSEW)
        self._list_transactions_frame.grid(row=2, column=1, sticky=tk.NSEW)


    def _open_account_gui(self):
        """Fills in the open account frame."""
        self._open_account_frame.grid(row=1, column=0)

        # dropdown label
        label = tk.Label(self._open_account_frame, text="Account Type:")
        label.grid(row=0, column=0)

        # dropdown menu
        option = tk.StringVar()
        option.set("Checking")
        dropdown = tk.OptionMenu(self._open_account_frame, option, "Checking", "Savings")
        dropdown.grid(row=0, column=1)

        def enter_callback():
            self._open_account(option.get().lower())
            cancel_callback()

        def cancel_callback():
            for child in self._open_account_frame.winfo_children():
                child.destroy()
            self._open_account_frame.grid_forget()
            self._summary()

        # enter and cancel buttons
        enter_button = tk.Button(self._open_account_frame, text="Enter", command=enter_callback)
        enter_button.grid(row=0, column=2)
        cancel_button = tk.Button(self._open_account_frame, text="Cancel", command=cancel_callback)
        cancel_button.grid(row=0, column=3)

    def _open_account(self, account_type):
        """Opens an account by calling the appropraite function from the bank class."""
        account_number = self._bank.open_account(account_type, self._session)
        self._session.commit()
        logging.debug(f"Created account: {account_number}")
        logging.debug("Saved to bank.db")

    def _summary(self):
        """Fills in the summary frame."""
        if hasattr(self, "_summary_widget"):
            self._summary_widget.delete()
        self._accounts = self._bank.get_accounts()
        self._summary_widget = SummaryStack(self._summary_frame, self._accounts, self._select_account)

    def _select_account(self, account_number):
        """Selects an account and updates the list of transactions according to which account was selected."""
        account = self._bank.select_account(account_number)
        self._selected_account = account
        self._list_transactions()


    def _add_transaction_gui(self):
        """Fills in the add transaction frame."""
        if not self._selected_account:
            messagebox.showwarning("No Account Selected", "This command requires that you first select an account.")
            return
        self._add_transaction_button.config(state=tk.DISABLED)
        self._add_transaction_frame.grid(row=1, column=1, sticky=tk.NSEW)

        def enter_callback():
            try:
                amount = decimal.Decimal(entered_amount.get())
                selected_date = cal.get_date()
                date = datetime.strptime(selected_date, "%m/%d/%y").date()
                if self._add_transaction(amount, date):
                    cancel_callback()
                    
            except decimal.InvalidOperation:
                messagebox.showwarning("Invalid Amount", "Please enter a valid amount.")

        def cancel_callback():
            for child in self._add_transaction_frame.winfo_children():
                child.destroy()
            self._add_transaction_frame.grid_forget()
            self._list_transactions()
            self._summary()
            self._add_transaction_button.config(state=tk.NORMAL)

        label = tk.Label(self._add_transaction_frame, text="Amount:")
        label.pack(padx=5, pady=3)

        def disable_non_numeric(event):
            if event.keysym == 'BackSpace':
                new_value = event.widget.get()
            else:
                # handle new character at the middle (or end)
                position = entered_amount.index(tk.INSERT)
                new_value = event.widget.get()[:position] + event.char + event.widget.get()[position:]

            # allow single -ve sign
            if new_value.count('-') > 1:
                return "break"
            # -ve sign only at the beginning
            if (new_value.count('-') == 1 and new_value[0] != '-'):
                return "break"
            # allow single decimal point
            if event.char in ['.'] and new_value.count(event.char) > 1:
                return "break"
            try:
                if new_value and new_value != "-":
                    float(new_value)
            except ValueError:
                return "break"
            except Exception:
                return "break"
            
        entered_amount = tk.Entry(self._add_transaction_frame, width=20)
        entered_amount.pack(padx=5, pady=3)
        entered_amount.bind('<Key>', disable_non_numeric)
        entered_amount.bind('<Return>', lambda event: enter_callback())

        enter_button = tk.Button(self._add_transaction_frame, text="Enter", command=enter_callback)
        enter_button.pack(padx=5, pady=3)
        cancel_button = tk.Button(self._add_transaction_frame, text="Cancel", command=cancel_callback)
        cancel_button.pack(padx=5, pady=3)

        cal = Calendar(self._add_transaction_frame, selectmode="day", 
                       month = datetime.now().month, year = datetime.now().year,
                          day = datetime.now().day)
        cal.pack(padx=5, pady=3)


    def _add_transaction(self, amount, date):
        """Adds a transaction to the selected account."""
        completed = False
        try:      
            self._selected_account.add_transaction(amount, date, self._session)
            self._session.commit()
            completed = True
        except OverdrawError:
            messagebox.showwarning("Overdraw Error", "This transaction could not be completed due to an insufficient account balance.")
        except TransactionLimitError as e:
            if e.month_violated:
                messagebox.showwarning("Transaction Limit Error", "This transaction could not be completed because this account already has 5 transactions in this month.")
            else:
                messagebox.showwarning("Transaction Limit Error", "This transaction could not be completed because this account already has 2 transactions in this day.")
        except TransactionSequenceError as e:
            messagebox.showwarning("Transaction Sequence Error", "New transactions must be from {} onward.".format(e.latest_date))
        else:
            logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {amount}")
            logging.debug("Saved to bank.db")
        finally:
            return completed

    def _list_transactions(self):
        """Fills in the list transactions frame."""
        if hasattr(self, "_list_transactions_widget"):
            self._list_transactions_widget.delete()
        self._transactions = self._selected_account.get_transactions()
        self._list_transactions_widget = TransactionStack(self._list_transactions_frame, self._transactions)

    def _interest_and_fees(self):
        """Applies interest and fees to the selected account."""
        try:
            # expecting a tuple that returns the status of the interest and fees transactions
            interest_details, fees_details = self._selected_account.apply_interest_and_fees(self._session)
            self._session.commit()
        except AttributeError:
            messagebox.showwarning("No Account Selected", "This command requires that you first select an account.")
        except TransactionSequenceError as e:
            month_name = datetime.strptime(str(e.latest_date.month), "%m").strftime("%B")
            messagebox.showwarning("Applying Again", "Cannot apply interest and fees again in the month of {}.".format(month_name))
        else:
            # if interest was applied
            if interest_details[0]:
                logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {interest_details[1]}")
            # if fees was deducted for applying interest on balance below $100 
            if fees_details[0]:
                logging.debug(f"Created transaction: {self._selected_account.get_account_number()}, {fees_details[1]}")
            logging.debug("Triggered interest and fees")
            logging.debug("Saved to bank.db")
            self._list_transactions()
            self._summary()

def handle_exception(exception, value, traceback):
    """Handle uncaught exceptions."""
    messagebox.showerror("Error", "Sorry! Something unexpected happened. Check the logs or contact the developer for assistance.")
    logging.error(f"{type(exception).__name__}: {repr(str(exception))}")
    sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(filename='bank.log', level=logging.DEBUG, 
                    format='%(asctime)s|%(levelname)s|%(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    engine = sqlalchemy.create_engine('sqlite:///bank.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker()
    Session.configure(bind=engine)
    BankGUI()
