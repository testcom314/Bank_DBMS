# SecureBank: Student Learning Guide

This guide teaches the project from the beginning. It explains what each file does, what happens when a user clicks a button, how the database works, and how to answer common questions about the code.

## 1. What the program does

SecureBank is a desktop banking practice project. It lets a customer:

- create an account with a name, phone number, PIN, and opening deposit;
- log in with an account number and PIN;
- see the current balance;
- deposit money;
- withdraw money if enough balance exists;
- transfer money to another account;
- view transaction history;
- change the account PIN;
- request help after forgetting a PIN.

An administrator enters `admin` and `admin123` into the normal Login page. The admin workspace can list, search, create, and delete accounts and review all transactions.

This is an educational application, not a real banking system. It stores PINs and the administrator password as plain text so the SQL and Python are easy to study.

## 2. Files and responsibilities

### `main.py`

This is the user interface. It creates the window, draws pages, reads text boxes, validates input, and calls functions in `database.py`.

It should not contain SQL. For example, the login page asks `database.py` whether a login is valid instead of writing a `SELECT` query itself.

### `database.py`

This is the database layer. It opens MySQL connections and contains functions such as `create_account()`, `deposit()`, `withdraw()`, and `transfer()`.

The GUI calls these functions. This separation means that changing a SQL query normally does not require rebuilding the screen layout.

### `config.py`

This contains the MySQL connection dictionary:

```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "...",
    "database": "bank_db"
}
```

Keeping these values in one file makes local setup easier. In a real project, the password should come from an environment variable instead of source code.

### `setup_database.sql`

This creates the database and its tables. It is run in MySQL before starting the Python program.

### `requirements.txt`

This lists third-party packages. `customtkinter` provides the modern-looking widgets and `mysql-connector-python` lets Python communicate with MySQL.

### `CONCEPTS.md`

This is a short concepts reference. This file, `STUDENT_GUIDE.md`, is the teaching explanation. `TECHNICAL_ARCHITECTURE.md` describes the system from an engineering point of view.

## 3. Python basics used in the project

### Variables

A variable stores a value:

```python
current_acc = None
```

At first, no customer is logged in. After successful login, `current_acc` contains the account number. The customer pages use this value to know which account to read or update.

### Functions

A function is a named group of instructions:

```python
def clear(parent):
    for widget in parent.winfo_children():
        widget.destroy()
```

`clear()` has one job: remove the old page widgets from a frame. Functions make repeated actions easier to understand and reuse.

### Parameters and return values

Parameters are values given to a function. `database.py` uses them to know which account to update:

```python
def deposit(acc_no, amount):
```

A return value is information sent back to the caller. `withdraw()` returns two values:

```python
return True, "Withdrawal successful"
```

The GUI stores them as `success, message` and changes the message color based on `success`.

### Lists and tuples

A list can hold several values:

```python
fields = [name_entry, phone_entry, pin_entry]
```

A tuple is commonly returned by MySQL for one row:

```python
acc_no, name, balance, created = details
```

The names on the left must match the column order in the SQL `SELECT` statement.

### `if` statements

The app uses conditions to reject invalid input:

```python
if deposit < 500:
    status.configure(text="Minimum initial deposit is 500")
    return
```

`return` stops the current function. This prevents invalid data from reaching the database.

### `try` and `except`

Text from a Tkinter entry is always text. Converting it to a number can fail:

```python
try:
    amount = float(amount_entry.get().strip())
except ValueError:
    status.configure(text="Enter an amount greater than 0")
    return
```

The `try` block attempts conversion. If the text is not a number, Python raises `ValueError`, and the `except` block displays a friendly message.

### Nested functions and callbacks

A GUI waits for a click, so a button needs a function to run later:

```python
button(form, "Transfer", submit)
```

Here `submit` is passed without parentheses. This means “run this function when clicked.” Writing `submit()` would run it immediately while the page is being built.

The `submit()` functions inside pages are nested functions. They can use the entry widgets created by the same page because Python keeps access to the surrounding variables. This is called a closure.

## 3A. Important ideas that are easy to miss

These ideas are often used in real programs but are not always explained carefully in school lessons.

### Functions are values

In Python, a function can be stored in a variable, passed to another function, and placed in a list. A function name without parentheses means the function object itself:

```python
nav_button(nav, "Transfer", show_transfer_form)
```

`show_transfer_form` is passed to `nav_button`. The button stores it and calls it later when the user clicks. By contrast:

```python
nav_button(nav, "Transfer", show_transfer_form())
```

would call `show_transfer_form` immediately while the page is being created. Its return value would be passed to `nav_button`, which is not what we want.

This is the central idea behind event-driven programming: build the interface now, save instructions for later, and let the event loop decide when they run.

### What `lambda` means

The customer menu contains this code:

```python
("Deposit", lambda: show_money_form("Deposit"))
```

`lambda` creates a small unnamed function. It is roughly equivalent to:

```python
def open_deposit_page():
    show_money_form("Deposit")
```

The lambda is useful because `show_money_form` needs an argument. This would be wrong:

```python
nav_button(nav, "Deposit", show_money_form("Deposit"))
```

That calls the function immediately. The lambda delays the call until the button is clicked.

The general form is:

```python
lambda parameters: expression
```

Examples:

```python
double = lambda number: number * 2
```

This is the same basic behavior as:

```python
def double(number):
    return number * 2
```

Use a lambda for a short one-action callback. Use a normal `def` when the operation has multiple steps, validation, error handling, or a meaningful name. In this project, the login and transfer actions are normal nested functions because they are too large to be clear as lambdas.

### Closures: why nested callbacks can see form fields

Inside a page, the code creates an entry and then defines a callback:

```python
amount_entry = entry(form, "Amount")

def submit():
    amount = float(amount_entry.get().strip())
```

`submit()` is defined inside the same function that created `amount_entry`. Even though `submit()` runs later, it remembers the surrounding variable. This remembered surrounding scope is a closure.

The closure is useful in a GUI because each page can keep its own widgets private. The deposit page's `amount_entry` does not need to be a global variable. The callback carries access to it.

There is an important difference between reading and assigning an outer variable. Reading works directly:

```python
def show_name():
    print(name)
```

Assigning to an outer variable requires `nonlocal` if it belongs to the enclosing function. Assigning to a module-level variable requires `global`, which is why `current_acc` uses:

```python
global current_acc
current_acc = account
```

Global state is easy for a small school project, but larger programs usually store session state inside an application object.

### The default-argument trick in the Delete button

The admin account list creates a button for every account. Its callback is built like this:

```python
lambda number=acc_no: delete_admin_account(number)
```

The `number=acc_no` part saves the current account number as a default value. This matters because callbacks run later, after the loop has finished. Without saving the value, every button could accidentally use the last account number from the loop.

An equivalent version that is easier to debug is:

```python
def make_delete_command(account_number):
    def delete_this_account():
        delete_admin_account(account_number)
    return delete_this_account
```

Both versions create a closure. The short lambda is acceptable here because its job is small.

### How `pack()` works

`pack()` is Tkinter's geometry manager. A geometry manager decides where a widget appears inside its parent. `pack` places widgets against one side of the available space, one after another.

For example:

```python
button(form, "Login", attempt_login).pack(
    anchor="w", padx=28, pady=(18, 10)
)
```

Important options:

- `side="left"` or `side="right"` places a widget beside earlier widgets;
- the default side is `"top"`;
- `fill="x"` lets a widget stretch horizontally;
- `fill="both"` lets it stretch horizontally and vertically;
- `expand=True` gives the widget extra unused space;
- `anchor="w"` aligns it to the west, meaning the left side;
- `padx` adds horizontal outside space;
- `pady` adds vertical outside space;
- `pady=(18, 10)` means 18 pixels before and 10 pixels after.

`pack()` works relative to the widget's immediate parent. A button packed into `form` is positioned inside `form`, not directly inside `root`. This parent-child relationship is the basis of the whole layout.

The root layout is:

```python
shell.pack(fill="both", expand=True)
```

The shell fills the root in both directions and takes extra space. A page then uses:

```python
sidebar.pack(side="left", fill="y")
content.pack(side="left", fill="both", expand=True)
```

The sidebar takes a fixed-width column and stretches vertically. The content takes the remaining horizontal space and expands in both directions.

Do not mix `pack()` and `grid()` inside the same parent frame. A child frame may use `pack()` in its parent and then use `grid()` for its own children, but one parent should normally have one geometry manager. Mixing them in the same parent leads to layout errors and confusing results.

### Widget parents and the widget tree

Tkinter widgets form a tree. A widget has one parent, and the parent controls its position and lifetime:

```text
root
└── shell
    ├── sidebar
    │   ├── bank canvas
    │   └── buttons
    └── content
        └── form
            ├── entries
            └── buttons
```

When `clear(shell)` calls `destroy()` on the shell's children, the sidebar and content disappear. Their children disappear with them. This is why changing pages removes the old widgets without manually destroying every entry and label.

Destroying a widget is different from hiding it. `destroy()` removes it permanently. `pack_forget()` only removes it from the layout so it could be packed again. SecureBank uses destroy-and-rebuild because each page is simple and does not need to preserve unfinished form input.

### How a button really works

This call creates a CustomTkinter button:

```python
ctk.CTkButton(parent, text="Login", command=attempt_login)
```

There are three separate parts:

1. `parent` tells Tkinter where the button belongs.
2. `text` controls what the user sees.
3. `command` stores a callable to execute after a click.

The button does not continuously run `attempt_login`. Tkinter waits for a mouse event, recognizes that the click happened inside the button, and invokes the stored callback. `pack()` is then needed because creating a widget does not automatically place it on screen.

CustomTkinter's `CTkButton` is a themed wrapper around Tkinter behavior. It adds colors, corner radius, hover styling, and a modern appearance, but the important callback idea is the same as ordinary Tkinter's `Button`.

### The event loop and why the program appears to pause

At the bottom of the file:

```python
root.mainloop()
```

The event loop repeatedly waits for events such as mouse clicks, keyboard input, window resize, and window close. When an event arrives, Tkinter finds the relevant widget and runs its callback.

The program is not frozen while waiting. It is idle in an organized event loop. However, callbacks should finish quickly. If a callback performs a very slow query or an endless loop, the event loop cannot process repainting or new clicks until that callback returns. This makes the window look frozen.

For a larger application, slow database work would run in a worker thread or task, and the UI would be updated afterward on the GUI thread. This project keeps operations synchronous so the control flow remains easy to study.

### Why `root` and `shell` are created once

There should be one main Tkinter root. Creating multiple roots can cause confusing event loops and resource problems. SecureBank creates `root` once and changes the contents of `shell`.

`CTkToplevel` would create another window, but the project deliberately does not use it for actions. Keeping one root and one shell makes navigation predictable.

### Why `tkinter` and `customtkinter` are both imported

CustomTkinter supplies `CTkFrame`, `CTkButton`, `CTkEntry`, and other themed widgets. The standard `tkinter` module is still used for the `Canvas` and `TclError` fallback.

The two libraries can work together because CustomTkinter is built on top of Tkinter's window system. They should use the same root rather than creating unrelated roots.

### `configure()` changes an existing widget

The status message is created once:

```python
status = ctk.CTkLabel(form, text="", text_color=DANGER)
```

Later, the program changes it:

```python
status.configure(text="PINs do not match")
```

`configure()` updates an existing widget. It is different from creating a new label. This is useful for validation messages because the layout does not need to be rebuilt after every invalid input.

### `get()` and `delete()` on entry fields

An entry is an editable text widget. These methods are common:

```python
text = account_entry.get()
account_entry.delete(0, "end")
```

`get()` reads the current text. `delete(0, "end")` removes text from the first character to the end. `.strip()` removes leading and trailing spaces before validation.

## 3B. Python expressions used in the project

### List comprehensions

Signup reads all entry widgets with:

```python
name, phone, pin, confirmation, deposit_text = [
    field.get().strip() for field in fields
]
```

The part inside brackets is a list comprehension. It means: for each `field` in `fields`, call `get()` and `strip()`, then collect the results into a list.

The longer equivalent is:

```python
values = []
for field in fields:
    values.append(field.get().strip())
name, phone, pin, confirmation, deposit_text = values
```

The longer version is useful when debugging. The comprehension is shorter once the pattern is understood.

The admin search uses another comprehension:

```python
rows = [
    row for row in rows
    if search_text in str(row[0]).lower()
    or search_text in row[1].lower()
]
```

It keeps only rows whose account number or name contains the search text.

### Tuple unpacking

This line assigns four values at once:

```python
acc_no, name, balance, created = details
```

It is equivalent to indexing each position manually:

```python
acc_no = details[0]
name = details[1]
balance = details[2]
created = details[3]
```

Unpacking is readable when the SQL column order is known. If the number of values does not match, Python raises `ValueError`.

### Truthiness and `all()`

This validation is concise:

```python
if not all((name, phone, pin, confirmation, deposit_text)):
```

An empty string is false in a condition. `all()` returns `True` only when every value in the tuple is true. Therefore, the condition detects whether at least one field is empty.

This is different from checking whether values are valid. A non-empty string like `"hello"` is truthy, so PIN format needs its own test.

### Conditional expressions

The message helper chooses a color with:

```python
DANGER if error else ACCENT
```

This is a conditional expression. It means “use `DANGER` when `error` is true, otherwise use `ACCENT`.” The longer form would use an `if` statement before creating the label.

### The `global` keyword

`current_acc` is defined at module level. Inside the login function, assigning to it requires:

```python
global current_acc
```

Without `global`, Python would treat `current_acc` as a new local variable inside that function. The dashboard would then not see the updated account number.

Globals are not automatically bad, but they make state changes less controlled. The project uses one global because it has one active customer and is intended to remain understandable. An object such as `BankApp` would be a better state container in a larger system.

### Exceptions are objects with types

`ValueError` means a value has the wrong form, such as trying to convert `"abc"` to a float. `mysql.connector.Error` represents a database problem. Catching the specific expected type is better than catching every exception with `except Exception`, because broad catches can hide programming bugs.

The UI catches database errors at user-action boundaries. It does not catch every error everywhere, which lets unexpected coding errors remain visible during development.

### `try` does not validate business rules

This only checks whether conversion is possible:

```python
amount = float(text)
```

It does not check whether the amount is positive, affordable, or appropriate for the account. Those are separate business rules. SecureBank therefore performs both conversion and a later comparison with zero. The database performs balance checks for withdrawals and transfers.

## 4. How the GUI works

### Creating the root window

`root = ctk.CTk()` creates the main application window. It is created only once. `shell` is the main frame inside it:

```python
shell = ctk.CTkFrame(root, fg_color=BG, corner_radius=0)
shell.pack(fill="both", expand=True)
```

Every page is placed inside `shell`.

### Fullscreen mode

The program calls:

```python
root.attributes("-fullscreen", True)
```

This starts the app in fullscreen mode. The Escape key runs a small callback that turns fullscreen off, which is useful during testing.

### Page switching

There are no separate application windows for customer actions. A page function follows this pattern:

1. call `clear(shell)`;
2. create a sidebar and content frame;
3. add labels, fields, and buttons;
4. connect each button to its next function.

For example, `show_customer_dashboard()` clears the old login page and builds the balance page in the same root window.

### Widget helper functions

`entry()`, `button()`, `outline()`, and `nav_button()` create commonly used widgets with the same colors and sizes. This avoids copying a long style configuration every time a button is needed.

The helpers do not hide important business logic. They only handle appearance and basic widget construction.

### The bank drawing

`draw_bank_mark()` uses a Tkinter `Canvas`. It draws a triangle for a roof and rectangles for pillars and a base. These are simple vector shapes created by code, so no image file is required.

## 5. The start screen

`show_welcome()` creates exactly three choices:

- `Login` calls `show_customer_login()`;
- `Sign up` calls `show_create_account()`;
- `Exit` calls `root.destroy()`.

The admin workspace is deliberately not shown on this page. Admin access is checked inside the normal login function.

## 6. Login logic

The login page reads two strings:

```python
account = acc_entry.get().strip()
password = pin_entry.get().strip()
```

First, it compares them with the code constants:

```python
if account == ADMIN_USERNAME and password == ADMIN_PASSWORD:
    show_admin_dashboard()
```

If they are not the admin credentials, it calls:

```python
db.verify_customer_login(account, password)
```

If the database returns `True`, `current_acc` is set and the customer dashboard opens. Otherwise an error is shown.

## 7. Signup logic

Signup collects five values: name, phone, PIN, confirmation PIN, and initial deposit.

Validation happens in this order:

1. every field must contain text;
2. phone must contain digits and be at least seven characters;
3. PIN must contain exactly four digits;
4. both PIN entries must match;
5. deposit must convert to a number;
6. deposit must be at least 500.

Only after all checks pass does the GUI call:

```python
db.create_account(name, pin, phone, deposit)
```

The database function generates a six-digit account number, inserts the row, commits it, and returns the new account number.

## 8. Forgot PIN logic

The forgot-PIN page asks for an account number and phone number. `get_phone_for_account()` runs a parameterized query that requires both values to match the same account.

If they match, the UI masks every phone digit except the last two:

```python
masked_phone = "X" * max(0, len(phone) - 2) + phone[-2:]
```

For `9876543210`, this displays `XXXXXXXX10`. The educational project displays a support message; it does not connect to an SMS provider.

## 9. Customer banking actions

### Deposit

The GUI checks that the amount is greater than zero. `database.deposit()` adds it to the account balance and records a transaction.

### Withdrawal

`database.withdraw()` first reads the current balance. If the balance is too small, it returns a failure message. Otherwise it subtracts the amount and records a transaction.

### Transfer

`database.transfer()` checks three business rules:

1. the sender and recipient cannot be the same;
2. the recipient account must exist;
3. the sender must have enough balance.

If all checks pass, it subtracts from the sender, adds to the recipient, and writes two transaction records: `TRANSFER OUT` and `TRANSFER IN`.

### Change PIN

The page checks that the new PIN contains four digits and matches the confirmation. `database.change_pin()` updates the PIN for the logged-in account.

### Transaction history

`get_transaction_history()` selects rows for one account and sorts them by newest transaction first. The GUI creates one small card for each row inside a scrollable frame.

## 10. Admin features

The admin page includes:

- account count and total balance;
- account search by name or account number;
- account refresh;
- account deletion;
- account creation with phone number;
- complete transaction history.

The admin page is still a normal page inside the same window. It does not open a popup.

### Why destructive actions need confirmation

Deleting an account is different from changing a label on the screen: it removes the account and, because of the database foreign key, its transaction history too. The first Delete click therefore changes that row into a confirmation row with Confirm and Cancel buttons.

Clearing the database is even more serious. The admin page shows a Danger zone. The clear button opens an inline confirmation panel, and the final button is disabled until the exact phrase `CLEAR BANK DATABASE` is typed. This is similar to confirmation controls used by GitHub for destructive repository actions. The database function deletes transactions first and accounts second, but leaves the `admins` table so the administrator can log in again.

## 11. MySQL basics

A connection is the communication link to MySQL:

```python
conn = get_connection()
```

A cursor sends SQL commands:

```python
cursor = conn.cursor()
cursor.execute("SELECT ...", (value,))
```

`fetchone()` reads one result row. `fetchall()` reads all result rows. `commit()` saves an INSERT, UPDATE, or DELETE. Finally, the cursor and connection are closed.

The `%s` placeholder is not Python string formatting. It is a MySQL connector parameter placeholder:

```python
cursor.execute(
    "SELECT acc_no FROM accounts WHERE acc_no = %s",
    (acc_no,)
)
```

This is safer than joining user input into an SQL string.

## 12. Database tables

### `accounts`

One row represents one customer account. `acc_no` is the primary key, so it must be unique. `phone` is stored here because it belongs to the customer account.

### `transactions`

One row represents one account activity. `acc_no` connects it to an account. `related_acc` stores the other account for transfers and is empty for deposits and withdrawals.

### `admins`

This table is created for database compatibility. The current UI uses the constants in `main.py` for the requested simple admin login rather than reading admin credentials from this table.

## 13. Common viva questions and answers

### Why use a separate database file?

It separates data access from screen design. The GUI becomes easier to read, and SQL changes stay in one place.

### Why use a primary key?

A primary key identifies one row uniquely. Account numbers cannot accidentally be duplicated.

### Why call `commit()`?

Without `commit()`, MySQL may not permanently save an INSERT, UPDATE, or DELETE.

### Why validate before SQL?

It gives immediate messages and avoids sending obviously invalid input to the database. Important rules should still be checked in a production service layer.

### Why use parameterized SQL?

It keeps user input separate from the SQL command and helps prevent SQL injection.

### Why does a transfer write two transaction rows?

Both accounts need a history entry. The sender sees money leaving and the recipient sees money arriving.

### Why use `current_acc`?

After login, the app needs to remember which account is active while the user moves between pages.

### Why is the account number random?

`generate_account_number()` chooses a six-digit number and checks whether it is already used. It repeats until it finds an unused one.

### Why is this not production-ready?

PINs are plain text, the admin password is in source code, money uses Python floats, transfers need stronger rollback handling, and deletion needs an explicit confirmation. These are acceptable simplifications for a learning project but not for real financial software.

## 14. How to add a feature

Use this order:

1. decide what information the feature needs;
2. add or update a function in `database.py`;
3. add a page or button in `main.py`;
4. validate the input before calling the database;
5. show success and failure messages;
6. update the documentation;
7. run `python -m py_compile main.py database.py` and test the feature manually.

For example, adding an account email would require a new database column, an updated INSERT function, an input field on signup, validation, and updated documentation.
