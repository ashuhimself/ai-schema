-- Fix merchant categorization to be realistic
-- This script corrects the random categorization with proper merchant-to-category mapping

BEGIN;

-- Create a proper merchant category mapping
UPDATE transactions 
SET merchant_category = CASE 
    -- Food & Dining
    WHEN merchant_name IN ('McDonalds', 'Starbucks', 'Subway', 'KFC', 'Pizza Hut', 'Dominos', 'Chipotle', 'Taco Bell') THEN 'Restaurants'
    WHEN merchant_name IN ('Whole Foods', 'Walmart', 'Target', 'Costco', 'Kroger', 'Safeway', 'Publix') THEN 'Grocery'
    
    -- Gas Stations
    WHEN merchant_name IN ('Shell', 'Exxon', 'BP', 'Chevron', 'Mobil', '76', 'Citgo', 'Texaco') THEN 'Gas Stations'
    
    -- Retail & Shopping
    WHEN merchant_name IN ('Amazon', 'Best Buy', 'Apple Store', 'Microsoft', 'Target', 'Walmart') THEN 'Retail'
    WHEN merchant_name IN ('Home Depot', 'Lowes', 'Ace Hardware', 'Menards') THEN 'Home Improvement'
    
    -- Health & Pharmacy
    WHEN merchant_name IN ('CVS', 'Walgreens', 'Rite Aid', 'Pharmacy', 'Clinic', 'Hospital') THEN 'Health'
    
    -- Entertainment & Streaming
    WHEN merchant_name IN ('Netflix', 'Spotify', 'Hulu', 'Disney+', 'Amazon Prime', 'YouTube') THEN 'Entertainment'
    WHEN merchant_name IN ('AMC', 'Regal', 'MovieTheater', 'Concert', 'Sports') THEN 'Entertainment'
    
    -- Transportation
    WHEN merchant_name IN ('Uber', 'Lyft', 'Taxi', 'Bus', 'Train', 'Airline', 'Airport') THEN 'Transportation'
    
    -- Utilities & Services
    WHEN merchant_name IN ('Electric Company', 'Gas Company', 'Water', 'Internet', 'Phone', 'Cable') THEN 'Utilities'
    WHEN merchant_name = 'Google' AND transaction_type = 'online' THEN 'Technology'
    
    -- Travel
    WHEN merchant_name IN ('Hotel', 'Airbnb', 'Expedia', 'Booking.com', 'Airline', 'Car Rental') THEN 'Travel'
    
    -- Default fallback for existing categories
    ELSE merchant_category
END
WHERE merchant_name IS NOT NULL;

-- Fix specific problematic categorizations we can see from the data
UPDATE transactions SET merchant_category = 'Technology' WHERE merchant_name = 'Google';
UPDATE transactions SET merchant_category = 'Technology' WHERE merchant_name = 'Microsoft';
UPDATE transactions SET merchant_category = 'Technology' WHERE merchant_name = 'Apple Store';

-- Update credit card transactions with the same logic
UPDATE credit_card_transactions 
SET merchant_category = CASE 
    -- Food & Dining
    WHEN merchant_name IN ('McDonalds', 'Starbucks', 'Subway', 'KFC', 'Pizza Hut', 'Dominos', 'Chipotle', 'Taco Bell') THEN 'Restaurants'
    WHEN merchant_name IN ('Whole Foods', 'Walmart', 'Target', 'Costco', 'Kroger', 'Safeway', 'Publix') THEN 'Grocery'
    
    -- Gas Stations
    WHEN merchant_name IN ('Shell', 'Exxon', 'BP', 'Chevron', 'Mobil', '76', 'Citgo', 'Texaco') THEN 'Gas Stations'
    
    -- Retail & Shopping
    WHEN merchant_name IN ('Amazon', 'Best Buy', 'Apple Store', 'Microsoft', 'Target', 'Walmart') THEN 'Retail'
    WHEN merchant_name IN ('Home Depot', 'Lowes', 'Ace Hardware', 'Menards') THEN 'Home Improvement'
    
    -- Health & Pharmacy
    WHEN merchant_name IN ('CVS', 'Walgreens', 'Rite Aid', 'Pharmacy', 'Clinic', 'Hospital') THEN 'Health'
    
    -- Entertainment & Streaming
    WHEN merchant_name IN ('Netflix', 'Spotify', 'Hulu', 'Disney+', 'Amazon Prime', 'YouTube') THEN 'Entertainment'
    WHEN merchant_name IN ('AMC', 'Regal', 'MovieTheater', 'Concert', 'Sports') THEN 'Entertainment'
    
    -- Transportation
    WHEN merchant_name IN ('Uber', 'Lyft', 'Taxi', 'Bus', 'Train', 'Airline', 'Airport') THEN 'Transportation'
    
    -- Utilities & Services
    WHEN merchant_name IN ('Electric Company', 'Gas Company', 'Water', 'Internet', 'Phone', 'Cable') THEN 'Utilities'
    WHEN merchant_name = 'Google' AND transaction_type = 'purchase' THEN 'Technology'
    
    -- Travel
    WHEN merchant_name IN ('Hotel', 'Airbnb', 'Expedia', 'Booking.com', 'Airline', 'Car Rental') THEN 'Travel'
    
    -- Default fallback for existing categories
    ELSE merchant_category
END
WHERE merchant_name IS NOT NULL;

-- Fix specific problematic categorizations for credit cards too
UPDATE credit_card_transactions SET merchant_category = 'Technology' WHERE merchant_name = 'Google';
UPDATE credit_card_transactions SET merchant_category = 'Technology' WHERE merchant_name = 'Microsoft';
UPDATE credit_card_transactions SET merchant_category = 'Retail' WHERE merchant_name = 'Apple Store';

COMMIT;

-- Verify the fix by showing corrected merchant categories
SELECT 'Merchant Categorization Fixed!' as status;
SELECT 
    merchant_name,
    merchant_category,
    COUNT(*) as transaction_count
FROM transactions 
WHERE merchant_name IS NOT NULL 
GROUP BY merchant_name, merchant_category 
ORDER BY merchant_name, merchant_category;
