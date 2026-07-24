CREATE TABLE IF NOT EXISTS customers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    wallet NUMERIC(10,2)
);

INSERT INTO customers (name,email,password,wallet)
VALUES
('Ganesha','ganesha@test.com','12345',5000),
('Muruga','muruga@test.com','12345',3500),
('Lakshmi','lakshmi@test.com','12345',8000);