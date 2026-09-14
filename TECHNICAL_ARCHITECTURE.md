# SecureBank Technical Architecture

This document describes how the application is assembled and how data travels through it. It is written from a technical point of view rather than as a beginner lesson.

## 1. System boundary

SecureBank is a local desktop client with a MySQL database:

```text
User
  |
  v
CustomTkinter UI in main.py
  |
  v
Database functions in database.py
  |
  v
mysql-connector-python
  |
  v
MySQL bank_db database
```

`config.py` supplies connection settings. `setup_database.sql` defines the database before the application starts.

The application is synchronous. A button callback performs validation and then performs a database query on the GUI thread. This keeps the code easy to understand, but a slow database connection would temporarily freeze the interface. A larger application would use a service layer and background tasks.

## 2. Module responsibilities

### Presentation layer: `main.py`

Responsibilities:

- create and configure the root window;
- construct page widgets;
- move between pages by clearing and rebuilding `shell`;
- read values from entry widgets;
- perform simple input validation;
- call database functions;
- display returned messages.

It owns the UI state variable `current_acc` and the two code-based admin constants.

It does not own SQL statements or connection lifecycle code.

### Data access layer: `database.py`

Responsibilities:

- create MySQL connections;
- generate account numbers;
- execute parameterized SQL;
- commit write operations;
- return rows or simple result values to the UI.

It does not create Tkinter widgets or decide where a message appears.

### Configuration: `config.py`

Responsibilities:

- provide `DB_CONFIG` to `mysql.connector.connect()`.

Credentials are currently source-controlled for local classroom setup. A production deployment would load them from environment variables or a secret store.

## 3. Runtime initialization sequence

When Python runs `main.py`:

1. Python imports `tkinter`, `customtkinter`, `mysql.connector`, and `database`.
2. CustomTkinter dark appearance is selected.
3. UI constants and admin credentials are defined.
4. `root` is created.
5. The root window is set to fullscreen.
6. Escape is bound to leave fullscreen mode.
7. `shell` is created inside `root`.
8. `show_welcome()` builds the first page.
9. `root.mainloop()` starts Tkinter's event loop.

Nothing after `mainloop()` runs until the window closes because the event loop owns control of the application.

## 3A. Image asset pipeline

The workspace contains `images.png`, a 225 by 225 PNG bank illustration. `main.py` loads it when `draw_bank_mark()` builds a sidebar:

```text
images.png beside main.py
  |
  v
os.path.join(os.path.dirname(__file__), "images.png")
  |
  v
tk.PhotoImage(file=image_path)
  |
  v
scan every pixel and mark near-white pixels transparent
  |
  +-- full-size image for the welcome sidebar
  |
  +-- subsample(2, 2) copy for compact sidebars
  |
  v
tk.Label(parent, image=image)
```

The transparency pass is an in-memory transformation. It does not rewrite the asset on disk. For each pixel, the code calls `image.get(pixel_x, pixel_y)`. If red, green, and blue are all greater than 245, it calls `image.transparency_set(..., True)`. This removes white and near-white background pixels while preserving the teal, navy, and light gray logo shapes.

The threshold is a deliberate asset-specific choice. It handles an image whose background is white, but it is not a general background-removal algorithm. It can remove pale foreground pixels and does not create smooth alpha edges. For this 225 by 225 asset, the $225 \times 225 = 50{,}625$ pixel scan is small and happens only while a page is being built. Large or frequently changing images should be preprocessed offline or handled by an image library.

`PhotoImage` objects must remain referenced by a live Python object. The code stores the image as `parent.logo_image` before assigning it to a Tkinter `Label`. When the page is destroyed, its parent and image reference are destroyed together. `images.png` must remain beside `main.py`; otherwise `PhotoImage` raises a file-loading error during page construction.

## 4. UI composition model

The application uses a single-root, single-shell composition model:

```text
root
└── shell
    ├── current sidebar
    └── current content frame
```

A page switch calls `clear(shell)`. That function destroys every direct child of `shell`. The selected page function then creates new sidebar and content frames.

This avoids `CTkToplevel` popups and avoids a page-class registry. The tradeoff is that each page is rebuilt, so unsaved entry text disappears when the user navigates away.

## 5. UI helper dependency graph

```text
show_welcome()
  ├── draw_bank_mark()
  ├── button()
  └── outline()

show_customer_dashboard()
  ├── make_customer_shell()
  │   └── draw_bank_mark()
  ├── show_customer_menu()
  │   └── nav_button()
  └── database.get_account_details()

show_money_form()
  ├── show_customer_menu()
  ├── entry()
  ├── button()
  └── database.deposit() or database.withdraw()
```

`show_customer_menu()` is deliberately shared. It is the single source of truth for the customer sidebar: Overview, Deposit, Withdraw, Transfer, Transaction history, Change PIN, and Log out.

The helper only creates widgets. It does not make database decisions.

## 6. Login control flow

```text
Login button
  |
  v
show_customer_login.attempt_login()
  |
  +-- account == ADMIN_USERNAME and password == ADMIN_PASSWORD
  |       |
  |       +-- show_admin_dashboard()
  |
  +-- otherwise db.verify_customer_login(account, password)
          |
          +-- True: current_acc = account; show_customer_dashboard()
          |
          +-- False: display error
```

The admin path intentionally does not query the `admins` table. The user requested credentials stored in code and a single login box. The `admins` table remains in the schema for compatibility and possible future authentication work.

## 7. Signup control flow

```text
Signup form
  |
  v
Read name, phone, PIN, confirmation, deposit
  |
  v
Validate required fields
  |
  v
Validate phone and PIN format
  |
  v
Convert deposit to float and check minimum
  |
  v
db.create_account(name, pin, phone, deposit)
  |
  v
generate_account_number()
  |
  v
INSERT accounts row
  |
  v
COMMIT and return account number
```

The account number generator opens its own connection, repeatedly executes a lookup, and closes its connection after an unused number is found. `create_account()` then opens a second connection for the INSERT.

This is simple but not perfectly concurrency-safe: two simultaneous processes could theoretically choose the same unused number before either inserts. The primary key still prevents a duplicate row; a production generator would handle a duplicate retry or use a database-generated identifier.

## 8. Database schema and relationships

```text
accounts
--------
acc_no PK
name
pin
phone
balance
created_at
   |
   | one account has many transactions
   v
transactions
------------
txn_id PK
acc_no FK -> accounts.acc_no
txn_type
amount
related_acc
txn_time

admins
------
username PK
password
```

The foreign key uses `ON DELETE CASCADE`. Deleting an account automatically deletes its transaction history. This keeps orphan transaction rows from remaining after account deletion.

## 9. Database function contracts

### Account functions

`create_account(name, pin, phone, initial_deposit)` returns a new account number.

`delete_account(acc_no)` returns `True` when a row was deleted and `False` when no matching account existed.

`get_account_details(acc_no)` returns one row containing account number, name, balance, and creation time, or `None`.

`get_all_accounts()` returns all account rows ordered newest first.

`get_account_summary()` returns `(account_count, total_balance)`.

### Authentication and recovery functions

`verify_customer_login(acc_no, pin)` returns a boolean.

`get_phone_for_account(acc_no, phone)` returns a boolean indicating whether both values match one row.

`change_pin(acc_no, new_pin)` updates the PIN and returns whether a row was affected.

`verify_admin_login()` remains available but is not used by the current UI because admin login is code-based.

### Money functions

`deposit()` writes an account balance update and one transaction row.

`withdraw()` returns `(False, message)` for insufficient funds or `(True, message)` after updating the balance and transaction log.

`transfer()` returns the same tuple style. It updates two balances and inserts two transaction rows in one connection before committing.

## 10. Transaction behavior

A deposit has one write to `accounts` and one write to `transactions`:

```text
balance = balance + amount
log DEPOSIT
commit
```

A withdrawal follows:

```text
read balance
if balance < amount: close and return failure
balance = balance - amount
log WITHDRAW
commit
```

A transfer follows:

```text
reject same sender and recipient
check recipient
read sender balance
reject insufficient funds
subtract sender
add recipient
log TRANSFER OUT
log TRANSFER IN
commit
```

The transfer writes all changes through one connection and commits once. The code does not explicitly call `rollback()` when an unexpected exception occurs. That is an important production improvement.

## 11. SQL safety and current risks

The project uses parameterized statements such as:

```python
cursor.execute(
    "SELECT acc_no FROM accounts WHERE acc_no = %s",
    (acc_no,)
)
```

This prevents user input from being interpreted as part of the SQL command.

Current risks:

- PINs and the admin password are plain text;
- the admin credentials are visible in source code;
- there is no authorization session beyond the local screen state;
- money is parsed as Python `float` rather than `Decimal`;
- database connections are manually repeated in every function;
- unexpected database errors can leave a connection or transaction incomplete;
- account deletion has no confirmation dialog;
- the forgot-PIN flow displays a support message but sends no real message.

These limitations are documented intentionally because the project is designed for learning and local demonstration.

## 12. Error boundaries

The UI catches `mysql.connector.Error` around several user-triggered operations and displays the exception text. Validation catches `ValueError` around numeric conversion.

The database layer mostly assumes that the connection and expected rows exist. For example, `withdraw()` assumes the account lookup returns a row before reading `[0]`. The current UI normally supplies an account that just logged in, but a stronger data layer would handle missing rows explicitly.

## 13. Recommended production evolution

A production-oriented version could be developed in this order:

1. move credentials to environment variables;
2. hash customer PINs and admin passwords;
3. replace floats with `Decimal` and fixed-point database values;
4. add connection context managers and rollback handling;
5. make transfers transactional with explicit isolation requirements;
6. add role-based admin authentication;
7. add confirmation and audit logging for deletion;
8. put database work behind a service layer;
9. add automated tests for database operations and validation;
10. move slow database work off the GUI thread;
11. add an actual SMS or email provider only after secure recovery design;
12. add logging that does not record PINs or passwords.

## 14. Testing map

A useful test plan maps each requirement to a check:

| Area | Check |
|---|---|
| Startup | `python main.py` opens fullscreen |
| Syntax | `python -m py_compile main.py database.py` |
| Signup | valid account receives a six-digit number |
| Signup validation | bad phone, PIN, confirmation, and deposit are rejected |
| Login | valid customer reaches dashboard; bad PIN is rejected |
| Admin | `admin` / `admin123` reaches admin workspace |
| Deposit | balance and history increase |
| Withdrawal | insufficient balance does not change balance |
| Transfer | both account balances and both histories change |
| Recovery | only a matching account and phone show masked contact output |
| Change PIN | new PIN works after update |
| Delete | account and cascaded transaction rows disappear |

## 15. Change guide for future developers

When adding a feature, keep the dependency direction:

```text
main.py -> database.py -> config.py
```

The database layer should not import `main.py`, and the UI should not write SQL directly. Add a database function first, connect it to a page or button second, then update both documentation files and the test plan.
