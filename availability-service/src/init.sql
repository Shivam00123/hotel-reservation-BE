USE `hotel-inventory`;

SET SESSION cte_max_recursion_depth = 5000;

CREATE TABLE IF NOT EXISTS hotel_inventory (
    id INT PRIMARY KEY AUTO_INCREMENT,
    hotel_id INT,
    room_id INT,
    available BOOLEAN,
    startDate DATE,
    endDate DATE
);

-- =========================
-- INSERT HOTEL INVENTORY (3000)
-- =========================

INSERT INTO hotel_inventory (
    hotel_id,
    room_id,
    available,
    startDate,
    endDate
)
WITH RECURSIVE seq AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM seq WHERE n < 3000
)
SELECT
    seeded.hotel_id,
    seeded.room_id,
    seeded.available,
    seeded.startDate,
    DATE_ADD(seeded.startDate, INTERVAL seeded.stay_nights DAY) AS endDate
FROM (
    SELECT
        FLOOR(1 + (RAND() * 1000)) AS hotel_id,        -- hotel_id 1..1000
        FLOOR(1 + (RAND() * 1500)) AS room_id,         -- room_id 1..1500
        FLOOR(RAND() * 2) AS available,                -- 0 or 1
        DATE_ADD(
            CURDATE(),
            INTERVAL (FLOOR(RAND() * 120) - 60) DAY
        ) AS startDate,                                -- +/- 60 days from today
        FLOOR(1 + (RAND() * 7)) AS stay_nights         -- 1..7 nights
    FROM seq
) AS seeded;