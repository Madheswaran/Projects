INSERT INTO customers
(name,email,password,wallet)
VALUES
(
'Madhes',
'madhes@gmail.com',
'password',
500
)
ON CONFLICT (email)
DO NOTHING;