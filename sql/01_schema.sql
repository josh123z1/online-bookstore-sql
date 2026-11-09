-- WBS Online Bookstore: SQLite schema (DDL)
-- 9 tables, normalised to 3NF

PRAGMA foreign_keys = ON;


-- ============================================================
-- Lookup & Catalogue Tables
-- ============================================================

CREATE TABLE genre (
  genre_id   INTEGER PRIMARY KEY,
  genre_name TEXT NOT NULL UNIQUE
);

CREATE TABLE customer (
  customer_id INTEGER PRIMARY KEY,
  first_name  TEXT NOT NULL,
  last_name   TEXT NOT NULL,
  email       TEXT NOT NULL UNIQUE,
  join_date   TEXT NOT NULL,
  phone       TEXT,
  country     TEXT NOT NULL
);

CREATE TABLE author (
  author_id   INTEGER PRIMARY KEY,
  author_name TEXT NOT NULL
);

CREATE TABLE book (
  book_id        INTEGER PRIMARY KEY,
  isbn           TEXT NOT NULL UNIQUE,
  title          TEXT NOT NULL,
  publish_year   INTEGER CHECK (publish_year BETWEEN 1800 AND 2026),
  list_price     REAL NOT NULL CHECK (list_price > 0),
  stock_quantity INTEGER NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
  genre_id       INTEGER NOT NULL,
  FOREIGN KEY (genre_id) REFERENCES genre(genre_id)
);


-- ============================================================
-- Junction & Transaction Tables
-- ============================================================

CREATE TABLE book_author (
  book_id   INTEGER NOT NULL,
  author_id INTEGER NOT NULL,
  PRIMARY KEY (book_id, author_id),
  FOREIGN KEY (book_id)   REFERENCES book(book_id),
  FOREIGN KEY (author_id) REFERENCES author(author_id)
);

CREATE TABLE orders (
  order_id     INTEGER PRIMARY KEY,
  customer_id  INTEGER NOT NULL,
  order_date   TEXT NOT NULL,
  order_status TEXT NOT NULL CHECK (order_status IN ('Pending','Paid','Shipped','Delivered','Cancelled','Returned')),
  total_amount REAL NOT NULL CHECK (total_amount >= 0),
  FOREIGN KEY (customer_id) REFERENCES customer(customer_id)
);

CREATE TABLE order_item (
  order_id   INTEGER NOT NULL,
  book_id    INTEGER NOT NULL,
  quantity   INTEGER NOT NULL CHECK (quantity > 0),
  unit_price REAL NOT NULL CHECK (unit_price > 0),
  PRIMARY KEY (order_id, book_id),
  FOREIGN KEY (order_id) REFERENCES orders(order_id),
  FOREIGN KEY (book_id)  REFERENCES book(book_id)
);


-- ============================================================
-- Payment & Shipping Tables
-- ============================================================

CREATE TABLE payment (
  payment_id     INTEGER PRIMARY KEY,
  order_id       INTEGER NOT NULL UNIQUE,
  payment_date   TEXT NOT NULL,
  payment_method TEXT NOT NULL,
  amount         REAL NOT NULL CHECK (amount >= 0),
  payment_status TEXT NOT NULL CHECK (payment_status IN ('Success','Failed','Pending','Refunded')),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

CREATE TABLE shipping_details (
  shipping_id      INTEGER PRIMARY KEY,
  order_id         INTEGER NOT NULL UNIQUE,
  recipient_name   TEXT NOT NULL,
  shipping_address TEXT NOT NULL,
  city             TEXT NOT NULL,
  postal_code      TEXT NOT NULL,
  country          TEXT NOT NULL,
  shipping_method  TEXT NOT NULL,
  shipping_cost    REAL NOT NULL DEFAULT 0 CHECK (shipping_cost >= 0),
  shipped_date     TEXT,
  delivery_date    TEXT,
  shipping_status  TEXT NOT NULL CHECK (shipping_status IN ('Not Shipped','Shipped','Delivered','Cancelled','Returned')),
  FOREIGN KEY (order_id) REFERENCES orders(order_id)
);
