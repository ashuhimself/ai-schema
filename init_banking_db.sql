-- Initialize Banking Database for Warehouse Copilot
-- This script sets up the comprehensive banking demo database

\c warehouse;

-- Drop any existing e-commerce tables first
DROP TABLE IF EXISTS reviews CASCADE;
DROP TABLE IF EXISTS order_items CASCADE;
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS inventory_log CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Load banking schema
\i /docker-entrypoint-initdb.d/banking_schema.sql

-- Load banking data
\i /docker-entrypoint-initdb.d/banking_data.sql

-- Create some useful views for analysis
CREATE OR REPLACE VIEW customer_summary AS
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name as full_name,
    c.customer_segment,
    c.credit_score,
    c.annual_income,
    c.risk_category,
    COUNT(DISTINCT a.account_id) as total_accounts,
    COALESCE(SUM(a.balance), 0) as total_balance,
    COUNT(DISTINCT cc.card_id) as total_credit_cards,
    COALESCE(SUM(cc.credit_limit), 0) as total_credit_limit,
    COALESCE(SUM(cc.current_balance), 0) as total_credit_balance,
    COUNT(DISTINCT l.loan_id) as total_loans,
    COALESCE(SUM(l.outstanding_balance), 0) as total_loan_balance
FROM customers c
LEFT JOIN accounts a ON c.customer_id = a.customer_id AND a.account_status = 'active'
LEFT JOIN credit_cards cc ON c.customer_id = cc.customer_id AND cc.card_status = 'active'
LEFT JOIN loans l ON c.customer_id = l.customer_id AND l.loan_status = 'active'
GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment, c.credit_score, c.annual_income, c.risk_category;

CREATE OR REPLACE VIEW monthly_transaction_trends AS
SELECT 
    DATE_TRUNC('month', transaction_date) as month,
    transaction_type,
    merchant_category,
    COUNT(*) as transaction_count,
    SUM(ABS(amount)) as total_amount,
    AVG(ABS(amount)) as avg_amount
FROM transactions 
WHERE transaction_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', transaction_date), transaction_type, merchant_category;

CREATE OR REPLACE VIEW risk_analysis AS
SELECT 
    risk_category,
    customer_segment,
    COUNT(*) as customer_count,
    AVG(annual_income) as avg_income,
    AVG(credit_score) as avg_credit_score,
    SUM(CASE WHEN cs.total_credit_balance > cs.total_credit_limit * 0.8 THEN 1 ELSE 0 END) as high_utilization_customers,
    SUM(CASE WHEN cs.total_loan_balance > cs.annual_income * 3 THEN 1 ELSE 0 END) as high_debt_customers
FROM customers c
JOIN customer_summary cs ON c.customer_id = cs.customer_id
GROUP BY risk_category, customer_segment;

CREATE OR REPLACE VIEW branch_performance AS
SELECT 
    b.branch_name,
    b.city,
    b.state,
    COUNT(DISTINCT c.customer_id) as total_customers,
    COUNT(DISTINCT a.account_id) as total_accounts,
    SUM(a.balance) as total_deposits,
    COUNT(DISTINCT cc.card_id) as total_credit_cards,
    COUNT(DISTINCT l.loan_id) as total_loans,
    SUM(l.outstanding_balance) as total_loan_balance
FROM branches b
LEFT JOIN customers c ON b.branch_id = c.branch_id
LEFT JOIN accounts a ON c.customer_id = a.customer_id AND a.account_status = 'active'
LEFT JOIN credit_cards cc ON c.customer_id = cc.customer_id AND cc.card_status = 'active'
LEFT JOIN loans l ON c.customer_id = l.customer_id AND l.loan_status = 'active'
GROUP BY b.branch_id, b.branch_name, b.city, b.state;

-- Grant permissions
GRANT SELECT ON ALL TABLES IN SCHEMA public TO postgres;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT USAGE ON SCHEMA public TO postgres;