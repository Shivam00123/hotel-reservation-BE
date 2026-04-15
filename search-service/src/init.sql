-- Use existing DB (created by MYSQL_DATABASE)

SET SESSION cte_max_recursion_depth = 2000;
USE `hotel-search`;

-- =========================
-- 1. TABLES
-- =========================

CREATE TABLE IF NOT EXISTS hotels (
    id INT AUTO_INCREMENT PRIMARY KEY,

    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),

    name VARCHAR(255),
    total_rooms INT,
    thumbnail VARCHAR(255),
    rating FLOAT,
    status ENUM('Open', 'Closed') DEFAULT 'Open',
    reserved_rooms INT,

    INDEX idx_location (country, state, city)
);

CREATE TABLE IF NOT EXISTS rooms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hotel_id INT,
    floor INT,
    max_adults INT,
    max_children INT,
    price DECIMAL(10,2),

    FOREIGN KEY (hotel_id) REFERENCES hotels(id)
);

-- =========================
-- 2. INSERT HOTELS (1000)
-- =========================

INSERT INTO hotels (
    country, state, city, name,
    total_rooms, thumbnail, rating,
    status, reserved_rooms
)
WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 1000
)
SELECT
    'India',

    ELT(FLOOR(1 + (RAND() * 5)),
        'Rajasthan', 'Maharashtra', 'Karnataka', 'Delhi', 'Gujarat'
    ),

    ELT(FLOOR(1 + (RAND() * 5)),
        'Udaipur', 'Mumbai', 'Bangalore', 'Delhi', 'Ahmedabad'
    ),

    CONCAT('Hotel_', n),

    FLOOR(50 + (RAND() * 100)),                 -- total_rooms (50–150)
    'https://example.com/image.jpg',

    ROUND(2 + (RAND() * 3), 1),                 -- rating (2.0–5.0)

    ELT(FLOOR(1 + (RAND() * 2)), 'Open', 'Closed'),

    FLOOR(RAND() * 50)                          -- reserved_rooms

FROM seq;

-- =========================
-- 3. INSERT ROOMS (1500)
-- =========================

INSERT INTO rooms (
    hotel_id,
    floor,
    max_adults,
    max_children,
    price
)
WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 1500
)
SELECT
    FLOOR(1 + (RAND() * 1000)),                 -- valid hotel_id

    FLOOR(1 + (RAND() * 10)),                  -- floor (1–10)
    FLOOR(1 + (RAND() * 4)),                   -- max_adults (1–4)
    FLOOR(RAND() * 3),                         -- max_children (0–2)

    ROUND(1000 + (RAND() * 9000), 2)           -- price (1000–10000)

FROM seq;