CREATE TABLE IF NOT EXISTS customers (
    customer_id BIGINT PRIMARY KEY,
    customer_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL,
    price NUMERIC(12, 2) NOT NULL CHECK (price >= 0)
);

CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT PRIMARY KEY,
    customer_id BIGINT NOT NULL REFERENCES customers (customer_id),
    order_date TIMESTAMPTZ NOT NULL,
    status TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS order_items (
    order_id BIGINT NOT NULL REFERENCES orders (order_id),
    line_number INTEGER NOT NULL,
    product_id BIGINT NOT NULL REFERENCES products (product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, line_number)
);