import tkinter as tk
from tkinter import ttk
from checking_account import CheckingAccount
from savings_account import SavingsAccount

class TransactionStack(tk.Frame):
    """ A stack of labels representing transactions"""
    def __init__(self, parent, transactions, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._transactions = transactions
        self._labels = []
        for transaction in self._transactions:
            newLabel = ttk.Label(parent, text=str(transaction), width=25, anchor=tk.CENTER, justify=tk.CENTER)
            if transaction.get_amount() < 0:
                newLabel.config(foreground="red")
            newLabel.pack(padx=10, ipady=10, pady=2)
            self._labels.append(newLabel)

    def delete(self):
        for label in self._labels:
            label.destroy()

class SummaryStack(tk.Frame):
    """ A stack of selectable radio buttons representing accounts"""
    def __init__(self, parent, accounts,select_account, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._accounts = accounts
        self._buttons = []
        self._select_account_callback = select_account
        self._buttons = []
        for account in self._accounts:
            newButton = tk.Radiobutton(parent, text=str(account), width=40, background="light gray", 
                                       activebackground="light blue",
                                       command=lambda account_number=account.get_account_number(): self._select_account_callback(account_number),
                                       value=account.get_account_number(), justify=tk.CENTER)
            if isinstance(account, CheckingAccount):
                newButton.config(foreground="black")
            elif isinstance(account, SavingsAccount):
                newButton.config(foreground="blue")
            newButton.pack(padx=10, ipady=10, pady=2, anchor=tk.W)
            self._buttons.append(newButton)
    def delete(self):
        for button in self._buttons:
            button.destroy()
