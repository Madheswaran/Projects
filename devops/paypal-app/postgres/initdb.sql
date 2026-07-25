CREATE TABLE customers(

id SERIAL PRIMARY KEY,

name VARCHAR(100),

email VARCHAR(100),

password VARCHAR(100),

wallet DECIMAL(10,2),

phone VARCHAR(20),

address TEXT

);


INSERT INTO customers(

name,

email,

password,

wallet,

phone,

address

)

VALUES(

'Ganesha',

'ganesha@gmail.com',

'password123',

5000,

'9876543210',

'Chennai'

);