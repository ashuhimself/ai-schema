-- Generate realistic demo data for banking database
-- This will create 250 customers with full banking relationships

BEGIN;

-- Use existing branches (already created)

-- Generate 250 customers with realistic demographics
INSERT INTO customers (first_name, last_name, email, phone, date_of_birth, ssn, address, city, state, zip_code, employment_status, annual_income, credit_score, customer_segment, risk_category, kyc_status, branch_id)
SELECT 
  CASE (random() * 49)::int
    WHEN 0 THEN 'John' WHEN 1 THEN 'Jane' WHEN 2 THEN 'Michael' WHEN 3 THEN 'Sarah' WHEN 4 THEN 'David'
    WHEN 5 THEN 'Emily' WHEN 6 THEN 'Robert' WHEN 7 THEN 'Jessica' WHEN 8 THEN 'William' WHEN 9 THEN 'Ashley'
    WHEN 10 THEN 'James' WHEN 11 THEN 'Amanda' WHEN 12 THEN 'Christopher' WHEN 13 THEN 'Stephanie' WHEN 14 THEN 'Daniel'
    WHEN 15 THEN 'Jennifer' WHEN 16 THEN 'Matthew' WHEN 17 THEN 'Michelle' WHEN 18 THEN 'Anthony' WHEN 19 THEN 'Lisa'
    WHEN 20 THEN 'Mark' WHEN 21 THEN 'Kimberly' WHEN 22 THEN 'Donald' WHEN 23 THEN 'Nancy' WHEN 24 THEN 'Steven'
    WHEN 25 THEN 'Dorothy' WHEN 26 THEN 'Paul' WHEN 27 THEN 'Karen' WHEN 28 THEN 'Andrew' WHEN 29 THEN 'Helen'
    WHEN 30 THEN 'Brian' WHEN 31 THEN 'Carol' WHEN 32 THEN 'Kevin' WHEN 33 THEN 'Ruth' WHEN 34 THEN 'George'
    WHEN 35 THEN 'Sharon' WHEN 36 THEN 'Kenneth' WHEN 37 THEN 'Maria' WHEN 38 THEN 'Edward' WHEN 39 THEN 'Linda'
    WHEN 40 THEN 'Ryan' WHEN 41 THEN 'Patricia' WHEN 42 THEN 'Jason' WHEN 43 THEN 'Sandra' WHEN 44 THEN 'Jeffrey'
    WHEN 45 THEN 'Donna' WHEN 46 THEN 'Jacob' WHEN 47 THEN 'Angela' WHEN 48 THEN 'Gary' ELSE 'Barbara'
  END as first_name,
  CASE (random() * 49)::int
    WHEN 0 THEN 'Smith' WHEN 1 THEN 'Johnson' WHEN 2 THEN 'Williams' WHEN 3 THEN 'Brown' WHEN 4 THEN 'Jones'
    WHEN 5 THEN 'Garcia' WHEN 6 THEN 'Miller' WHEN 7 THEN 'Davis' WHEN 8 THEN 'Rodriguez' WHEN 9 THEN 'Martinez'
    WHEN 10 THEN 'Hernandez' WHEN 11 THEN 'Lopez' WHEN 12 THEN 'Gonzalez' WHEN 13 THEN 'Wilson' WHEN 14 THEN 'Anderson'
    WHEN 15 THEN 'Thomas' WHEN 16 THEN 'Taylor' WHEN 17 THEN 'Moore' WHEN 18 THEN 'Jackson' WHEN 19 THEN 'Martin'
    WHEN 20 THEN 'Lee' WHEN 21 THEN 'Perez' WHEN 22 THEN 'Thompson' WHEN 23 THEN 'White' WHEN 24 THEN 'Harris'
    WHEN 25 THEN 'Sanchez' WHEN 26 THEN 'Clark' WHEN 27 THEN 'Ramirez' WHEN 28 THEN 'Lewis' WHEN 29 THEN 'Robinson'
    WHEN 30 THEN 'Walker' WHEN 31 THEN 'Young' WHEN 32 THEN 'Allen' WHEN 33 THEN 'King' WHEN 34 THEN 'Wright'
    WHEN 35 THEN 'Scott' WHEN 36 THEN 'Torres' WHEN 37 THEN 'Nguyen' WHEN 38 THEN 'Hill' WHEN 39 THEN 'Flores'
    WHEN 40 THEN 'Green' WHEN 41 THEN 'Adams' WHEN 42 THEN 'Nelson' WHEN 43 THEN 'Baker' WHEN 44 THEN 'Hall'
    WHEN 45 THEN 'Rivera' WHEN 46 THEN 'Campbell' WHEN 47 THEN 'Mitchell' WHEN 48 THEN 'Carter' ELSE 'Roberts'
  END as last_name,
  lower(
    CASE (random() * 49)::int
      WHEN 0 THEN 'john' WHEN 1 THEN 'jane' WHEN 2 THEN 'michael' WHEN 3 THEN 'sarah' WHEN 4 THEN 'david'
      WHEN 5 THEN 'emily' WHEN 6 THEN 'robert' WHEN 7 THEN 'jessica' WHEN 8 THEN 'william' WHEN 9 THEN 'ashley'
      WHEN 10 THEN 'james' WHEN 11 THEN 'amanda' WHEN 12 THEN 'christopher' WHEN 13 THEN 'stephanie' WHEN 14 THEN 'daniel'
      WHEN 15 THEN 'jennifer' WHEN 16 THEN 'matthew' WHEN 17 THEN 'michelle' WHEN 18 THEN 'anthony' WHEN 19 THEN 'lisa'
      WHEN 20 THEN 'mark' WHEN 21 THEN 'kimberly' WHEN 22 THEN 'donald' WHEN 23 THEN 'nancy' WHEN 24 THEN 'steven'
      WHEN 25 THEN 'dorothy' WHEN 26 THEN 'paul' WHEN 27 THEN 'karen' WHEN 28 THEN 'andrew' WHEN 29 THEN 'helen'
      WHEN 30 THEN 'brian' WHEN 31 THEN 'carol' WHEN 32 THEN 'kevin' WHEN 33 THEN 'ruth' WHEN 34 THEN 'george'
      WHEN 35 THEN 'sharon' WHEN 36 THEN 'kenneth' WHEN 37 THEN 'maria' WHEN 38 THEN 'edward' WHEN 39 THEN 'linda'
      WHEN 40 THEN 'ryan' WHEN 41 THEN 'patricia' WHEN 42 THEN 'jason' WHEN 43 THEN 'sandra' WHEN 44 THEN 'jeffrey'
      WHEN 45 THEN 'donna' WHEN 46 THEN 'jacob' WHEN 47 THEN 'angela' WHEN 48 THEN 'gary' ELSE 'barbara'
    END || '.' ||
    CASE (random() * 49)::int
      WHEN 0 THEN 'smith' WHEN 1 THEN 'johnson' WHEN 2 THEN 'williams' WHEN 3 THEN 'brown' WHEN 4 THEN 'jones'
      WHEN 5 THEN 'garcia' WHEN 6 THEN 'miller' WHEN 7 THEN 'davis' WHEN 8 THEN 'rodriguez' WHEN 9 THEN 'martinez'
      WHEN 10 THEN 'hernandez' WHEN 11 THEN 'lopez' WHEN 12 THEN 'gonzalez' WHEN 13 THEN 'wilson' WHEN 14 THEN 'anderson'
      WHEN 15 THEN 'thomas' WHEN 16 THEN 'taylor' WHEN 17 THEN 'moore' WHEN 18 THEN 'jackson' WHEN 19 THEN 'martin'
      WHEN 20 THEN 'lee' WHEN 21 THEN 'perez' WHEN 22 THEN 'thompson' WHEN 23 THEN 'white' WHEN 24 THEN 'harris'
      WHEN 25 THEN 'sanchez' WHEN 26 THEN 'clark' WHEN 27 THEN 'ramirez' WHEN 28 THEN 'lewis' WHEN 29 THEN 'robinson'
      WHEN 30 THEN 'walker' WHEN 31 THEN 'young' WHEN 32 THEN 'allen' WHEN 33 THEN 'king' WHEN 34 THEN 'wright'
      WHEN 35 THEN 'scott' WHEN 36 THEN 'torres' WHEN 37 THEN 'nguyen' WHEN 38 THEN 'hill' WHEN 39 THEN 'flores'
      WHEN 40 THEN 'green' WHEN 41 THEN 'adams' WHEN 42 THEN 'nelson' WHEN 43 THEN 'baker' WHEN 44 THEN 'hall'
      WHEN 45 THEN 'rivera' WHEN 46 THEN 'campbell' WHEN 47 THEN 'mitchell' WHEN 48 THEN 'carter' ELSE 'roberts'
    END || '@' ||
    CASE (random() * 9)::int
      WHEN 0 THEN 'gmail.com' WHEN 1 THEN 'yahoo.com' WHEN 2 THEN 'outlook.com' WHEN 3 THEN 'hotmail.com' WHEN 4 THEN 'aol.com'
      WHEN 5 THEN 'icloud.com' WHEN 6 THEN 'protonmail.com' WHEN 7 THEN 'company.com' WHEN 8 THEN 'business.org' ELSE 'enterprise.net'
    END || generate_series
  ) as email,
  '(' || (100 + (random() * 900)::int) || ') ' || (100 + (random() * 900)::int) || '-' || (1000 + (random() * 9000)::int) as phone,
  (CURRENT_DATE - interval '25 years' + (random() * interval '40 years'))::date as date_of_birth,
  (100000000 + (random() * 800000000)::bigint)::text as ssn,
  (100 + (random() * 9900)::int) || ' ' || 
  CASE (random() * 19)::int
    WHEN 0 THEN 'Main St' WHEN 1 THEN 'Park Ave' WHEN 2 THEN 'Oak Dr' WHEN 3 THEN 'First Ave' WHEN 4 THEN 'Second St'
    WHEN 5 THEN 'Third Ave' WHEN 6 THEN 'Fourth St' WHEN 7 THEN 'Fifth Ave' WHEN 8 THEN 'Broadway' WHEN 9 THEN 'Washington St'
    WHEN 10 THEN 'Lincoln Ave' WHEN 11 THEN 'Madison St' WHEN 12 THEN 'Jefferson Ave' WHEN 13 THEN 'Adams St' WHEN 14 THEN 'Jackson Ave'
    WHEN 15 THEN 'Wilson St' WHEN 16 THEN 'Taylor Ave' WHEN 17 THEN 'Anderson St' WHEN 18 THEN 'Thomas Ave' ELSE 'Johnson St'
  END as address,
  CASE (random() * 9)::int
    WHEN 0 THEN 'New York' WHEN 1 THEN 'Brooklyn' WHEN 2 THEN 'Queens' WHEN 3 THEN 'Los Angeles' WHEN 4 THEN 'San Francisco'
    WHEN 5 THEN 'Chicago' WHEN 6 THEN 'Miami' WHEN 7 THEN 'Houston' WHEN 8 THEN 'Seattle' ELSE 'Boston'
  END as city,
  CASE (random() * 9)::int
    WHEN 0 THEN 'NY' WHEN 1 THEN 'NY' WHEN 2 THEN 'NY' WHEN 3 THEN 'CA' WHEN 4 THEN 'CA'
    WHEN 5 THEN 'IL' WHEN 6 THEN 'FL' WHEN 7 THEN 'TX' WHEN 8 THEN 'WA' ELSE 'MA'
  END as state,
  (10000 + (random() * 89999)::int)::text as zip_code,
  CASE (random() * 4)::int
    WHEN 0 THEN 'employed' WHEN 1 THEN 'employed' WHEN 2 THEN 'self_employed' WHEN 3 THEN 'retired' ELSE 'student'
  END as employment_status,
  (30000 + (random() * 470000)::int)::decimal as annual_income,
  (300 + (random() * 550)::int) as credit_score,
  CASE 
    WHEN random() < 0.6 THEN 'retail'
    WHEN random() < 0.85 THEN 'premium'
    WHEN random() < 0.95 THEN 'private_banking'
    ELSE 'business'
  END as customer_segment,
  CASE 
    WHEN random() < 0.7 THEN 'low'
    WHEN random() < 0.9 THEN 'medium'
    ELSE 'high'
  END as risk_category,
  CASE (random() * 3)::int
    WHEN 0 THEN 'approved' WHEN 1 THEN 'approved' WHEN 2 THEN 'under_review' ELSE 'pending'
  END as kyc_status,
  (35 + (random() * 4)::int) as branch_id
FROM generate_series(1, 250);

-- Generate accounts for customers (1-3 accounts per customer)
INSERT INTO accounts (customer_id, account_number, account_type, balance, interest_rate, minimum_balance, account_status, overdraft_limit, branch_id, opened_date)
SELECT 
  c.customer_id,
  '4' || lpad((random() * 999999999999999)::bigint::text, 15, '0') as account_number,
  CASE (random() * 5)::int
    WHEN 0 THEN 'checking' WHEN 1 THEN 'savings' WHEN 2 THEN 'money_market' 
    WHEN 3 THEN 'business_checking' WHEN 4 THEN 'business_savings' ELSE 'certificate_deposit'
  END as account_type,
  (100 + (random() * 49900)::int)::decimal as balance,
  CASE 
    WHEN random() < 0.5 THEN 0.0150
    WHEN random() < 0.8 THEN 0.0250
    ELSE 0.0350
  END as interest_rate,
  CASE (random() * 3)::int
    WHEN 0 THEN 100.00 WHEN 1 THEN 500.00 WHEN 2 THEN 1000.00 ELSE 2500.00
  END as minimum_balance,
  CASE (random() * 4)::int
    WHEN 0 THEN 'active' WHEN 1 THEN 'active' WHEN 2 THEN 'active' ELSE 'inactive'
  END as account_status,
  CASE (random() * 3)::int
    WHEN 0 THEN 0.00 WHEN 1 THEN 500.00 WHEN 2 THEN 1000.00 ELSE 2000.00
  END as overdraft_limit,
  c.branch_id,
  (CURRENT_DATE - interval '5 years' + (random() * interval '5 years'))::date as opened_date
FROM customers c
CROSS JOIN generate_series(1, 2) -- 2 accounts per customer on average
WHERE random() < 0.8; -- 80% chance for each account

-- Generate credit cards for customers (60% of customers have 1-2 cards)
INSERT INTO credit_cards (customer_id, card_number, card_type, card_category, credit_limit, current_balance, available_credit, apr, annual_fee, card_status, issue_date, expiry_date)
SELECT 
  c.customer_id,
  CASE (random() * 3)::int
    WHEN 0 THEN '4' WHEN 1 THEN '5' WHEN 2 THEN '3' ELSE '6'
  END || lpad((random() * 999999999999999)::bigint::text, 15, '0') as card_number,
  CASE (random() * 3)::int
    WHEN 0 THEN 'visa' WHEN 1 THEN 'mastercard' WHEN 2 THEN 'amex' ELSE 'discover'
  END as card_type,
  CASE (random() * 5)::int
    WHEN 0 THEN 'basic' WHEN 1 THEN 'gold' WHEN 2 THEN 'platinum' WHEN 3 THEN 'rewards' WHEN 4 THEN 'cashback' ELSE 'business'
  END as card_category,
  CASE 
    WHEN c.credit_score > 750 THEN (5000 + (random() * 45000)::int)::decimal
    WHEN c.credit_score > 650 THEN (2000 + (random() * 18000)::int)::decimal
    ELSE (500 + (random() * 4500)::int)::decimal
  END as credit_limit,
  0.00 as current_balance, -- Will be updated with transactions
  0.00 as available_credit, -- Will be calculated
  (12.99 + (random() * 12)::numeric)::decimal(5,2) as apr,
  CASE (random() * 4)::int
    WHEN 0 THEN 0.00 WHEN 1 THEN 95.00 WHEN 2 THEN 195.00 WHEN 3 THEN 395.00 ELSE 595.00
  END as annual_fee,
  CASE (random() * 4)::int
    WHEN 0 THEN 'active' WHEN 1 THEN 'active' WHEN 2 THEN 'active' ELSE 'inactive'
  END as card_status,
  (CURRENT_DATE - interval '3 years' + (random() * interval '3 years'))::date as issue_date,
  (CURRENT_DATE + interval '2 years' + (random() * interval '3 years'))::date as expiry_date
FROM customers c
WHERE random() < 0.6; -- 60% of customers have credit cards

-- Update available credit
UPDATE credit_cards SET available_credit = credit_limit - current_balance;

-- Generate loans for some customers (30% have loans)
INSERT INTO loans (customer_id, loan_number, loan_type, loan_amount, outstanding_balance, interest_rate, term_months, monthly_payment, loan_status, origination_date, maturity_date, next_payment_date, collateral_value, ltv_ratio)
SELECT 
  c.customer_id,
  'LN' || lpad(generate_series::text, 8, '0') as loan_number,
  CASE (random() * 5)::int
    WHEN 0 THEN 'personal' WHEN 1 THEN 'mortgage' WHEN 2 THEN 'auto' WHEN 3 THEN 'business' WHEN 4 THEN 'student' ELSE 'line_of_credit'
  END as loan_type,
  CASE 
    WHEN random() < 0.3 THEN (5000 + (random() * 45000)::int)::decimal  -- Personal/Auto
    WHEN random() < 0.6 THEN (50000 + (random() * 450000)::int)::decimal -- Mortgage
    ELSE (10000 + (random() * 90000)::int)::decimal  -- Business
  END as loan_amount,
  0.00 as outstanding_balance, -- Will be calculated
  (3.5 + (random() * 8)::numeric)::decimal(5,4) as interest_rate,
  CASE (random() * 4)::int
    WHEN 0 THEN 36 WHEN 1 THEN 60 WHEN 2 THEN 120 WHEN 3 THEN 240 ELSE 360
  END as term_months,
  0.00 as monthly_payment, -- Will be calculated
  CASE (random() * 4)::int
    WHEN 0 THEN 'active' WHEN 1 THEN 'active' WHEN 2 THEN 'active' ELSE 'paid_off'
  END as loan_status,
  (CURRENT_DATE - interval '2 years' + (random() * interval '2 years'))::date as origination_date,
  CURRENT_DATE + interval '5 years' as maturity_date,
  CURRENT_DATE + interval '1 month' as next_payment_date,
  NULL as collateral_value,
  NULL as ltv_ratio
FROM customers c
CROSS JOIN generate_series(1, 75) -- 75 loans total
WHERE c.customer_id <= 75 AND random() < 0.8;

-- Update outstanding balance and monthly payment for active loans
UPDATE loans 
SET outstanding_balance = loan_amount * (0.3 + random() * 0.7),
    monthly_payment = loan_amount * ((interest_rate/100/12) * power(1 + interest_rate/100/12, term_months)) / (power(1 + interest_rate/100/12, term_months) - 1)
WHERE loan_status = 'active';

-- Generate transactions for accounts (last 6 months)
INSERT INTO transactions (account_id, transaction_type, amount, balance_after, description, transaction_date, merchant_name, merchant_category, location, channel, reference_number, status)
SELECT 
  a.account_id,
  CASE (random() * 10)::int
    WHEN 0 THEN 'deposit' WHEN 1 THEN 'withdrawal' WHEN 2 THEN 'transfer_in' WHEN 3 THEN 'transfer_out'
    WHEN 4 THEN 'atm' WHEN 5 THEN 'online' WHEN 6 THEN 'mobile' WHEN 7 THEN 'check' WHEN 8 THEN 'fee' ELSE 'interest'
  END as transaction_type,
  CASE 
    WHEN random() < 0.3 THEN (10 + (random() * 190)::int)::decimal
    WHEN random() < 0.7 THEN (200 + (random() * 800)::int)::decimal
    ELSE (1000 + (random() * 4000)::int)::decimal
  END as amount,
  a.balance + (random() * 1000 - 500)::decimal as balance_after,
  CASE (random() * 9)::int
    WHEN 0 THEN 'ATM Withdrawal' WHEN 1 THEN 'Direct Deposit' WHEN 2 THEN 'Online Purchase' WHEN 3 THEN 'Gas Station'
    WHEN 4 THEN 'Grocery Store' WHEN 5 THEN 'Restaurant' WHEN 6 THEN 'Transfer' WHEN 7 THEN 'Bill Payment' ELSE 'Cash Deposit'
  END as description,
  (CURRENT_TIMESTAMP - interval '6 months' + (random() * interval '6 months')) as transaction_date,
  CASE (random() * 19)::int
    WHEN 0 THEN 'Amazon' WHEN 1 THEN 'Walmart' WHEN 2 THEN 'Target' WHEN 3 THEN 'Starbucks' WHEN 4 THEN 'McDonalds'
    WHEN 5 THEN 'Shell' WHEN 6 THEN 'Exxon' WHEN 7 THEN 'Whole Foods' WHEN 8 THEN 'Home Depot' WHEN 9 THEN 'Best Buy'
    WHEN 10 THEN 'CVS' WHEN 11 THEN 'Walgreens' WHEN 12 THEN 'Netflix' WHEN 13 THEN 'Spotify' WHEN 14 THEN 'Uber'
    WHEN 15 THEN 'Lyft' WHEN 16 THEN 'Costco' WHEN 17 THEN 'Apple Store' WHEN 18 THEN 'Google' ELSE 'Microsoft'
  END as merchant_name,
  CASE (random() * 9)::int
    WHEN 0 THEN 'Retail' WHEN 1 THEN 'Gas Stations' WHEN 2 THEN 'Restaurants' WHEN 3 THEN 'Grocery'
    WHEN 4 THEN 'Entertainment' WHEN 5 THEN 'Health' WHEN 6 THEN 'Travel' WHEN 7 THEN 'Utilities' ELSE 'Other'
  END as merchant_category,
  CASE (random() * 9)::int
    WHEN 0 THEN 'New York, NY' WHEN 1 THEN 'Los Angeles, CA' WHEN 2 THEN 'Chicago, IL' WHEN 3 THEN 'Houston, TX'
    WHEN 4 THEN 'Phoenix, AZ' WHEN 5 THEN 'Philadelphia, PA' WHEN 6 THEN 'San Antonio, TX' WHEN 7 THEN 'San Diego, CA' ELSE 'Dallas, TX'
  END as location,
  CASE (random() * 5)::int
    WHEN 0 THEN 'online' WHEN 1 THEN 'atm' WHEN 2 THEN 'mobile' WHEN 3 THEN 'branch' ELSE 'phone'
  END as channel,
  'TXN' || lpad((random() * 999999999)::bigint::text, 9, '0') as reference_number,
  CASE (random() * 9)::int
    WHEN 0 THEN 'completed' WHEN 1 THEN 'completed' WHEN 2 THEN 'completed' WHEN 3 THEN 'completed'
    WHEN 4 THEN 'completed' WHEN 5 THEN 'completed' WHEN 6 THEN 'completed' WHEN 7 THEN 'pending' ELSE 'failed'
  END as status
FROM accounts a
CROSS JOIN generate_series(1, 15) -- 15 transactions per account
WHERE a.account_status = 'active';

-- Generate credit card transactions
INSERT INTO credit_card_transactions (card_id, transaction_type, amount, merchant_name, merchant_category, transaction_date, location, reference_number, status, rewards_earned)
SELECT 
  cc.card_id,
  CASE (random() * 5)::int
    WHEN 0 THEN 'purchase' WHEN 1 THEN 'purchase' WHEN 2 THEN 'purchase' WHEN 3 THEN 'payment' WHEN 4 THEN 'cash_advance' ELSE 'refund'
  END as transaction_type,
  CASE 
    WHEN random() < 0.5 THEN (10 + (random() * 190)::int)::decimal
    WHEN random() < 0.8 THEN (200 + (random() * 800)::int)::decimal
    ELSE (1000 + (random() * 2000)::int)::decimal
  END as amount,
  CASE (random() * 19)::int
    WHEN 0 THEN 'Amazon' WHEN 1 THEN 'Walmart' WHEN 2 THEN 'Target' WHEN 3 THEN 'Starbucks' WHEN 4 THEN 'McDonalds'
    WHEN 5 THEN 'Shell' WHEN 6 THEN 'Exxon' WHEN 7 THEN 'Whole Foods' WHEN 8 THEN 'Home Depot' WHEN 9 THEN 'Best Buy'
    WHEN 10 THEN 'CVS' WHEN 11 THEN 'Walgreens' WHEN 12 THEN 'Netflix' WHEN 13 THEN 'Spotify' WHEN 14 THEN 'Uber'
    WHEN 15 THEN 'Lyft' WHEN 16 THEN 'Costco' WHEN 17 THEN 'Apple Store' WHEN 18 THEN 'Google' ELSE 'Microsoft'
  END as merchant_name,
  CASE (random() * 9)::int
    WHEN 0 THEN 'Retail' WHEN 1 THEN 'Gas Stations' WHEN 2 THEN 'Restaurants' WHEN 3 THEN 'Grocery'
    WHEN 4 THEN 'Entertainment' WHEN 5 THEN 'Health' WHEN 6 THEN 'Travel' WHEN 7 THEN 'Utilities' ELSE 'Other'
  END as merchant_category,
  (CURRENT_TIMESTAMP - interval '6 months' + (random() * interval '6 months')) as transaction_date,
  CASE (random() * 9)::int
    WHEN 0 THEN 'New York, NY' WHEN 1 THEN 'Los Angeles, CA' WHEN 2 THEN 'Chicago, IL' WHEN 3 THEN 'Houston, TX'
    WHEN 4 THEN 'Phoenix, AZ' WHEN 5 THEN 'Philadelphia, PA' WHEN 6 THEN 'San Antonio, TX' WHEN 7 THEN 'San Diego, CA' ELSE 'Dallas, TX'
  END as location,
  'CC' || lpad((random() * 999999999)::bigint::text, 9, '0') as reference_number,
  CASE (random() * 9)::int
    WHEN 0 THEN 'completed' WHEN 1 THEN 'completed' WHEN 2 THEN 'completed' WHEN 3 THEN 'completed'
    WHEN 4 THEN 'completed' WHEN 5 THEN 'completed' WHEN 6 THEN 'completed' WHEN 7 THEN 'pending' ELSE 'disputed'
  END as status,
  (random() * 10)::decimal(8,2) as rewards_earned
FROM credit_cards cc
CROSS JOIN generate_series(1, 12) -- 12 transactions per credit card
WHERE cc.card_status = 'active';

-- Update credit card balances based on transactions
UPDATE credit_cards cc
SET current_balance = COALESCE((
  SELECT SUM(CASE 
    WHEN transaction_type IN ('purchase', 'cash_advance', 'fee', 'interest') THEN amount
    WHEN transaction_type IN ('payment', 'refund') THEN -amount
    ELSE 0
  END)
  FROM credit_card_transactions cct 
  WHERE cct.card_id = cc.card_id AND status = 'completed'
), 0),
available_credit = credit_limit - COALESCE((
  SELECT SUM(CASE 
    WHEN transaction_type IN ('purchase', 'cash_advance', 'fee', 'interest') THEN amount
    WHEN transaction_type IN ('payment', 'refund') THEN -amount
    ELSE 0
  END)
  FROM credit_card_transactions cct 
  WHERE cct.card_id = cc.card_id AND status = 'completed'
), 0);

-- Generate loan payments
INSERT INTO loan_payments (loan_id, payment_date, payment_amount, principal_amount, interest_amount, payment_method, payment_status)
SELECT 
  l.loan_id,
  (l.origination_date + (generate_series || ' months')::interval)::date as payment_date,
  l.monthly_payment as payment_amount,
  l.monthly_payment * 0.7 as principal_amount,
  l.monthly_payment * 0.3 as interest_amount,
  CASE (random() * 5)::int
    WHEN 0 THEN 'auto_debit' WHEN 1 THEN 'online' WHEN 2 THEN 'branch' WHEN 3 THEN 'phone' ELSE 'check'
  END as payment_method,
  CASE (random() * 9)::int
    WHEN 0 THEN 'completed' WHEN 1 THEN 'completed' WHEN 2 THEN 'completed' WHEN 3 THEN 'completed'
    WHEN 4 THEN 'completed' WHEN 5 THEN 'completed' WHEN 6 THEN 'completed' WHEN 7 THEN 'pending' ELSE 'failed'
  END as payment_status
FROM loans l
CROSS JOIN generate_series(1, 12) -- 12 months of payments
WHERE l.loan_status = 'active' 
AND (l.origination_date + (generate_series || ' months')::interval)::date <= CURRENT_DATE;

COMMIT;

-- Display summary
SELECT 'Data Generation Complete!' as status;
SELECT 'Customers' as table_name, COUNT(*) as record_count FROM customers
UNION ALL
SELECT 'Branches', COUNT(*) FROM branches
UNION ALL
SELECT 'Accounts', COUNT(*) FROM accounts
UNION ALL
SELECT 'Transactions', COUNT(*) FROM transactions
UNION ALL
SELECT 'Credit Cards', COUNT(*) FROM credit_cards
UNION ALL
SELECT 'Credit Card Transactions', COUNT(*) FROM credit_card_transactions
UNION ALL
SELECT 'Loans', COUNT(*) FROM loans
UNION ALL
SELECT 'Loan Payments', COUNT(*) FROM loan_payments;
