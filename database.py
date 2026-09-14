import random
import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


def generate_account_number():
    # keep generating a random 6 digit number until we find one that
    # isn't already used in the accounts table
    conn = get_connection()
    cursor = conn.cursor()
    while True:
        acc_no = str(random.randint(100000, 999999))
        cursor.execute("SELECT acc_no FROM accounts WHERE acc_no = %s", (acc_no,))
        if cursor.fetchone() is None:
            break
    cursor.close()
    conn.close()
    return acc_no


def create_account(name, pin, phone, initial_deposit):
    acc_no = generate_account_number()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO accounts (acc_no, name, pin, phone, balance) VALUES (%s, %s, %s, %s, %s)",
        (acc_no, name, pin, phone, initial_deposit)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return acc_no


def delete_account(acc_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE acc_no = %s", (acc_no,))
    conn.commit()
    deleted = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return deleted


def account_exists(acc_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT acc_no FROM accounts WHERE acc_no = %s", (acc_no,))
    found = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return found


def verify_customer_login(acc_no, pin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT acc_no FROM accounts WHERE acc_no = %s AND pin = %s", (acc_no, pin))
    ok = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return ok


def get_phone_for_account(acc_no, phone):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM accounts WHERE acc_no = %s AND phone = %s", (acc_no, phone))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None


def change_pin(acc_no, new_pin):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET pin = %s WHERE acc_no = %s", (new_pin, acc_no))
    conn.commit()
    changed = cursor.rowcount > 0
    cursor.close()
    conn.close()
    return changed


def verify_admin_login(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM admins WHERE username = %s AND password = %s", (username, password))
    ok = cursor.fetchone() is not None
    cursor.close()
    conn.close()
    return ok


def get_account_details(acc_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT acc_no, name, balance, created_at FROM accounts WHERE acc_no = %s", (acc_no,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def deposit(acc_no, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s", (amount, acc_no))
    _log_transaction(cursor, acc_no, "DEPOSIT", amount, None)
    conn.commit()
    cursor.close()
    conn.close()


def withdraw(acc_no, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (acc_no,))
    balance = cursor.fetchone()[0]

    if balance < amount:
        cursor.close()
        conn.close()
        return False, "Insufficient balance"

    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s", (amount, acc_no))
    _log_transaction(cursor, acc_no, "WITHDRAW", amount, None)
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Withdrawal successful"


def transfer(from_acc, to_acc, amount):
    if from_acc == to_acc:
        return False, "Cannot transfer to your own account"

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT acc_no FROM accounts WHERE acc_no = %s", (to_acc,))
    if cursor.fetchone() is None:
        cursor.close()
        conn.close()
        return False, "Recipient account number does not exist"

    cursor.execute("SELECT balance FROM accounts WHERE acc_no = %s", (from_acc,))
    balance = cursor.fetchone()[0]
    if balance < amount:
        cursor.close()
        conn.close()
        return False, "Insufficient balance"

    cursor.execute("UPDATE accounts SET balance = balance - %s WHERE acc_no = %s", (amount, from_acc))
    cursor.execute("UPDATE accounts SET balance = balance + %s WHERE acc_no = %s", (amount, to_acc))
    _log_transaction(cursor, from_acc, "TRANSFER OUT", amount, to_acc)
    _log_transaction(cursor, to_acc, "TRANSFER IN", amount, from_acc)
    conn.commit()
    cursor.close()
    conn.close()
    return True, "Transfer successful"


def _log_transaction(cursor, acc_no, txn_type, amount, related_acc):
    cursor.execute(
        "INSERT INTO transactions (acc_no, txn_type, amount, related_acc) VALUES (%s, %s, %s, %s)",
        (acc_no, txn_type, amount, related_acc)
    )


def get_transaction_history(acc_no):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT txn_type, amount, related_acc, txn_time FROM transactions "
        "WHERE acc_no = %s ORDER BY txn_time DESC",
        (acc_no,)
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_accounts():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT acc_no, name, balance, created_at FROM accounts ORDER BY created_at DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_account_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(balance), 0) FROM accounts")
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT acc_no, txn_type, amount, related_acc, txn_time "
        "FROM transactions ORDER BY txn_time DESC"
    )
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows
