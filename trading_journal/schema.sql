-- DuckDB schema definition for the trading journal

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    date DATE,
    symbol TEXT,
    quantity INTEGER,
    price DOUBLE,
    side TEXT
);
