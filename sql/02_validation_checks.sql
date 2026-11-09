-- Data validation checks
-- Every check should return zero rows (or zero violations).

-- ============================================================
-- Foreign Key / Orphan Record Checks
-- ============================================================

-- Orders linked to valid customers
SELECT o.order_id
FROM orders o
LEFT JOIN customer c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;

-- Books linked to valid genres
SELECT b.book_id
FROM book b
LEFT JOIN genre g ON b.genre_id = g.genre_id
WHERE g.genre_id IS NULL;

-- Order items linked to valid orders
SELECT oi.order_id, oi.book_id
FROM order_item oi
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- Order items linked to valid books
SELECT oi.order_id, oi.book_id
FROM order_item oi
LEFT JOIN book b ON oi.book_id = b.book_id
WHERE b.book_id IS NULL;

-- Book-author links tied to valid books
SELECT ba.book_id, ba.author_id
FROM book_author ba
LEFT JOIN book b ON ba.book_id = b.book_id
WHERE b.book_id IS NULL;

-- Book-author links tied to valid authors
SELECT ba.book_id, ba.author_id
FROM book_author ba
LEFT JOIN author a ON ba.author_id = a.author_id
WHERE a.author_id IS NULL;

-- Payments linked to valid orders
SELECT p.payment_id, p.order_id
FROM payment p
LEFT JOIN orders o ON p.order_id = o.order_id
WHERE o.order_id IS NULL;

-- Shipping records linked to valid orders
SELECT s.shipping_id, s.order_id
FROM shipping_details s
LEFT JOIN orders o ON s.order_id = o.order_id
WHERE o.order_id IS NULL;

-- ============================================================
-- Duplicate Value Checks
-- ============================================================

-- Duplicate customer emails
SELECT email, COUNT(*) AS cnt
FROM customer
GROUP BY email
HAVING COUNT(*) > 1;

-- Duplicate ISBNs
SELECT isbn, COUNT(*) AS cnt
FROM book
GROUP BY isbn
HAVING COUNT(*) > 1;

-- Duplicate author names
SELECT author_name, COUNT(*) AS cnt
FROM author
GROUP BY author_name
HAVING COUNT(*) > 1;

-- Duplicate composite keys in Order_Item
SELECT order_id, book_id, COUNT(*) AS cnt
FROM order_item
GROUP BY order_id, book_id
HAVING COUNT(*) > 1;

-- Duplicate composite keys in Book_Author
SELECT book_id, author_id, COUNT(*) AS cnt
FROM book_author
GROUP BY book_id, author_id
HAVING COUNT(*) > 1;

-- ============================================================
-- Date Sequence Checks
-- ============================================================

-- Orders placed before customer join date
SELECT o.order_id, o.order_date, c.join_date
FROM orders o
JOIN customer c ON o.customer_id = c.customer_id
WHERE o.order_date < c.join_date;

-- Payments dated before order date
SELECT p.payment_id, p.order_id, p.payment_date, o.order_date
FROM payment p
JOIN orders o ON p.order_id = o.order_id
WHERE p.payment_date < o.order_date;

-- Shipments dated before payment date
SELECT s.shipping_id, s.order_id, s.shipped_date, p.payment_date
FROM shipping_details s
JOIN payment p ON s.order_id = p.order_id
WHERE s.shipped_date IS NOT NULL
  AND s.shipped_date < p.payment_date;

-- Deliveries dated before shipped date
SELECT shipping_id, order_id, shipped_date, delivery_date
FROM shipping_details
WHERE shipped_date IS NOT NULL
  AND delivery_date IS NOT NULL
  AND delivery_date < shipped_date;

-- Orders dated in the future
SELECT order_id, order_date
FROM orders
WHERE order_date > DATE('now');

-- ============================================================
-- Financial Consistency Checks
-- ============================================================

-- Order totals reconciled to item revenue plus shipping cost
SELECT
    o.order_id,
    ROUND(o.total_amount, 2) AS recorded_total,
    ROUND(SUM(oi.quantity * oi.unit_price)
        + COALESCE(s.shipping_cost, 0), 2) AS calculated_total
FROM orders o
JOIN order_item oi ON o.order_id = oi.order_id
LEFT JOIN shipping_details s ON o.order_id = s.order_id
GROUP BY o.order_id
HAVING ABS(
    ROUND(o.total_amount, 2) -
    ROUND(SUM(oi.quantity * oi.unit_price)
        + COALESCE(s.shipping_cost, 0), 2)
) > 0.01;

-- Payment amount matches order total
SELECT p.payment_id, p.order_id, p.amount, o.total_amount
FROM payment p
JOIN orders o ON p.order_id = o.order_id
WHERE ABS(p.amount - o.total_amount) > 0.01;

-- ============================================================
-- Pricing and Quantity Rule Checks
-- ============================================================

-- Items sold above list price
SELECT oi.order_id, oi.book_id, oi.unit_price, b.list_price
FROM order_item oi
JOIN book b ON oi.book_id = b.book_id
WHERE oi.unit_price > b.list_price;

-- Zero or negative quantities
SELECT * FROM order_item WHERE quantity <= 0;

-- Zero or negative unit prices
SELECT * FROM order_item WHERE unit_price <= 0;

-- Negative stock quantities
SELECT * FROM book WHERE stock_quantity < 0;

-- ============================================================
-- Status Logic Checks
-- ============================================================

-- Paid, Shipped, or Delivered orders without successful payment
SELECT o.order_id, o.order_status, p.payment_status
FROM orders o
JOIN payment p ON o.order_id = p.order_id
WHERE o.order_status IN ('Paid', 'Shipped', 'Delivered')
  AND p.payment_status <> 'Success';

-- Cancelled orders with invalid shipping status
SELECT o.order_id, o.order_status, s.shipping_status
FROM orders o
JOIN shipping_details s ON o.order_id = s.order_id
WHERE o.order_status = 'Cancelled'
  AND s.shipping_status <> 'Cancelled';

-- Returned orders with invalid shipping status
SELECT o.order_id, o.order_status, s.shipping_status
FROM orders o
JOIN shipping_details s ON o.order_id = s.order_id
WHERE o.order_status = 'Returned'
  AND s.shipping_status <> 'Returned';

-- Pending orders with invalid shipping status
SELECT o.order_id, o.order_status, s.shipping_status
FROM orders o
JOIN shipping_details s ON o.order_id = s.order_id
WHERE o.order_status = 'Pending'
  AND s.shipping_status <> 'Not Shipped';

-- Returned orders without refunded payment
SELECT o.order_id, o.order_status, p.payment_status
FROM orders o
JOIN payment p ON o.order_id = p.order_id
WHERE o.order_status = 'Returned'
  AND p.payment_status <> 'Refunded';

-- ============================================================
-- Shipping Logic Checks
-- ============================================================

-- UK customers assigned non-UK shipping methods
SELECT s.order_id, c.country, s.shipping_method
FROM shipping_details s
JOIN orders o ON s.order_id = o.order_id
JOIN customer c ON o.customer_id = c.customer_id
WHERE c.country = 'United Kingdom'
  AND s.shipping_method NOT IN ('Standard', 'Express', 'Next-Day');

-- International customers assigned invalid shipping methods
SELECT s.order_id, c.country, s.shipping_method
FROM shipping_details s
JOIN orders o ON s.order_id = o.order_id
JOIN customer c ON o.customer_id = c.customer_id
WHERE c.country <> 'United Kingdom'
  AND s.shipping_method NOT IN
      ('International Standard', 'International Express');

-- ============================================================
-- Record Count Checks
-- ============================================================

-- Row counts by main table
SELECT 'customer'         AS table_name, COUNT(*) AS row_count FROM customer
UNION ALL
SELECT 'book',            COUNT(*) FROM book
UNION ALL
SELECT 'author',          COUNT(*) FROM author
UNION ALL
SELECT 'orders',          COUNT(*) FROM orders
UNION ALL
SELECT 'order_item',      COUNT(*) FROM order_item
UNION ALL
SELECT 'payment',         COUNT(*) FROM payment
UNION ALL
SELECT 'shipping_details',COUNT(*) FROM shipping_details
UNION ALL
SELECT 'book_author',     COUNT(*) FROM book_author
UNION ALL
SELECT 'genre',           COUNT(*) FROM genre;
