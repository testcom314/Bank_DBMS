-- Run this once in MySQL Workbench (or the mysql CLI) before starting the app.

CREATE DATABASE IF NOT EXISTS bank_db;
USE bank_db;

CREATE TABLE IF NOT EXISTS accounts (
    acc_no VARCHAR(6) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    pin VARCHAR(4) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    balance DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    acc_no VARCHAR(6) NOT NULL,
    txn_type VARCHAR(20) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    related_acc VARCHAR(6),
    txn_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (acc_no) REFERENCES accounts(acc_no) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS admins (
    username VARCHAR(50) PRIMARY KEY,
    password VARCHAR(50) NOT NULL
);

-- default admin login, change the password if you want
INSERT INTO admins (username, password)
SELECT 'admin', 'admin123'
WHERE NOT EXISTS (SELECT 1 FROM admins WHERE username = 'admin');

-- If the database was created before phone support was added, run this once:
-- ALTER TABLE accounts ADD COLUMN phone VARCHAR(20) NOT NULL DEFAULT '' AFTER pin;
