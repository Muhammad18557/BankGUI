# Bank GUI Application

This application serves as a graphical platform for bank-related operations, written in Python. It offers a user-friendly interface for executing banking transactions such as account creation, transaction logging, and the application of interest and fees for different account types.

## Prerequisites

To ensure the smooth operation of the Bank Interface Application, you'll need to have the following components installed:

- **Python** (3.x version recommended)
- **Tkinter**: Python's built-in GUI package, interfacing with the Tk toolkit.
- **SQLAlchemy**: A comprehensive toolkit and ORM framework for Python that facilitates SQL database interactions.
- **tkcalendar**: A Tkinter-compatible calendar widget, enhancing date selection capabilities.

These dependencies can be installed via pip. For an enhanced experience, consider setting up a Python virtual environment before proceeding with the installation:

```sh
pip install sqlalchemy tkcalendar
```

## How to Use
Launch the application by executing the gui.py script with Python:
```
python gui.py
```
Upon execution, the application presents a window with multiple functionalities:

Open Account: Initiates the process of creating a new bank account, providing options for account type selection (savings or checking) and setting an initial deposit.

Add Transaction: Enables the addition of transactions to an existing account. Users must select an account, specify the transaction amount, and pick a date from the calendar. Alerts are generated for issues like insufficient funds or exceeding transaction limits.

Interest and Fees: Applies interest and applicable fees to a chosen account. Alerts are issued for unselected accounts or if the operations have already been completed for the current period.

Account information, including account numbers and balances, is displayed within the application. Users can select an account to view detailed transaction history in a dedicated panel.

## Data Management
SQLite is employed for data storage, with a ```bank.db``` database file generated in the application's running directory. This database encompasses tables for entities such as banks, accounts, and transactions.

## Exception Handling and Logging

The application robustly handles exceptions, providing user alerts for errors and logging details in a ```bank.log``` file for troubleshooting.


## Limitations
The current version of the Bank Interface Application does not support features like user authentication or the management of multiple user profiles. It is primarily designed for educational and demonstrative purposes. Additionally, the application lacks functionalities for account or transaction deletion and comes with basic placeholders for interest and fee calculations, which may require customization.

## Developer Information
This application was developed by Muhammad Abdullah. Contributions to enhance the application are highly encouraged. For bug reports or suggestions, please feel free to open an issue or propose a pull request.


