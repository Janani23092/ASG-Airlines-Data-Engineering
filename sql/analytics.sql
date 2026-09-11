-- ============================================================
-- ASG Airlines — Analytics / KPI queries
-- Run against the star schema created in schema.sql, loaded
-- from data/curated/*.csv
-- ============================================================

-- 1. Total Flights
SELECT COUNT(*) AS total_flights
FROM fact_flights;

-- 2. Average Flight Duration (valid records only)
SELECT ROUND(AVG(duration_minutes), 2) AS avg_duration_minutes
FROM fact_flights
WHERE duration_status = 'VALID';

-- 3. Route-wise Traffic (top routes by flight count)
SELECT r.route, COUNT(*) AS flight_count
FROM fact_flights f
JOIN dim_route r ON f.route_key = r.route_key
GROUP BY r.route
ORDER BY flight_count DESC;

-- 4. Airline Distribution
SELECT a.airline, COUNT(*) AS flight_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_share
FROM fact_flights f
JOIN dim_airline a ON f.airline_key = a.airline_key
GROUP BY a.airline
ORDER BY flight_count DESC;

-- 5. Delay / Anomaly rate
SELECT
    SUM(CASE WHEN anomaly_flag = 'ANOMALY' THEN 1 ELSE 0 END) AS anomaly_count,
    COUNT(*) AS total_flights,
    ROUND(100.0 * SUM(CASE WHEN anomaly_flag = 'ANOMALY' THEN 1 ELSE 0 END) / COUNT(*), 2) AS anomaly_rate_pct
FROM fact_flights;

-- 6. Overnight flight share
SELECT
    SUM(CASE WHEN is_overnight THEN 1 ELSE 0 END) AS overnight_flights,
    ROUND(100.0 * SUM(CASE WHEN is_overnight THEN 1 ELSE 0 END) / COUNT(*), 2) AS overnight_share_pct
FROM fact_flights;

-- 7. Average duration by route
SELECT r.route, ROUND(AVG(f.duration_minutes), 2) AS avg_duration_minutes, COUNT(*) AS flight_count
FROM fact_flights f
JOIN dim_route r ON f.route_key = r.route_key
WHERE f.duration_status = 'VALID'
GROUP BY r.route
ORDER BY avg_duration_minutes DESC;

-- 8. Revenue by payment method (confirmed bookings only)
SELECT p.payment_method, ROUND(SUM(p.amount), 2) AS total_revenue, COUNT(*) AS payment_count
FROM fact_payments p
JOIN fact_bookings b ON p.booking_id = b.booking_id
WHERE b.status = 'CONFIRMED'
GROUP BY p.payment_method
ORDER BY total_revenue DESC;

-- 9. Booking status breakdown
SELECT status, COUNT(*) AS booking_count
FROM fact_bookings
GROUP BY status
ORDER BY booking_count DESC;

-- 10. Data quality / quarantine summary
SELECT reason_description, COUNT(*) AS record_count
FROM quarantine_flights
GROUP BY reason_description
ORDER BY record_count DESC;
