-- ============================================================
--  BookUrTrim – PostgreSQL Schema
--  Generated from the architecture design document v1.0
-- ============================================================

-- ────────────────────────────────────────────────────────────
--  Extensions
-- ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS unaccent;

-- ────────────────────────────────────────────────────────────
--  ENUM TYPES
-- ────────────────────────────────────────────────────────────
CREATE TYPE appointment_status  AS ENUM ('confirmed', 'cancelled', 'completed', 'pending');
CREATE TYPE payment_type        AS ENUM ('deposit', 'balance');
CREATE TYPE payment_status      AS ENUM ('pending', 'validated');
CREATE TYPE availability_type   AS ENUM ('work', 'break');
CREATE TYPE notification_type   AS ENUM ('confirmation', 'reminder', 'schedule_change');
CREATE TYPE recipient_type      AS ENUM ('client', 'provider');

-- ────────────────────────────────────────────────────────────
--  TABLE : client
-- ────────────────────────────────────────────────────────────
CREATE TABLE client (
    id                   SERIAL          PRIMARY KEY,
    last_name            VARCHAR(100)    NOT NULL,
    first_name           VARCHAR(100)    NOT NULL,
    email                VARCHAR(255)    NOT NULL,
    phone                VARCHAR(20),
    gender               VARCHAR(50),
    hair_length          VARCHAR(50),
    hair_type            VARCHAR(50),
    history_preferences  TEXT,
    stripe_customer_id   VARCHAR(255),                         -- Stripe Customer object (cus_...)
    created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_client_email          UNIQUE (email),
    CONSTRAINT uq_client_stripe_cus     UNIQUE (stripe_customer_id)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : provider
-- ────────────────────────────────────────────────────────────
CREATE TABLE provider (
    id                       SERIAL          PRIMARY KEY,
    last_name                VARCHAR(100)    NOT NULL,
    first_name               VARCHAR(100)    NOT NULL,
    email                    VARCHAR(255)    NOT NULL,
    phone                    VARCHAR(20),
    google_calendar_token    VARCHAR(255),
    created_at               TIMESTAMP       NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_provider_email UNIQUE (email)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : service
-- ────────────────────────────────────────────────────────────
CREATE TABLE service (
    id                   SERIAL          PRIMARY KEY,
    provider_id          INT             NOT NULL,
    name                 VARCHAR(150)    NOT NULL,
    description          TEXT,
    default_duration     INT             NOT NULL CHECK (default_duration > 0), -- in minutes
    base_price           DECIMAL(10,2)   NOT NULL CHECK (base_price >= 0),
    created_at           TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_service_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : availability
-- ────────────────────────────────────────────────────────────
CREATE TABLE availability (
    id                   SERIAL              PRIMARY KEY,
    provider_id          INT                 NOT NULL,
    day_date             DATE                NOT NULL,
    start_time           TIME                NOT NULL,
    end_time             TIME                NOT NULL,
    slot_type            availability_type   NOT NULL DEFAULT 'work',

    CONSTRAINT fk_availability_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_availability_times CHECK (end_time > start_time)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : appointment
-- ────────────────────────────────────────────────────────────
CREATE TABLE appointment (
    id                   SERIAL              PRIMARY KEY,
    client_id            INT                 NOT NULL,
    provider_id          INT                 NOT NULL,
    start_at             TIMESTAMP           NOT NULL,
    end_at               TIMESTAMP           NOT NULL,
    status               appointment_status  NOT NULL DEFAULT 'pending',
    products_used        TEXT,
    specific_request     TEXT,
    created_at           TIMESTAMP           NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMP           NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_appointment_client
        FOREIGN KEY (client_id) REFERENCES client (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_appointment_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_appointment_times CHECK (end_at > start_at)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : appointment_service  (appointment ↔ service)
-- ────────────────────────────────────────────────────────────
CREATE TABLE appointment_service (
    appointment_id       INT             NOT NULL,
    service_id           INT             NOT NULL,
    adjusted_duration    INT             CHECK (adjusted_duration > 0), -- may differ from default_duration
    billed_price         DECIMAL(10,2)   NOT NULL CHECK (billed_price >= 0),

    CONSTRAINT pk_appointment_service PRIMARY KEY (appointment_id, service_id),

    CONSTRAINT fk_appsvc_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_appsvc_service
        FOREIGN KEY (service_id) REFERENCES service (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : payment
-- ────────────────────────────────────────────────────────────
CREATE TABLE payment (
    id                         SERIAL          PRIMARY KEY,
    appointment_id             INT             NOT NULL,
    amount                     DECIMAL(10,2)   NOT NULL CHECK (amount > 0),
    currency                   CHAR(3)         NOT NULL DEFAULT 'eur',  -- ISO 4217
    payment_type               payment_type    NOT NULL,
    status                     payment_status  NOT NULL DEFAULT 'pending',
    paid_at                    TIMESTAMP       NOT NULL DEFAULT NOW(),

    -- Stripe
    stripe_payment_intent_id   VARCHAR(255),   -- pi_...  source of truth
    stripe_charge_id           VARCHAR(255),   -- ch_...  used for refunds
    stripe_metadata            JSONB,          -- free data from Stripe webhooks

    CONSTRAINT fk_payment_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_stripe_payment_intent UNIQUE (stripe_payment_intent_id),
    CONSTRAINT uq_stripe_charge         UNIQUE (stripe_charge_id)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : invoice
-- ────────────────────────────────────────────────────────────
CREATE TABLE invoice (
    id                   SERIAL          PRIMARY KEY,
    appointment_id       INT             NOT NULL,
    issued_at            TIMESTAMP       NOT NULL DEFAULT NOW(),
    total_amount         DECIMAL(10,2)   NOT NULL CHECK (total_amount >= 0),
    pdf_url              VARCHAR(255),

    CONSTRAINT uq_invoice_appointment UNIQUE (appointment_id),

    CONSTRAINT fk_invoice_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : review
-- ────────────────────────────────────────────────────────────
CREATE TABLE review (
    id                   SERIAL          PRIMARY KEY,
    appointment_id       INT             NOT NULL,
    provider_id          INT             NOT NULL,
    rating               SMALLINT        NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment              TEXT,
    reviewed_at          TIMESTAMP       NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_review_appointment UNIQUE (appointment_id),

    CONSTRAINT fk_review_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_review_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : notification
-- ────────────────────────────────────────────────────────────
CREATE TABLE notification (
    id                   SERIAL              PRIMARY KEY,
    appointment_id       INT                 NOT NULL,
    recipient            recipient_type      NOT NULL,
    notification_type    notification_type   NOT NULL,
    sent_at              TIMESTAMP           NOT NULL DEFAULT NOW(),
    status               VARCHAR(50)         NOT NULL DEFAULT 'sent',

    CONSTRAINT fk_notification_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
--  INDEXES
-- ============================================================

-- Client lookups
CREATE INDEX idx_client_email               ON client       (email);
CREATE INDEX idx_client_stripe_customer     ON client       (stripe_customer_id);

-- Provider lookups
CREATE INDEX idx_provider_email             ON provider     (email);

-- Services by provider
CREATE INDEX idx_service_provider           ON service      (provider_id);

-- Availability: time-based filters
CREATE INDEX idx_availability_provider      ON availability (provider_id, day_date);

-- Appointments: frequent filters
CREATE INDEX idx_appointment_client         ON appointment  (client_id);
CREATE INDEX idx_appointment_provider       ON appointment  (provider_id);
CREATE INDEX idx_appointment_start          ON appointment  (start_at);
CREATE INDEX idx_appointment_status         ON appointment  (status);

-- Payments
CREATE INDEX idx_payment_appointment        ON payment      (appointment_id);
CREATE INDEX idx_payment_stripe_intent      ON payment      (stripe_payment_intent_id);
CREATE INDEX idx_payment_stripe_charge      ON payment      (stripe_charge_id);

-- Reviews: average rating per provider
CREATE INDEX idx_review_provider            ON review       (provider_id);

-- Notifications
CREATE INDEX idx_notification_appointment   ON notification (appointment_id);
CREATE INDEX idx_notification_sent_at       ON notification (sent_at DESC);

-- ============================================================
--  TRIGGER : auto-update updated_at
-- ============================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_client_updated_at
    BEFORE UPDATE ON client
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_provider_updated_at
    BEFORE UPDATE ON provider
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_appointment_updated_at
    BEFORE UPDATE ON appointment
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();