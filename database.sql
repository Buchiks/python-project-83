CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at DATE DEFAULT CURRENT_DATE
    );

CREATE TABLE url_checks (
    id SERIAL PRIMARY KEY,
    url_id bigint REFERENCES urls (id),
    status_code INTEGER,
    h1 TEXT,
    title VARCHAR(255),
    description TEXT,
    created_at DATE DEFAULT CURRENT_DATE
    );