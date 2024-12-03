INSERT INTO users (first_name, last_name, email_address, password)
VALUES
    ('John', 'Doe', 'john.doe@example.com', 'password123'),
    ('Jane', 'Smith', 'jane.smith@example.com', 'securepass'),
    ('Alice', 'Johnson', 'alice.j@example.com', 'mypassword'),
    ('Bob', 'Williams', 'bob.w@example.com', 'pass1234'),
    ('John', 'Smith', 'john_s@example.com', 'abcdef');


INSERT INTO website (website_name)
VALUES 
    ('Amazon'),
    ('eBay'),
    ('BestBuy'),
    ('Walmart'),
    ('Target');

INSERT INTO product (product_name, url, website_id, original_price)
VALUES 
    ('Laptop', 'https://www.amazon.com/laptop', 1, 999.99),
    ('Smartphone', 'https://www.ebay.com/smartphone', 2, 799.99),
    ('Headphones', 'https://www.bestbuy.com/headphones', 3, 199.99),
    ('Tablet', 'https://www.walmart.com/tablet', 4, 299.99),
    ('Smartwatch', 'https://www.target.com/smartwatch', 5, 149.99);

INSERT INTO price_changes (price, product_id, timestamp)
VALUES 
    (949.99, 1, '2024-12-01 10:00:00'),
    (759.99, 2, '2024-12-01 11:00:00'),
    (179.99, 3, '2024-12-01 12:00:00'),
    (289.99, 4, '2024-12-01 13:00:00'),
    (139.99, 5, '2024-12-01 14:00:00'),
    (939.99, 1, '2024-12-02 10:00:00'),
    (929.99, 1, '2024-12-03 10:00:00'),
    (749.99, 2, '2024-12-02 11:00:00'),
    (739.99, 2, '2024-12-03 11:00:00'),
    (169.99, 3, '2024-12-02 12:00:00'),
    (159.99, 3, '2024-12-03 12:00:00'),
    (279.99, 4, '2024-12-02 13:00:00'),
    (269.99, 4, '2024-12-03 13:00:00'),
    (129.99, 5, '2024-12-02 14:00:00'),
    (119.99, 5, '2024-12-03 14:00:00');


INSERT INTO subscription (user_id, product_id, discount_percentage)
VALUES 
    (1, 1, 10.0),
    (2, 2, 5.0),
    (3, 3, 15.0),
    (4, 4, 8.0),
    (5, 5, 12.0);
