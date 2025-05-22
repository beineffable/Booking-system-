-- Initialize database schema for Training Club Fitness Platform

-- Create tables

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role ENUM('member', 'trainer', 'admin') NOT NULL DEFAULT 'member',
    status ENUM('active', 'inactive', 'pending') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Membership types
CREATE TABLE IF NOT EXISTS membership_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    duration_days INT NOT NULL,
    class_credits INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Memberships
CREATE TABLE IF NOT EXISTS memberships (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    membership_type_id INT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status ENUM('active', 'expired', 'cancelled') NOT NULL DEFAULT 'active',
    payment_status ENUM('paid', 'pending', 'failed') NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (membership_type_id) REFERENCES membership_types(id)
);

-- Class types
CREATE TABLE IF NOT EXISTS class_types (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    duration_minutes INT NOT NULL,
    default_capacity INT NOT NULL,
    color VARCHAR(7) DEFAULT '#9ed6fe',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Classes
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_type_id INT NOT NULL,
    trainer_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    capacity INT NOT NULL,
    location VARCHAR(255) DEFAULT 'Main Studio',
    status ENUM('scheduled', 'cancelled', 'completed') NOT NULL DEFAULT 'scheduled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (class_type_id) REFERENCES class_types(id),
    FOREIGN KEY (trainer_id) REFERENCES users(id)
);

-- Bookings
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    class_id INT NOT NULL,
    status ENUM('booked', 'cancelled', 'attended', 'no_show') NOT NULL DEFAULT 'booked',
    credits_used INT DEFAULT 0,
    check_in_time DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (class_id) REFERENCES classes(id),
    UNIQUE KEY (user_id, class_id)
);

-- Credits
CREATE TABLE IF NOT EXISTS credits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount INT NOT NULL,
    transaction_type ENUM('earned', 'spent', 'gifted', 'received', 'expired') NOT NULL,
    description TEXT,
    reference_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Referrals
CREATE TABLE IF NOT EXISTS referrals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    referrer_id INT NOT NULL,
    referred_email VARCHAR(255) NOT NULL,
    status ENUM('pending', 'registered', 'completed', 'expired') NOT NULL DEFAULT 'pending',
    completed_at DATETIME,
    credits_awarded INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (referrer_id) REFERENCES users(id)
);

-- Photos
CREATE TABLE IF NOT EXISTS photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    uploaded_by INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    access_code VARCHAR(20) NOT NULL,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'CHF',
    payment_method ENUM('stripe', 'twint', 'other') NOT NULL,
    payment_status ENUM('pending', 'completed', 'failed', 'refunded') NOT NULL,
    transaction_id VARCHAR(255),
    reference_type ENUM('membership', 'class', 'product', 'other') NOT NULL,
    reference_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert seed data

-- Admin user (password: Admin123!)
INSERT INTO users (email, password_hash, first_name, last_name, role, status)
VALUES ('admin@trainingclub.ch', '$2b$12$1NyQcwAhO7Tg3dRLb5NpCODLxaC1zYS9rXQMYKFRP0sUvnzNkn2Aq', 'Admin', 'User', 'admin', 'active');

-- Membership types
INSERT INTO membership_types (name, description, price, duration_days, class_credits)
VALUES 
('Standard', 'Regular membership with access to all standard classes', 120.00, 30, 8),
('Premium', 'Premium membership with access to all classes including special events', 180.00, 30, 12),
('Annual Standard', 'Annual standard membership with discounted rate', 1200.00, 365, 100),
('Annual Premium', 'Annual premium membership with discounted rate and priority booking', 1800.00, 365, 150);

-- Class types
INSERT INTO class_types (name, description, duration_minutes, default_capacity, color)
VALUES 
('HIIT', 'High-Intensity Interval Training', 45, 20, '#f16c13'),
('Yoga', 'Relaxing and strengthening yoga session', 60, 15, '#9ed6fe'),
('Strength', 'Strength and conditioning workout', 60, 12, '#c8b4a3'),
('Cardio', 'Cardiovascular workout', 45, 20, '#c9dee7');
