-- Bike Shop E-Commerce Database Schema
-- MySQL 8.0+ / MariaDB 10.11+

USE bike_shop;

-- ============ USERS TABLE ============
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(36) PRIMARY KEY,
    mobile VARCHAR(20) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mobile (mobile)
);

-- ============ BIKES TABLE ============
CREATE TABLE IF NOT EXISTS bikes (
    id VARCHAR(36) PRIMARY KEY,
    brand VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    variant VARCHAR(100) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_bike (brand, model, variant),
    INDEX idx_brand (brand),
    INDEX idx_model (model)
);

-- ============ PRODUCT BRANDS TABLE ============
CREATE TABLE IF NOT EXISTS product_brands (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    logo VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
);

-- ============ SPARE CATEGORIES TABLE ============
CREATE TABLE IF NOT EXISTS spare_categories (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    image VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_slug (slug)
);

-- ============ PRODUCTS TABLE ============
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    brand_id VARCHAR(36),
    spare_category_id VARCHAR(36),
    product_type ENUM('spare', 'accessory') NOT NULL DEFAULT 'spare',
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    description LONGTEXT,
    images JSON,
    specifications JSON,
    stock INT DEFAULT 0,
    rating DECIMAL(3, 2) DEFAULT 4.5,
    reviews_count INT DEFAULT 0,
    is_best_seller BOOLEAN DEFAULT FALSE,
    is_new_arrival BOOLEAN DEFAULT FALSE,
    installation_difficulty VARCHAR(50) DEFAULT 'Medium',
    warranty VARCHAR(100) DEFAULT '1 Year',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES product_brands(id) ON DELETE SET NULL,
    FOREIGN KEY (spare_category_id) REFERENCES spare_categories(id) ON DELETE SET NULL,
    INDEX idx_brand (brand_id),
    INDEX idx_category (spare_category_id),
    INDEX idx_product_type (product_type),
    INDEX idx_price (price),
    INDEX idx_best_seller (is_best_seller)
);

-- ============ PRODUCT BIKE COMPATIBILITY TABLE ============
CREATE TABLE IF NOT EXISTS product_bike_compatibility (
    product_id VARCHAR(36) NOT NULL,
    bike_id VARCHAR(36) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id, bike_id),
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (bike_id) REFERENCES bikes(id) ON DELETE CASCADE,
    INDEX idx_bike (bike_id)
);

-- ============ CARTS TABLE ============
CREATE TABLE IF NOT EXISTS carts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL UNIQUE,
    items JSON NOT NULL DEFAULT '[]',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id)
);

-- ============ ORDERS TABLE ============
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    items JSON NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address JSON,
    payment_method VARCHAR(50),
    payment_status ENUM('pending', 'completed', 'failed') DEFAULT 'pending',
    order_status ENUM('placed', 'confirmed', 'processing', 'pickup', 'delivery', 'delivered', 'cancelled') DEFAULT 'placed',
    razorpay_order_id VARCHAR(100),
    razorpay_payment_id VARCHAR(100),
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_status (order_status),
    INDEX idx_created (created_at)
);
