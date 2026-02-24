GRANT ALL PRIVILEGES ON eCommerce.* TO 'ecommerce_user'@'%';
FLUSH PRIVILEGES;

USE eCommerce;
CREATE TABLE Customer (
    id INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(100),
    LastName VARCHAR(100)
);
CREATE TABLE Product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ProductName VARCHAR(255),
    Price DECIMAL(10, 2),
    CurrentQuantity INT
);
CREATE TABLE Orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    CustomerId INT,
    ProductId INT,
    OrderDate DATE,
    Price DECIMAL(10, 2),
    Quantity INT,
    OrderStatus VARCHAR(20),
    FOREIGN KEY (CustomerId) REFERENCES Customer(id),
    FOREIGN KEY (ProductId) REFERENCES Product(id)
);
CREATE TABLE ConversationHistory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    SessionId VARCHAR(100) NOT NULL,
    Role VARCHAR(20) NOT NULL,
    Content TEXT NOT NULL,
    MessageType VARCHAR(20) DEFAULT 'text',
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);