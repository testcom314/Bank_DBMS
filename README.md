# SecureBank

SecureBank is a small CustomTkinter and MySQL banking application. It includes customer account creation, customer sign in, deposits, withdrawals, transfers, transaction history, and a direct admin workspace.

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

The interface opens directly in fullscreen mode. The first screen has exactly three choices: Login, Sign up, and Exit. To enter the admin workspace, use Login with `admin` and `admin123`, which are defined at the top of `main.py`. Customer actions no longer open separate popup windows.

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

## Important note

This is an educational project. The current database stores PINs and admin passwords as plain text and the admin workspace is intentionally direct-access to match the requested classroom workflow. Do not use it for real financial data without authentication, hashing, authorization, audit logging, and stronger database error handling.
