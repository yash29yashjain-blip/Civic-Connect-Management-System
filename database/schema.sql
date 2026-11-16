
CREATE DATABASE IF NOT EXISTS civic_connect
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE civic_connect;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('citizen', 'officer', 'admin') NOT NULL DEFAULT 'citizen',
    phone VARCHAR(25),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    department_id INT NOT NULL,
    designation VARCHAR(100) DEFAULT 'Public Service Officer',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);

CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    citizen_id INT NOT NULL,
    department_id INT,
    assigned_officer_id INT,
    title VARCHAR(180) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    location VARCHAR(255),
    priority ENUM('Low', 'Medium', 'High', 'Urgent')
        NOT NULL DEFAULT 'Medium',
    status ENUM(
        'Submitted',
        'Assigned',
        'In Progress',
        'Resolved',
        'Rejected'
    ) NOT NULL DEFAULT 'Submitted',
    officer_notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (citizen_id) REFERENCES users(id),
    FOREIGN KEY (department_id) REFERENCES departments(id)
        ON DELETE SET NULL,
    FOREIGN KEY (assigned_officer_id) REFERENCES users(id)
        ON DELETE SET NULL,
    INDEX idx_complaints_status (status),
    INDEX idx_complaints_citizen (citizen_id),
    INDEX idx_complaints_department (department_id)
);

CREATE TABLE IF NOT EXISTS resources (
    id INT AUTO_INCREMENT PRIMARY KEY,
    department_id INT NOT NULL,
    name VARCHAR(120) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    quantity INT NOT NULL DEFAULT 0,
    available_quantity INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
        ON DELETE CASCADE,
    CHECK (quantity >= 0),
    CHECK (available_quantity >= 0),
    CHECK (available_quantity <= quantity)
);
