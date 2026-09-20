-- Expense Tracker database
-- Run this file in MySQL Workbench / MySQL command line (optional).
-- The app also creates these tables automatically when it starts.

CREATE DATABASE IF NOT EXISTS expense_tracker_db;
USE expense_tracker_db;

-- Registered users (password is stored as a salted hash, never as plain text)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Daily (variable) expenses. Each row belongs to one user.
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    expense_date DATE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    description VARCHAR(255),
    CONSTRAINT fk_expenses_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- One budget per user per month (month_year looks like 2026-09)
CREATE TABLE IF NOT EXISTS budgets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    month_year VARCHAR(7) NOT NULL,
    budget_amount DECIMAL(10,2) NOT NULL,
    UNIQUE KEY unique_user_month (user_id, month_year),
    CONSTRAINT fk_budgets_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Fixed (recurring) expenses. Each row belongs to one user.
CREATE TABLE IF NOT EXISTS recurring_expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    expense_name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    due_day INT,
    frequency VARCHAR(20),
    CONSTRAINT fk_recurring_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
