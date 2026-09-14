# SecureBank

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

## How to study this project (for students)

If you're using this repository for classwork or a final demo, here's a simple study path that focuses on concepts first and code second. The notes below are written plainly so you can adapt them into your own words for reports and presentations.

1. Start with CONCEPTS.md — read this first to learn the key ideas and terminology used across the project. Its a short, high-level summary and the fastest way to get oriented.
2. Walk through STUDENT_GUIDE.md next — it explains the GUI flow, common Python/Tkinter patterns (callbacks, closures, pack), and shows example code snippets you should understand for viva questions.
3. Read TECHNICAL_ARCHITECTURE.md for the system-level view: how the UI, data layer, and MySQL fit together, plus function contracts and known risks.
4. Run the app locally (see Run it). Interact with the UI: create an account, deposit, withdraw, transfer, and use the admin tabs. Hands-on use makes the concepts concrete.
5. Open the code: read `main.py` and `database.py` side-by-side. Try to trace one full action (for example, Transfer): which UI callback runs, what validation happens, which database functions are called, and what SQL executes.
6. Try a small change: add a print statement, change a label, or tweak validation. Re-run and observe the effect. Small edits are the best way to learn.
7. Prepare for your demo: choose 3–4 scenarios to show (signup → login → deposit; withdrawal with insufficient funds; transfer between accounts; admin account listing). Rehearse the steps and the expected results so you can demonstrate reliably.

Notes to avoid "AI-sounding" phrasing in reports:
- Write explanations in your own words and use short, concrete sentences.
- Include screenshots and short captions showing the exact UI state youll demo.
- Cite specific files and line numbers when you explain code behavior (for example: `main.py` lines 175–187 handle the login flow).

## Important note

This is an educational project. The current database stores PINs and admin passwords as plain text and the admin workspace is intentionally direct-access to match the requested classroom workflow. Do not use this code as-is for any real banking or production system.
