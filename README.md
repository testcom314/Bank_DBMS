# SecureBank

[![Author: Adithya S (testcom314)](https://img.shields.io/badge/author-Adithya%20S%20%28testcom314%29-blue?style=flat-square)](https://github.com/testcom314) [![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

SecureBank is a small CustomTkinter and MySQL banking application. It includes customer account creation, customer sign in, deposits, withdrawals, transfers, transaction history, and a direct admin workspace for classroom use.

## Run it

1. Install the dependencies:

```text
pip install -r requirements.txt
```

2. Run `setup_database.sql` in MySQL Workbench or the MySQL command line.

3. Update the credentials in `config.py`.

4. Start the application:

```text
python main.py
```

The interface opens directly in fullscreen mode. The first screen has exactly three choices: Login, Sign up, and Exit. To enter the admin workspace, use Login with `admin` and `admin123`, which are provided for classroom demos.

Existing databases need the phone-column migration in `setup_database.sql` before phone signup and Forgot PIN can work.

## Files

| File | Purpose |
|---|---|
| `main.py` | Single-window CustomTkinter interface and input validation |
| `database.py` | MySQL queries and banking operations |
| `config.py` | MySQL connection configuration |
| `setup_database.sql` | Database and table setup |
| `CONCEPTS.md` | Short reference to the main programming concepts |
| `STUDENT_GUIDE.md` | Detailed teaching guide with code explanations and viva questions |
| `TECHNICAL_ARCHITECTURE.md` | Technical view of modules, data flow, database contracts, and testing |

## Student project note & executive summary

This repository contains my 12th‑grade final project: a small classroom banking application (SecureBank) built with CustomTkinter and MySQL. The goal of the project is to demonstrate a simple three‑layer desktop architecture, basic GUI programming patterns, and parameterized SQL operations. I am keeping the repository public so other students and developers can read the code, reuse ideas, and learn from the implementation.

## Quick prerequisites / environment

- Python 3.10+ recommended
- MySQL 8.0+ (or a compatible MySQL server)
- Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Example environment configuration (recommended)

Before running the app, either edit `config.py` or create an environment file with the connection values. Example `.env` / variables:

```text
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=bank_db
```

If you keep `config.py` as-is for classroom demos, remember to remove any real credentials before publishing.

## Quick database setup (mysql CLI)

Create the database and run the schema with the MySQL command line:
```bash
mysql -u root -p < setup_database.sql
```

Optional: a tiny seed file helps make demos repeatable. Create `seed_demo.sql` with entries like:
```sql
INSERT INTO accounts (acc_no, name, pin, phone, balance) VALUES
('100001', 'Alice Student', '1234', '9876543210', 1000.00),
('100002', 'Bob Learner',  '4321', '9123456789', 500.00);
```
Then load it with:
```bash
mysql -u root -p bank_db < seed_demo.sql
```

## Demo checklist (use this for timed presentations)

Pick 3–4 of these scenarios and rehearse them in order:

- Signup → Login → Deposit
  1. Click Sign up, fill name/phone/4‑digit PIN, deposit >= 500.
  2. Note the generated account number.
  3. Login and deposit an amount; check balance and history.

- Withdrawal with insufficient funds
  1. Login to an account with a small balance.
  2. Attempt to withdraw more than the balance.
  3. Confirm the “Insufficient balance” message and unchanged balance.

- Transfer and admin review
  1. Transfer from account A to account B.
  2. Check both accounts show TRANSFER OUT / TRANSFER IN in their histories.
  3. Login as admin (admin / admin123) and open All transactions to review logs.

Rehearse the mouse clicks and expected messages to avoid surprises during the oral demo.

## How to study the code (short path for exam prep)

1. Read `CONCEPTS.md` for the core ideas and terminology.  
2. Read `STUDENT_GUIDE.md` for code examples and GUI patterns you should understand.  
3. Read `TECHNICAL_ARCHITECTURE.md` for the system-level view and function contracts.  
4. Trace one operation end-to-end in code (for example: Transfer). Identify the UI callback in `main.py`, the validation, and the `database.py` functions that run.  
5. Make a tiny change (label text or print statement), run the app again, and observe the result — hands-on edits help you remember the flow.

## Minimal testing idea

If you want to add a simple automated check, create `tests/test_db.py` and run with pytest (use a disposable test database):

```python
# tests/test_db.py
import database as db

def test_create_and_deposit():
    acc = db.create_account("Test User", "9999", "9000000000", 600.0)
    db.deposit(acc, 400.0)
    details = db.get_account_details(acc)
    assert details[2] == 1000.0  # balance column
```

Do not run tests against a production database. Use a dedicated test DB instance.

## Troubleshooting (common issues)

- ImportError for customtkinter: make sure you installed the package and are using the same Python interpreter.  
- MySQL connection refused: check that the server is running and credentials in `config.py` are correct.  
- Missing phone column errors: if you are reusing an old database, run the migration in `setup_database.sql` to add the phone column.

## Notes for future readers / contributors

If you plan to reuse or extend this project, these small changes make it easier for others:

- Move DB credentials out of `config.py` and read them from environment variables.
- Add a `SEED.sql` for demo accounts and a short `DEMO.md` that lists demo credentials.
- Add a few screenshots and an ER diagram to make the README self-contained.

## License

Licensed under the MIT License (see the LICENSE file). Please retain the license and copyright notice when redistributing; a brief credit to "Adithya S (testcom314)" in the README or About page is appreciated.

## About the credit badges

Two small badges near the top of this README point to my GitHub profile and the LICENSE file. They are a quick, friendly way to see authorship and license information; the legal requirement for attribution is the license text itself.

## Important note

This is an educational project. The current database stores PINs and admin passwords as plain text and the admin workspace is intentionally direct-access to match the requested classroom workflow. Do not use this code as-is for any real banking or production system.
