INSERT INTO users (first_name, last_name, email_address, password)
VALUES
    -- ('John', 'Doe', 'john.doe@example.com', 'password123'),
    -- ('Jane', 'Smith', 'jane.smith@example.com', 'securepass'),
    -- ('Alice', 'Johnson', 'alice.j@example.com', 'mypassword'),
    -- ('Bob', 'Williams', 'bob.w@example.com', 'pass1234'),
    -- ('John', 'Smith', 'john_s@example.com', 'abcdef'),
    ('John', 'Doe', 'chris.owen@sigmalabs.co.uk', 'password123'),
    ('Jane', 'Smith', 'trainee.india.howell@sigmalabs.co.uk', 'securepass'),
    ('Alice', 'Johnson', 'fariha.choudhury@sigmalabs.co.uk', 'mypassword'),
    ('Bob', 'Williams', 'trainee.anita.megarry@sigmalabs.co.uk', 'pass1234'),
    ('John', 'Smith', 'dan.keefe@sigmalabs.co.uk', 'abcdef'),
    ('Gem', 'Lo', 'trainee.gem.lo@sigmalabs.co.uk', 'trainee');



INSERT INTO website (website_name)
VALUES 
    ('Amazon'),
    ('eBay'),
    ('BestBuy'),
    ('Walmart'),
    ('Target'),
    ('Steam');

INSERT INTO product (product_name, url, website_id, original_price)
VALUES 
    ('Laptop', 'https://www.amazon.com/laptop', 1, 999.99),
    ('Smartphone', 'https://www.ebay.com/smartphone', 2, 799.99),
    ('Headphones', 'https://www.bestbuy.com/headphones', 3, 199.99),
    ('Tablet', 'https://www.walmart.com/tablet', 4, 299.99),
    ('Smartwatch', 'https://www.target.com/smartwatch', 5, 149.99),
    ('Slay the Spire', 'https://store.steampowered.com/app/646570/Slay_the_Spire/', 6, 19.99);

    -- ('Cyberpunk 2077','https://store.steampowered.com/app/1091500/Cyberpunk_2077/',6,49.99),
    -- ('Stardew Valley','https://store.steampowered.com/app/413150/Stardew_Valley/',6,10.99);

INSERT INTO price_changes (price, product_id, timestamp)
VALUES 
    (949.99, 1, '2024-12-01 10:00:00'),
    (939.99, 1, '2024-12-02 10:00:00'),
    (929.99, 1, '2024-12-03 10:00:00'),
    (919.99, 1, '2024-12-04 10:00:00'),
    (909.99, 1, '2024-12-05 10:00:00'),
    (899.99, 1, '2024-12-06 10:00:00'),
    (889.99, 1, '2024-12-07 10:00:00'),
    (879.99, 1, '2024-12-08 10:00:00'),
    (759.99, 2, '2024-12-01 11:00:00'),
    (749.99, 2, '2024-12-02 11:00:00'),
    (739.99, 2, '2024-12-03 11:00:00'),
    (729.99, 2, '2024-12-04 11:00:00'),
    (719.99, 2, '2024-12-05 11:00:00'),
    (709.99, 2, '2024-12-06 11:00:00'),
    (699.99, 2, '2024-12-07 11:00:00'),
    (689.99, 2, '2024-12-08 11:00:00'),
    (179.99, 3, '2024-12-01 12:00:00'),
    (169.99, 3, '2024-12-02 12:00:00'),
    (159.99, 3, '2024-12-03 12:00:00'),
    (149.99, 3, '2024-12-04 12:00:00'),
    (139.99, 3, '2024-12-05 12:00:00'),
    (129.99, 3, '2024-12-06 12:00:00'),
    (119.99, 3, '2024-12-07 12:00:00'),
    (109.99, 3, '2024-12-08 12:00:00'),
    (289.99, 4, '2024-12-01 13:00:00'),
    (279.99, 4, '2024-12-02 13:00:00'),
    (269.99, 4, '2024-12-03 13:00:00'),
    (259.99, 4, '2024-12-04 13:00:00'),
    (249.99, 4, '2024-12-05 13:00:00'),
    (239.99, 4, '2024-12-06 13:00:00'),
    (229.99, 4, '2024-12-07 13:00:00'),
    (219.99, 4, '2024-12-08 13:00:00'),
    (139.99, 5, '2024-12-01 14:00:00'),
    (129.99, 5, '2024-12-02 14:00:00'),
    (119.99, 5, '2024-12-03 14:00:00'),
    (109.99, 5, '2024-12-04 14:00:00'),
    (99.99, 5, '2024-12-05 14:00:00'),
    (89.99, 5, '2024-12-06 14:00:00'),
    (79.99, 5, '2024-12-07 14:00:00'),
    (69.99, 5, '2024-12-08 14:00:00'),
    (1029.99, 1, '2024-12-09 10:00:00'),
    (689.49, 2, '2024-12-09 11:00:00'),
    (149.99, 3, '2024-12-09 12:00:00'),
    (199.99, 4, '2024-12-09 13:00:00'),
    (59.99, 5, '2024-12-09 14:00:00');


INSERT INTO subscription (user_id, product_id, notification_price)
VALUES 
    (1, 1, 900.0),
    (2, 2, 730.0),
    (3, 3, 150.0),
    (4, 4, 270.0),
    (5, 5, 80.0),
    (6, 6, 10.99);