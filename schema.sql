-- Database Schema for Student Management System
-- Run this SQL in phpMyAdmin or MySQL to create the database and table

-- Create database if not exists
CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Create students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    age INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample data (optional)
-- INSERT INTO students (name, email, age) VALUES 
-- ('John Doe', 'john@example.com', 20),
-- ('Jane Smith', 'jane@example.com', 19);
