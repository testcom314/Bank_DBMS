# SecureBank Concepts and Code Guide

This is a short reference to the concepts used in the current version of the project. For full explanations, read `STUDENT_GUIDE.md` and `TECHNICAL_ARCHITECTURE.md`.

## 1. Program structure

The project uses a simple three-layer structure:

- `config.py` contains MySQL connection settings.
- `database.py` contains SQL and database operations.
- `main.py` contains the CustomTkinter interface and user actions.

The GUI does not write SQL itself. For example, when a customer clicks Deposit, `main.py` reads and validates the amount, then calls `db.deposit(current_acc, amount)`. Keeping SQL in one file makes the program easier to test and change.

## 2. The single-window GUI

`main.py` creates one root window and one `shell` frame. `show_welcome()`, `show_customer_dashboard()`, `show_money_form()`, `show_history()`, and `show_admin_dashboard()` are views inside that same shell.

The `clear(parent)` function removes the widgets from the current view. The next view then creates its own widgets in the same root window. This is intentionally straightforward: there is no screen class hierarchy and no complicated routing system to learn.

The left sidebar is a navigation menu. Its buttons call view functions directly. Deposit, withdrawal, transfer, and history are pages in the shell rather than popup windows. The application starts with only Login, Sign up, and Exit. It starts in fullscreen mode; pressing Escape leaves fullscreen mode.

## 3. The bank image

`draw_bank_mark()` loads the workspace `images.png` file with Tkinter's built-in `PhotoImage`. The function checks every pixel and marks near-white pixels transparent, removing the original white square so the image blends into the dark sidebar. Compact sidebars use `subsample(2, 2)` to make the image smaller. The image is stored on its parent frame so Tkinter keeps it alive while the page is visible.

The transparency threshold is intentionally simple: red, green, and blue must all be greater than 245. This is suitable for this small logo, but it could remove very pale artwork from a different image. The source PNG is never modified; transparency exists only in the in-memory Tkinter image.

## 4. CustomTkinter widgets

CustomTkinter provides the visual controls while keeping Tkinter's event-driven programming model:

- `CTkFrame` groups parts of the interface.
- `CTkLabel` displays headings, balances, messages, and timestamps.
- `CTkEntry` collects account numbers, PINs, and amounts.
- `CTkButton` connects a visible command to a Python function.
- `CTkScrollableFrame` displays long account and transaction lists.
- `CTkTabview` separates admin accounts, account creation, and transaction review.

The helper functions `entry()`, `button()`, `outline()`, and `nav_button()` keep repeated styling in one place without hiding the main application flow behind custom classes.

## 5. Event-driven programming

The program reaches `root.mainloop()` and waits for events. A button's `command` is a callback that runs only when the user clicks it. For example:

```python
button(form, "Transfer", submit)
```

This creates a button now, but the nested `submit()` function runs later. It can still access the form's entry widgets because Python closures preserve the surrounding function's variables.

## 6. Database connections and SQL

Most functions in `database.py` follow this sequence:

```python
conn = get_connection()
cursor = conn.cursor()
cursor.execute("SELECT ... WHERE acc_no = %s", (acc_no,))
rows = cursor.fetchall()
cursor.close()
conn.close()
```

`%s` parameters are important. They keep user input separate from the SQL command and reduce SQL injection risk. `commit()` is required after inserts, updates, and deletes so MySQL saves the change.

## 7. Database design

The SQL setup creates three tables:

- `accounts` stores the account number, customer name, phone number, PIN, balance, and creation date.
- `transactions` stores each deposit, withdrawal, or side of a transfer.
- `admins` stores the existing admin credentials table for database compatibility.

`accounts.acc_no` is the primary key. `transactions.acc_no` is a foreign key with `ON DELETE CASCADE`, so an account's transaction rows are removed when that account is deleted.

## 8. Banking operations

- Deposit increases the account balance and records a `DEPOSIT` transaction.
- Withdrawal first checks the current balance. If there is not enough money, it returns `(False, "Insufficient balance")`; otherwise it subtracts and records the transaction.
- Transfer rejects self-transfers, checks that the recipient exists, checks the sender balance, updates both accounts, and records `TRANSFER OUT` and `TRANSFER IN` rows.

The `(success, message)` return pattern keeps expected business failures easy for the GUI to display without throwing exceptions for normal user mistakes.

## 9. Input validation

The GUI validates required fields before calling the database:

- Customer PINs must contain exactly four digits.
- New customer deposits must be at least 500.
- Amounts must be numbers greater than zero.
- Transfer recipients cannot be empty.
- Admin-created account PINs must also contain exactly four digits.

Validation improves the user experience, but a production application should also validate inside the database/service layer because GUI validation can be bypassed.

## 10. Login, recovery, and PIN changes

The normal Login page handles both kinds of access. A customer enters an account number and PIN. An administrator enters the constants `ADMIN_USERNAME` and `ADMIN_PASSWORD` from `main.py`, currently `admin` and `admin123`. The start screen does not expose a separate admin button.

Sign up stores a phone number with the account. Forgot PIN checks both the account number and phone number, then displays the phone number with every digit except the last two replaced by `X`. It does not claim to send an SMS; it represents the support-contact step for this educational project. A signed-in customer can use Change PIN to save a new four-digit PIN.

## 11. Admin workspace

The admin workspace is reached by entering the admin credentials into the normal Login form. It provides three tabs and a summary area:

- Accounts shows every account, total account count, total balance, search, refresh, and deletion.
- New account creates an account from the admin side, including its phone number.
- All transactions shows the complete transaction log.

This is suitable for a classroom project. A real bank system must restore authentication, authorization, password hashing, audit logs, and confirmation for destructive operations before deployment.

## 12. Practical next suggestions

1. Store PINs and admin passwords as salted hashes instead of plain text.
2. Use `Decimal` for money values instead of Python `float` to avoid rounding errors.
3. Add database transactions and rollback handling around transfers.
4. Add an explicit confirmation step before deleting an account.
5. Add focused tests for validation, insufficient balance, self-transfer, and missing recipients.
6. Move database credentials to environment variables rather than keeping them in source code.
7. Add a search box and account export option to the admin workspace as the project grows.
