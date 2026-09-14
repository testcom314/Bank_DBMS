# SecureBank

[![Author: Adithya S (testcom314)](https://img.shields.io/badge/author-Adithya%20S%20%28testcom314%29-blue?style=flat-square)](https://github.com/testcom314) [![License: MIT](https://img.shields.io/badge/license-MIT-brightgreen?style=flat-square)](LICENSE)

SecureBank is a small CustomTkinter and MySQL banking application. It includes customer account creation, customer sign in, deposits, withdrawals, transfers, transaction history, and a direct admin workspace for quick review and demo.

## Student project note & executive summary

This repository contains my 12th‑grade final project: a small classroom banking application (SecureBank) built with CustomTkinter and MySQL. The goal of the project is to demonstrate a simple three‑tier desktop application (UI, data access, and storage) so students can study and modify the core concepts.

This repository is intended as a starter template and learning tool for 12th‑grade projects. It is designed to be easy to run and modify in the classroom. Security and robustness are intentionally simplified for teaching: PINs and the admin password are stored in plain text and some production practices are omitted. You are encouraged to fork this project, experiment, and publish your own improvements or versions. Please keep the MIT license when redistributing.

## Quick Start - run in 5 minutes

1. Copy the example env file and edit it with your MySQL credentials:
   - cp .env.example .env  (then edit .env)
2. Create the database schema:
   - mysql -u root -p < setup_database.sql
3. Load the demo data (included in this repo):
   - mysql -u root -p bank_db < seed_demo.sql
4. Install Python dependencies and run the app:
   - pip install -r requirements.txt
   - python main.py

Notes:
- Copy `.env.example` to `.env` and replace the values, or set equivalent environment variables; do not commit `.env` with real credentials.
- If you keep `config.py` instead of using `.env`, update its values to match your MySQL setup.

The interface opens directly in fullscreen mode. The first screen has exactly three choices: Login, Sign up, and Exit. To enter the admin workspace, use Login with `admin` and `admin123`, which are intentionally simple to make classroom demos quick.

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

## Quick prerequisites / environment

- Python 3.10+ recommended
- MySQL 8.0+ (or a compatible MySQL server)
- Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Example environment configuration (recommended)

Before running the app, either edit `config.py` or use an environment file with the connection values. Example `.env` variables:

```text
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
MYSQL_DATABASE=bank_db
```

Copy `.env.example` to `.env` and replace the values, or set equivalent environment variables; do not commit `.env` with real credentials.

## Quick database setup (mysql CLI)

Create the database and run the schema with the MySQL command line:
```bash
mysql -u root -p < setup_database.sql
```

Load provided demo rows (seed_demo.sql) to make demos repeatable:
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

## For teachers

This repository is designed as a starter template and learning tool for 12th‑grade projects. It is suitable for short classroom labs or final project demonstrations. Suggested teacher guidance:

- Learning goals: students should understand the UI → data layer → DB flow, parameterized SQL, and simple GUI event handling.
- Setup for classroom demos:
  - Load the demo rows before the lab: `mysql -u root -p bank_db < seed_demo.sql`.
  - Recommend each student use a local MySQL instance or provide a pre-configured environment.
- Assessment suggestions: focus on functionality (signup, login, deposit/withdraw/transfer), code understanding (ability to trace and explain the flow), and small improvements (input validation, defensive checks).

Please keep the MIT license when reusing or redistributing this repository.

## Notes for future readers / contributors

If you plan to reuse or extend this project, these small changes make it easier for others:

- Move DB credentials out of `config.py` and read them from environment variables.
- Add a `SEED.sql` for demo accounts and a short `DEMO.md` that lists demo credentials.
- Add a few screenshots and an ER diagram to make the README self-contained.

## License

Licensed under the MIT License (see the LICENSE file). Please retain the license and copyright notice when redistributing; a brief credit to "Adithya S (testcom314)" in the README or About page is appreciated.

## Important note

This is an educational project. The current database stores PINs and admin passwords as plain text and the admin workspace is intentionally direct-access to match the requested classroom workflow. Use this repo as a learning tool and do not deploy it to production without addressing the security issues described in TECHNICAL_ARCHITECTURE.md.
