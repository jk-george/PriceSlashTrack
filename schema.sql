DROP TABLE IF EXISTS notifications_sent CASCADE;
DROP TABLE IF EXISTS subscription CASCADE;
DROP TABLE IF EXISTS price_changes CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS website CASCADE;
DROP TABLE IF EXISTS users CASCADE;

CREATE TABLE users (
    user_id INT GENERATED ALWAYS AS IDENTITY,
    first_name VARCHAR(30),
    last_name VARCHAR(30),
    email_address VARCHAR(320) NOT NULL UNIQUE,
    password VARCHAR(30),
    PRIMARY KEY (user_id)
);

CREATE TABLE website (
    website_id INT GENERATED ALWAYS AS IDENTITY,
    website_name VARCHAR(30) NOT NULL UNIQUE,
    PRIMARY KEY (website_id)
);

CREATE TABLE product (
    product_id INT GENERATED ALWAYS AS IDENTITY,
    product_name VARCHAR(100) NOT NULL,
    url VARCHAR(2048) NOT NULL UNIQUE,
    website_id INT NOT NULL,
    original_price FLOAT NOT NULL,
    PRIMARY KEY (product_id),
    FOREIGN KEY (website_id) REFERENCES website(website_id)
);

CREATE TABLE price_changes (
    price_id INT GENERATED ALWAYS AS IDENTITY,
    price FLOAT NOT NULL,
    product_id INT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (price_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE subscription (
    subscription_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    notification_price FLOAT NOT NULL,
    PRIMARY KEY (subscription_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);

CREATE TABLE notifications_sent (
    notification_id INT GENERATED ALWAYS AS IDENTITY,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    price FLOAT NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (notification_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES product(product_id)
);