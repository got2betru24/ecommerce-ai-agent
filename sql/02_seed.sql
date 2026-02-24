USE eCommerce;

-- Customers
INSERT INTO Customer (FirstName, LastName) VALUES
('Anderson', 'Cooper'),
('Robert', 'Jensen'),
('Sarah', 'Mitchell'),
('Emily', 'Jensen'),
('Carlos', 'Rivera');

-- Products
INSERT INTO Product (ProductName, Price, CurrentQuantity) VALUES
('Men\'s Alpine Jacket - Blue', 42.99, 15),
('Men\'s Alpine Jacket - Dark Grey', 42.99, 12),
('Men\'s Ski Pants - Blue', 32.99, 15),
('Men\'s Ski Pants - Dark Grey', 32.99, 8),
('Women\'s Alpine Jacket - Red', 44.99, 10),
('Women\'s Alpine Jacket - Black', 44.99, 6),
('Women\'s Ski Pants - Black', 34.99, 14),
('Thermal Base Layer - Men\'s', 24.99, 20),
('Thermal Base Layer - Women\'s', 24.99, 18),
('Ski Goggles - Pro Series', 59.99, 9);

-- Orders
-- Anderson Cooper (CustomerId 1)
INSERT INTO Orders (CustomerId, ProductId, OrderDate, Price, Quantity, OrderStatus) VALUES
(1, 1, '2026-01-15', 42.99, 1, 'delivered'),
(1, 3, '2026-01-28', 32.99, 1, 'delivered'),
(1, 8, '2026-02-10', 24.99, 2, 'shipped'),
(1, 10, '2026-02-18', 59.99, 1, 'processing');

-- Robert Jensen (CustomerId 2)
INSERT INTO Orders (CustomerId, ProductId, OrderDate, Price, Quantity, OrderStatus) VALUES
(2, 2, '2026-01-10', 42.99, 1, 'delivered'),
(2, 4, '2026-01-10', 32.99, 1, 'delivered'),
(2, 8, '2026-02-05', 24.99, 1, 'shipped'),
(2, 10, '2026-02-19', 59.99, 1, 'processing');

-- Sarah Mitchell (CustomerId 3)
INSERT INTO Orders (CustomerId, ProductId, OrderDate, Price, Quantity, OrderStatus) VALUES
(3, 5, '2026-01-20', 44.99, 1, 'delivered'),
(3, 7, '2026-01-20', 34.99, 1, 'delivered'),
(3, 9, '2026-02-01', 24.99, 2, 'delivered'),
(3, 6, '2026-02-14', 44.99, 1, 'shipped'),
(3, 10, '2026-02-17', 59.99, 1, 'processing');

-- Emily Jensen (CustomerId 4)
INSERT INTO Orders (CustomerId, ProductId, OrderDate, Price, Quantity, OrderStatus) VALUES
(4, 6, '2026-01-25', 44.99, 1, 'delivered'),
(4, 7, '2026-02-03', 34.99, 1, 'shipped'),
(4, 9, '2026-02-03', 24.99, 1, 'shipped'),
(4, 10, '2026-02-20', 59.99, 1, 'processing');

-- Carlos Rivera (CustomerId 5)
INSERT INTO Orders (CustomerId, ProductId, OrderDate, Price, Quantity, OrderStatus) VALUES
(5, 1, '2026-02-01', 42.99, 1, 'delivered'),
(5, 3, '2026-02-01', 32.99, 1, 'delivered'),
(5, 8, '2026-02-15', 24.99, 3, 'shipped');