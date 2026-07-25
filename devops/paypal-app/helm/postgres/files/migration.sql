-- Customer table upgrades

ALTER TABLE customers
ADD COLUMN IF NOT EXISTS phone VARCHAR(20);

ALTER TABLE customers
ADD COLUMN IF NOT EXISTS address TEXT;

ALTER TABLE customers
ADD COLUMN IF NOT EXISTS city VARCHAR(100);

------------------------------------------------

CREATE TABLE IF NOT EXISTS transactions
(
    id SERIAL PRIMARY KEY,

    sender_id INTEGER REFERENCES customers(id),

    receiver_email VARCHAR(100),

    amount DECIMAL(10,2),

    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

------------------------------------------------

UPDATE customers
SET
phone='9876543210',
address='Chennai'
WHERE email='ganesha@gmail.com';

UPDATE customers
SET
phone='9876543211',
address='Coimbatore'
WHERE email='muruga@gmail.com';

UPDATE customers
SET
phone='9876543212',
address='Madurai'
WHERE email='lakshmi@gmail.com';