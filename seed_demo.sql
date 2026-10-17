-- seed_demo.sql
-- Demo accounts for SecureBank (safe for classroom demos)
-- Run: mysql -u <user> -p bank_db < seed_demo.sql

INSERT INTO accounts (acc_no, name, pin, phone, balance, created_at) VALUES
('100001', 'Alice', '1234', '9876543210', 1000.00, NOW()),
('100002', 'Bob',  '4321', '9123456789', 500.00, NOW());
