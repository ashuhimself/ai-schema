-- Sample data for testing Warehouse Copilot
-- This inserts realistic test data into the e-commerce schema

-- Insert categories
INSERT INTO categories (id, name, description, parent_id) VALUES
(1, 'Electronics', 'Electronic devices and gadgets', NULL),
(2, 'Clothing', 'Apparel and fashion items', NULL),
(3, 'Books', 'Books and publications', NULL),
(4, 'Home & Garden', 'Home improvement and gardening', NULL),
(5, 'Smartphones', 'Mobile phones and accessories', 1),
(6, 'Laptops', 'Computers and laptops', 1),
(7, 'Men''s Clothing', 'Men''s apparel', 2),
(8, 'Women''s Clothing', 'Women''s apparel', 2),
(9, 'Fiction', 'Fiction books', 3),
(10, 'Non-Fiction', 'Non-fiction books', 3);

-- Insert users
INSERT INTO users (name, email, phone, date_of_birth, created_at) VALUES
('John Doe', 'john.doe@email.com', '+1-555-0101', '1985-03-15', '2023-01-15 10:30:00'),
('Jane Smith', 'jane.smith@email.com', '+1-555-0102', '1990-07-22', '2023-01-20 14:45:00'),
('Bob Johnson', 'bob.johnson@email.com', '+1-555-0103', '1982-11-08', '2023-02-01 09:15:00'),
('Alice Brown', 'alice.brown@email.com', '+1-555-0104', '1995-04-30', '2023-02-10 16:20:00'),
('Charlie Wilson', 'charlie.wilson@email.com', '+1-555-0105', '1988-09-12', '2023-02-15 11:00:00'),
('Diana Miller', 'diana.miller@email.com', '+1-555-0106', '1992-12-03', '2023-02-20 13:30:00'),
('Frank Davis', 'frank.davis@email.com', '+1-555-0107', '1987-06-18', '2023-03-01 10:45:00'),
('Grace Taylor', 'grace.taylor@email.com', '+1-555-0108', '1993-02-25', '2023-03-05 15:10:00'),
('Henry Anderson', 'henry.anderson@email.com', '+1-555-0109', '1984-10-14', '2023-03-10 12:20:00'),
('Ivy Thompson', 'ivy.thompson@email.com', '+1-555-0110', '1991-08-07', '2023-03-15 14:55:00');

-- Insert products
INSERT INTO products (name, description, price, category_id, stock_quantity, created_at) VALUES
('iPhone 15 Pro', 'Latest Apple smartphone with advanced features', 999.99, 5, 50, '2023-01-10'),
('Samsung Galaxy S24', 'High-end Android smartphone', 899.99, 5, 35, '2023-01-12'),
('MacBook Air M3', 'Lightweight laptop with M3 chip', 1299.99, 6, 25, '2023-01-15'),
('Dell XPS 13', 'Premium ultrabook for professionals', 1199.99, 6, 30, '2023-01-18'),
('Men''s Cotton T-Shirt', 'Comfortable cotton t-shirt', 29.99, 7, 100, '2023-01-20'),
('Women''s Summer Dress', 'Elegant summer dress', 79.99, 8, 45, '2023-01-22'),
('The Great Gatsby', 'Classic American novel', 14.99, 9, 200, '2023-01-25'),
('Thinking, Fast and Slow', 'Behavioral economics book', 19.99, 10, 150, '2023-01-28'),
('Garden Tool Set', 'Complete set of gardening tools', 89.99, 4, 75, '2023-02-01'),
('Smart Home Hub', 'Central control for smart devices', 149.99, 1, 40, '2023-02-05'),
('Wireless Headphones', 'Premium wireless audio experience', 299.99, 1, 60, '2023-02-10'),
('Coffee Maker', 'Automatic drip coffee maker', 89.99, 4, 55, '2023-02-15'),
('Running Shoes', 'Comfortable athletic shoes', 129.99, 2, 80, '2023-02-20'),
('Cookbook: Italian Cuisine', 'Authentic Italian recipes', 24.99, 10, 90, '2023-02-25'),
('Bluetooth Speaker', 'Portable wireless speaker', 79.99, 1, 70, '2023-03-01');

-- Insert orders
INSERT INTO orders (user_id, total_amount, status, shipping_address, order_date, shipped_date, delivered_date) VALUES
(1, 1029.98, 'delivered', '123 Main St, Anytown, USA', '2023-03-01 10:00:00', '2023-03-02 14:00:00', '2023-03-05 16:30:00'),
(2, 899.99, 'delivered', '456 Oak Ave, Somewhere, USA', '2023-03-02 11:30:00', '2023-03-03 09:15:00', '2023-03-06 14:20:00'),
(3, 149.98, 'delivered', '789 Pine St, Elsewhere, USA', '2023-03-03 14:45:00', '2023-03-04 10:30:00', '2023-03-07 12:10:00'),
(4, 1379.98, 'shipped', '321 Elm Dr, Nowhere, USA', '2023-03-04 16:20:00', '2023-03-05 13:45:00', NULL),
(5, 59.98, 'delivered', '654 Birch Ln, Anywhere, USA', '2023-03-05 09:10:00', '2023-03-06 15:20:00', '2023-03-09 11:30:00'),
(6, 299.99, 'pending', '987 Cedar St, Someplace, USA', '2023-03-15 13:30:00', NULL, NULL),
(7, 89.99, 'processing', '147 Spruce Ave, Here, USA', '2023-03-16 10:15:00', NULL, NULL),
(8, 44.98, 'delivered', '258 Maple Dr, There, USA', '2023-03-10 12:45:00', '2023-03-11 14:10:00', '2023-03-14 16:25:00'),
(9, 209.98, 'delivered', '369 Willow St, Everywhere, USA', '2023-03-12 15:00:00', '2023-03-13 11:30:00', '2023-03-16 13:45:00'),
(10, 1199.99, 'shipped', '741 Aspen Ln, Nowhere Else, USA', '2023-03-14 11:20:00', '2023-03-15 16:00:00', NULL);

-- Insert order items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
-- Order 1: iPhone 15 Pro + T-Shirt
(1, 1, 1, 999.99, 999.99),
(1, 5, 1, 29.99, 29.99),

-- Order 2: Samsung Galaxy S24
(2, 2, 1, 899.99, 899.99),

-- Order 3: Books
(3, 7, 1, 14.99, 14.99),
(3, 8, 1, 19.99, 19.99),
(3, 14, 1, 24.99, 24.99),
(3, 15, 1, 79.99, 79.99),

-- Order 4: MacBook Air + Accessories
(4, 3, 1, 1299.99, 1299.99),
(4, 11, 1, 79.99, 79.99),

-- Order 5: Clothing
(5, 5, 1, 29.99, 29.99),
(5, 6, 1, 29.99, 29.99),

-- Order 6: Headphones
(6, 11, 1, 299.99, 299.99),

-- Order 7: Garden Tools
(7, 9, 1, 89.99, 89.99),

-- Order 8: Books
(8, 7, 1, 14.99, 14.99),
(8, 8, 1, 19.99, 19.99),
(8, 14, 1, 9.99, 9.99),

-- Order 9: Smart Home + Speaker
(9, 10, 1, 149.99, 149.99),
(9, 15, 1, 59.99, 59.99),

-- Order 10: Dell XPS 13
(10, 4, 1, 1199.99, 1199.99);

-- Insert reviews
INSERT INTO reviews (user_id, product_id, rating, comment, created_at) VALUES
(1, 1, 5, 'Amazing phone! The camera quality is outstanding.', '2023-03-06 10:30:00'),
(2, 2, 4, 'Great phone, good value for money.', '2023-03-07 14:20:00'),
(3, 7, 5, 'Classic book, must read!', '2023-03-08 16:45:00'),
(3, 8, 4, 'Very insightful, changed my perspective on decision making.', '2023-03-08 16:50:00'),
(5, 5, 3, 'Good quality but sizing runs small.', '2023-03-10 11:15:00'),
(8, 7, 5, 'Beautifully written, timeless story.', '2023-03-15 13:30:00'),
(9, 10, 4, 'Works well with all my smart devices.', '2023-03-17 09:45:00'),
(1, 5, 4, 'Comfortable and good quality fabric.', '2023-03-06 10:35:00'),
(4, 3, 5, 'Best laptop I''ve ever owned. Super fast and lightweight.', '2023-03-18 14:20:00'),
(6, 11, 5, 'Excellent sound quality, great for workouts.', '2023-03-16 16:30:00');

-- Insert inventory log entries
INSERT INTO inventory_log (product_id, change_type, quantity_change, reason, created_at) VALUES
(1, 'in', 100, 'Initial stock', '2023-01-10 09:00:00'),
(1, 'out', -50, 'Sales', '2023-03-01 18:00:00'),
(2, 'in', 75, 'Initial stock', '2023-01-12 09:00:00'),
(2, 'out', -40, 'Sales', '2023-03-02 18:00:00'),
(3, 'in', 50, 'Initial stock', '2023-01-15 09:00:00'),
(3, 'out', -25, 'Sales', '2023-03-04 18:00:00'),
(4, 'in', 40, 'Initial stock', '2023-01-18 09:00:00'),
(4, 'out', -10, 'Sales', '2023-03-14 18:00:00'),
(5, 'in', 200, 'Initial stock', '2023-01-20 09:00:00'),
(5, 'out', -100, 'Sales', '2023-03-05 18:00:00'),
(11, 'in', 80, 'Restock', '2023-02-10 09:00:00'),
(11, 'out', -20, 'Sales', '2023-03-15 18:00:00'),
(15, 'in', 90, 'Initial stock', '2023-03-01 09:00:00'),
(15, 'out', -20, 'Sales', '2023-03-12 18:00:00');

-- Update the sequence values to avoid conflicts
SELECT setval('categories_id_seq', (SELECT MAX(id) FROM categories));
SELECT setval('users_id_seq', (SELECT MAX(id) FROM users));
SELECT setval('products_id_seq', (SELECT MAX(id) FROM products));
SELECT setval('orders_id_seq', (SELECT MAX(id) FROM orders));
SELECT setval('order_items_id_seq', (SELECT MAX(id) FROM order_items));
SELECT setval('reviews_id_seq', (SELECT MAX(id) FROM reviews));
SELECT setval('inventory_log_id_seq', (SELECT MAX(id) FROM inventory_log));