-- ============================================================
-- ASG Airlines — Star Schema DDL
-- Load target for the curated CSVs in data/curated/
-- Dialect: ANSI SQL (tested against PostgreSQL syntax; adjust
-- data types trivially for SQL Server / Synapse / MySQL)
-- ============================================================

-- ---------- Dimensions ----------

CREATE TABLE dim_airline (
    airline_key     VARCHAR(6)   PRIMARY KEY,
    airline         VARCHAR(50)  NOT NULL
);

CREATE TABLE dim_route (
    route_key       VARCHAR(6)   PRIMARY KEY,
    source          VARCHAR(5)   NOT NULL,
    destination     VARCHAR(5)   NOT NULL,
    route           VARCHAR(20)  NOT NULL
);

CREATE TABLE dim_date (
    date_key        CHAR(8)      PRIMARY KEY,   -- YYYYMMDD
    date            DATE         NOT NULL,
    year            INT          NOT NULL,
    month           INT          NOT NULL,
    month_name      VARCHAR(15)  NOT NULL,
    day             INT          NOT NULL,
    day_name        VARCHAR(15)  NOT NULL,
    is_weekend      BOOLEAN      NOT NULL
);

CREATE TABLE dim_passenger (
    passenger_id        VARCHAR(10) PRIMARY KEY,
    first_name           VARCHAR(50),
    last_name            VARCHAR(50),
    age                  INT,
    gender               VARCHAR(5),
    date_of_birth        DATE,
    quality_flag         VARCHAR(30),
    aadhaar_id_hash       VARCHAR(20),   -- SHA-256 truncated hash, not reversible
    phone_masked         VARCHAR(20),   -- partially masked, e.g. 9198******12
    email_masked         VARCHAR(60)    -- partially masked, e.g. j***@gmail.com
);

-- ---------- Facts ----------

CREATE TABLE fact_flights (
    flight_key              VARCHAR(8)   PRIMARY KEY,
    flight_id               VARCHAR(10)  NOT NULL,
    airline_key              VARCHAR(6)   REFERENCES dim_airline(airline_key),
    route_key                VARCHAR(6)   REFERENCES dim_route(route_key),
    date_key                 CHAR(8)      REFERENCES dim_date(date_key),
    departure_time            TIMESTAMP    NOT NULL,
    arrival_time              TIMESTAMP    NOT NULL,
    arrival_time_adjusted      TIMESTAMP    NOT NULL,
    duration_minutes          NUMERIC(6,2) NOT NULL,
    is_overnight               BOOLEAN      NOT NULL,
    duration_status            VARCHAR(15)  NOT NULL,   -- VALID / SUSPICIOUS
    anomaly_flag               VARCHAR(10)  NOT NULL,   -- NORMAL / ANOMALY
    airline_quality_flag       VARCHAR(30)  NOT NULL
);

CREATE TABLE fact_bookings (
    booking_id                       VARCHAR(10)  PRIMARY KEY,
    passenger_id                     VARCHAR(10)  REFERENCES dim_passenger(passenger_id),
    flight_key                       VARCHAR(8)   REFERENCES fact_flights(flight_key),
    flight_id                        VARCHAR(10),
    booking_date                      TIMESTAMP,
    status                            VARCHAR(15),           -- CONFIRMED / CANCELLED / PENDING / UNKNOWN
    status_quality_flag               VARCHAR(30),
    seat_number                       VARCHAR(5),
    passport_number_hash               VARCHAR(20),
    emergency_contact_name_masked      VARCHAR(5),
    emergency_contact_phone_masked     VARCHAR(20)
);

CREATE TABLE fact_payments (
    payment_id       VARCHAR(10)  PRIMARY KEY,
    booking_id       VARCHAR(10)  REFERENCES fact_bookings(booking_id),
    amount            NUMERIC(10,2) NOT NULL CHECK (amount > 0),
    payment_method    VARCHAR(15)
);

-- ---------- Quarantine (rejected records, preserved not deleted) ----------

CREATE TABLE quarantine_flights (
    row_ref              INT,
    flight_id             VARCHAR(20),
    airline               VARCHAR(50),
    source                VARCHAR(20),
    destination           VARCHAR(20),
    departure_time         TIMESTAMP,
    arrival_time           TIMESTAMP,
    reason_description      VARCHAR(200),
    validation_status       VARCHAR(15)
);

CREATE TABLE quarantine_payments (
    payment_id       VARCHAR(10),
    booking_id       VARCHAR(10),
    amount            VARCHAR(20),   -- kept as text since the raw value may be non-numeric ('INVALID')
    payment_method    VARCHAR(15),
    reason_code        VARCHAR(30),
    validation_status  VARCHAR(15)
);
