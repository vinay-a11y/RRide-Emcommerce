-- Seed Data for Bike Shop Database
USE bike_shop;

-- Insert Bikes
INSERT IGNORE INTO bikes (id, brand, model, variant) VALUES
('bike-ktm-1', 'KTM', 'Duke 390', '2024'),
('bike-ktm-2', 'KTM', 'Duke 390', '2023'),
('bike-ktm-3', 'KTM', 'Duke 250', '2024'),
('bike-ktm-4', 'KTM', 'RC 390', '2024'),
('bike-ktm-5', 'KTM', 'Adventure 390', '2024'),
('bike-bmw-1', 'BMW', 'G 310 R', '2024'),
('bike-bmw-2', 'BMW', 'G 310 GS', '2024'),
('bike-bmw-3', 'BMW', 'S 1000 RR', '2024'),
('bike-royal-1', 'Royal Enfield', 'Classic 350', '2024'),
('bike-royal-2', 'Royal Enfield', 'Meteor 350', '2024'),
('bike-royal-3', 'Royal Enfield', 'Himalayan', '2024'),
('bike-royal-4', 'Royal Enfield', 'Interceptor 650', '2024'),
('bike-yamaha-1', 'Yamaha', 'MT-15', '2024'),
('bike-yamaha-2', 'Yamaha', 'R15 V4', '2024'),
('bike-yamaha-3', 'Yamaha', 'FZ-S', '2024'),
('bike-yamaha-4', 'Yamaha', 'YZF R1', '2024');

-- Insert Product Brands
INSERT IGNORE INTO product_brands (id, name, logo) VALUES
('brand-1', 'Akrapovic', 'https://banner2.cleanpng.com/20180425/dvw/avgvk6yzo.webp'),
('brand-2', 'Motul', 'https://1000logos.net/wp-content/uploads/2023/09/Motul-Logo.png'),
('brand-3', 'Brembo', 'https://logos-world.net/wp-content/uploads/2023/11/Brembo-Logo.png'),
('brand-4', 'Michelin', 'https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Michelin_logo.svg/2048px-Michelin_logo.svg.png'),
('brand-5', 'Alpinestars', 'https://logos-world.net/wp-content/uploads/2022/04/Alpinestars-Logo.png'),
('brand-6', 'AGV', 'https://logodownload.org/wp-content/uploads/2022/01/agv-logo-0.png'),
('brand-7', 'K&N', 'https://1000logos.net/wp-content/uploads/2022/04/KN-Logo.png'),
('brand-8', 'DID', 'https://www.didchain.com/wp-content/themes/did-chain/assets/images/logo.png'),
('brand-9', 'Rizoma', 'https://www.rizomausa.com/wp-content/uploads/2020/02/logo_rizoma.png'),
('brand-10', 'Philips', 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/52/Philips_logo_new.svg/2560px-Philips_logo_new.svg.png');

-- Insert Spare Categories
INSERT IGNORE INTO spare_categories (id, name, slug, description) VALUES
('cat-1', 'Performance', 'performance', 'High performance upgrades for maximum power'),
('cat-2', 'Safety Gear', 'safety-gear', 'Protective equipment for riders'),
('cat-3', 'Pro Spares', 'pro-spares', 'Professional replacement parts'),
('cat-4', 'Accessories', 'accessories', 'Add-ons and customization parts');

-- Insert Products (SPARES - bike-specific replacement parts)
INSERT IGNORE INTO products (id, name, brand_id, spare_category_id, product_type, price, original_price, description, images, specifications, stock, rating, reviews_count, is_best_seller, is_new_arrival, installation_difficulty, warranty) VALUES
-- Performance Spares
('prod-1', 'Performance Exhaust System', 'brand-1', 'cat-1', 'spare', 25999.00, 32999.00, 'Premium titanium exhaust system for enhanced performance and sound. Direct fit for KTM Duke 390', 
'["https://images.unsplash.com/photo-1620937843955-a177ceba979e?crop=entropy&cs=srgb&fm=jpg&q=85"]', 
'{"material": "Titanium", "weight": "2.5kg", "power_gain": "+5HP", "sound_level": "95dB"}', 
15, 4.8, 124, TRUE, FALSE, 'Hard', '2 Years'),

('prod-2', 'Racing Brake Pads', 'brand-3', 'cat-1', 'spare', 3499.00, 4299.00, 'High performance brake pads for superior stopping power. Compatible with BMW G310 series',
'["https://images.unsplash.com/photo-1761583780521-7723c3569361?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"material": "Ceramic", "type": "Front", "temperature_range": "0-800°C"}',
60, 4.9, 203, TRUE, FALSE, 'Medium', '1 Year'),

-- Pro Spares
('prod-3', 'Chain & Sprocket Kit', 'brand-8', 'cat-3', 'spare', 4599.00, 5999.00, 'Heavy duty chain and sprocket kit for long lasting performance',
'["https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"chain_type": "O-Ring", "links": "120", "material": "Steel"}',
45, 4.6, 67, FALSE, FALSE, 'Medium', '6 Months'),

('prod-4', 'Engine Oil Filter', 'brand-7', 'cat-3', 'spare', 599.00, 799.00, 'High flow engine oil filter for better lubrication',
'["https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"type": "Cartridge", "filtration": "99%", "capacity": "Standard"}',
200, 4.4, 78, FALSE, FALSE, 'Easy', '3 Months'),

('prod-5', 'Air Filter High Flow', 'brand-7', 'cat-1', 'spare', 2499.00, 3199.00, 'Performance air filter for increased airflow and power',
'["https://images.unsplash.com/photo-1633281256183-c0f106f70d76?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"type": "High Flow", "cleaning": "Washable", "airflow_increase": "+15%"}',
80, 4.7, 156, TRUE, TRUE, 'Easy', '1 Year'),

-- ACCESSORIES (universal or bike-agnostic items)
('prod-6', 'Premium Full Face Helmet', 'brand-6', 'cat-2', 'accessory', 18999.00, 24999.00, 'DOT certified full face helmet with aerodynamic design. Universal size',
'["https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"shell": "Carbon Fiber", "weight": "1.3kg", "certification": "DOT, ECE"}',
30, 4.7, 89, TRUE, TRUE, 'Easy', '1 Year'),

('prod-7', 'Riding Jacket', 'brand-5', 'cat-2', 'accessory', 12999.00, 16999.00, 'All-weather riding jacket with CE certified armor. Universal fit',
'["https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"material": "Textile", "armor": "CE Level 2", "waterproof": "Yes"}',
25, 4.8, 112, TRUE, FALSE, 'Easy', '1 Year'),

('prod-8', 'LED Headlight Bulb', 'brand-10', 'cat-4', 'accessory', 1299.00, 1799.00, 'High intensity LED headlight bulb with white light. Universal H4 fitting',
'["https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"brightness": "6000K", "power": "30W", "type": "H4"}',
100, 4.5, 156, FALSE, TRUE, 'Easy', '1 Year'),

('prod-9', 'Bar End Mirrors', 'brand-9', 'cat-4', 'accessory', 2999.00, 3999.00, 'CNC machined aluminum bar end mirrors with wide angle view. Universal fit',
'["https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"material": "Aluminum", "adjustable": "Yes", "color": "Black"}',
35, 4.6, 42, FALSE, TRUE, 'Easy', '2 Years'),

('prod-10', 'Mobile Phone Holder', 'brand-9', 'cat-4', 'accessory', 1499.00, 1999.00, 'Universal mobile phone holder with 360° rotation and secure grip',
'["https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"max_phone_size": "6.7 inch", "rotation": "360°", "material": "Aluminum"}',
150, 4.3, 234, FALSE, FALSE, 'Easy', '6 Months'),

('prod-11', 'USB Charger Port', 'brand-10', 'cat-4', 'accessory', 899.00, 1299.00, 'Waterproof USB charger port for bikes. Universal installation',
'["https://images.unsplash.com/photo-1649027421785-6827863f0891?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"output": "5V 2.4A", "ports": "Dual USB", "waterproof": "IP65"}',
200, 4.4, 189, FALSE, FALSE, 'Medium', '1 Year'),

('prod-12', 'Riding Gloves', 'brand-5', 'cat-2', 'accessory', 2999.00, 3999.00, 'Premium leather riding gloves with knuckle protection',
'["https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"material": "Leather", "protection": "Knuckle Guard", "touchscreen": "Yes"}',
75, 4.7, 145, TRUE, FALSE, 'Easy', '6 Months'),

('prod-13', 'Riding Boots', 'brand-5', 'cat-2', 'accessory', 8999.00, 11999.00, 'Waterproof riding boots with ankle protection',
'["https://images.unsplash.com/photo-1611004061856-ccc3cbe944b2?crop=entropy&cs=srgb&fm=jpg&q=85"]',
'{"material": "Leather", "waterproof": "Yes", "protection": "Ankle + Toe"}',
40, 4.6, 98, FALSE, TRUE, 'Easy', '1 Year');

-- Insert Product-Bike Compatibility (for SPARES only - accessories are universal)
INSERT IGNORE INTO product_bike_compatibility (product_id, bike_id) VALUES
-- Exhaust System (prod-1)
('prod-1', 'bike-ktm-1'),
('prod-1', 'bike-ktm-2'),
-- Racing Brake Pads (prod-2)
('prod-2', 'bike-bmw-1'),
('prod-2', 'bike-bmw-2'),
-- Chain & Sprocket (prod-3)
('prod-3', 'bike-ktm-3'),
('prod-3', 'bike-yamaha-1'),
('prod-3', 'bike-yamaha-2'),
-- Oil Filter (prod-4)
('prod-4', 'bike-royal-3'),
('prod-4', 'bike-royal-4'),
-- Air Filter (prod-5)
('prod-5', 'bike-ktm-1'),
('prod-5', 'bike-ktm-2'),
('prod-5', 'bike-ktm-3');
