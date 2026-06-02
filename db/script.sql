-- ============================================================
--  BookUrTrim – PostgreSQL Schema  v1.1
-- ============================================================

-- ────────────────────────────────────────────────────────────
--  Extensions
-- ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- exclusion constraints on availability

-- ────────────────────────────────────────────────────────────
--  ENUM TYPES
-- ────────────────────────────────────────────────────────────
CREATE TYPE user_role           AS ENUM ('client', 'provider');
CREATE TYPE appointment_status  AS ENUM ('confirmed', 'cancelled', 'completed', 'pending', 'expired');
CREATE TYPE payment_type        AS ENUM ('deposit', 'balance');
CREATE TYPE payment_status      AS ENUM ('pending', 'validated', 'failed', 'refunded');
CREATE TYPE availability_type   AS ENUM ('work', 'break', 'booked');
CREATE TYPE notification_type   AS ENUM ('confirmation', 'reminder', 'schedule_change');
CREATE TYPE notification_status AS ENUM ('pending', 'sent', 'failed');
CREATE TYPE recipient_type      AS ENUM ('client', 'provider');
CREATE TYPE hair_type           AS ENUM ('lisse', 'ondulé', 'bouclé', 'crépu fin', 'crépu épais');
CREATE TYPE hair_length         AS ENUM ('court', 'mi-long', 'long', 'très long');

-- ────────────────────────────────────────────────────────────
--  TABLE : user_account  (authentication)
-- ────────────────────────────────────────────────────────────
CREATE TABLE user_account (
    id              BIGSERIAL       PRIMARY KEY,
    email           VARCHAR(255)    NOT NULL,
    password_hash   VARCHAR(255)    NOT NULL,
    role            user_role       NOT NULL,
    is_active       BOOLEAN         NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_user_email UNIQUE (email)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : client
-- ────────────────────────────────────────────────────────────
CREATE TABLE client (
    id                   BIGSERIAL       PRIMARY KEY,
    user_account_id      BIGINT          NOT NULL,
    last_name            VARCHAR(100)    NOT NULL,
    first_name           VARCHAR(100)    NOT NULL,
    phone                VARCHAR(20),
    gender               VARCHAR(50),
    hair_length          VARCHAR(50),
    hair_type            VARCHAR(50),
    history_preferences  TEXT,
    stripe_customer_id   VARCHAR(255),
    created_at           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_client_user
        FOREIGN KEY (user_account_id) REFERENCES user_account (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_client_user       UNIQUE (user_account_id),
    CONSTRAINT uq_client_stripe_cus UNIQUE (stripe_customer_id)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : client_hair_profile
-- ────────────────────────────────────────────────────────────
CREATE TABLE client_hair_profile (
    id           BIGSERIAL    PRIMARY KEY,
    client_id    BIGINT       NOT NULL,
    hair_type    hair_type    NOT NULL,
    hair_length  hair_length  NOT NULL,

    CONSTRAINT fk_hair_profile_client
        FOREIGN KEY (client_id) REFERENCES client (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT uq_hair_profile_client UNIQUE (client_id)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : provider
-- ────────────────────────────────────────────────────────────
CREATE TABLE provider (
    id                          BIGSERIAL       PRIMARY KEY,
    user_account_id             BIGINT          NOT NULL,
    last_name                   VARCHAR(100)    NOT NULL,
    first_name                  VARCHAR(100)    NOT NULL,
    phone                       VARCHAR(20),
    business_name               VARCHAR(150),
    address                     VARCHAR(255),
    -- token must be AES-256 encrypted by the application before storage
    google_calendar_token_enc   TEXT,
    stripe_account_id           VARCHAR(255)    UNIQUE,
    created_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_provider_user
        FOREIGN KEY (user_account_id) REFERENCES user_account (id)
        ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT uq_provider_user UNIQUE (user_account_id)
);

-- ────────────────────────────────────────────────────────────
--  TABLE : service
-- ────────────────────────────────────────────────────────────
CREATE TABLE service (
    id                   BIGSERIAL       PRIMARY KEY,
    provider_id          BIGINT          NOT NULL,
    name                 VARCHAR(150)    NOT NULL,
    description          TEXT,
    default_duration     INT             NOT NULL CHECK (default_duration > 0),  -- minutes
    base_price           DECIMAL(10,2)   NOT NULL CHECK (base_price >= 0),
    created_at           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_service_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : service_question
-- ────────────────────────────────────────────────────────────
CREATE TABLE service_question (
    id           BIGSERIAL   PRIMARY KEY,
    service_id   BIGINT      NOT NULL,
    question     TEXT        NOT NULL,
    options      JSONB       NOT NULL DEFAULT '[]',
    "order"      INT         NOT NULL DEFAULT 0,

    CONSTRAINT fk_question_service
        FOREIGN KEY (service_id) REFERENCES service (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : availability
-- ────────────────────────────────────────────────────────────
CREATE TABLE availability (
    id                   BIGSERIAL           PRIMARY KEY,
    provider_id          BIGINT              NOT NULL,
    day_date             DATE                NOT NULL,
    start_time           TIME                NOT NULL,
    end_time             TIME                NOT NULL,
    slot_type            availability_type   NOT NULL DEFAULT 'work',
    created_at           TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ         NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_availability_provider
        FOREIGN KEY (provider_id) REFERENCES provider (id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT chk_availability_times CHECK (end_time > start_time),

    -- prevents overlapping slots for the same provider on the same day
    CONSTRAINT excl_availability_no_overlap
        EXCLUDE USING gist (
            provider_id WITH =,
            tsrange(
                (day_date + start_time)::TIMESTAMP,
                (day_date + end_time)::TIMESTAMP
            ) WITH &&
        )
);

-- ────────────────────────────────────────────────────────────
--  TABLE : appointment
-- ────────────────────────────────────────────────────────────
CREATE TABLE appointment (
    id                   BIGSERIAL           PRIMARY KEY,
    client_id            BIGINT              NOT NULL,
    provider_id          BIGINT              NOT NULL,
    start_at             TIMESTAMPTZ         NOT NULL,
    end_at               TIMESTAMPTZ         NOT NULL,
    status               appointment_status  NOT NULL DEFAULT 'pending',
    products_used        TEXT,
    specific_request     TEXT,
    answers              JSONB,
    created_at           TIMESTAMPTZ         NOT NULL DEFAULT NOW(),
    updated_at           TIMESTAMPTZ         NOT NULL DEFAULT NOW(),

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
    appointment_id       BIGINT          NOT NULL,
    service_id           BIGINT          NOT NULL,
    adjusted_duration    INT             CHECK (adjusted_duration > 0),  -- may differ from default_duration
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
    id                         BIGSERIAL       PRIMARY KEY,
    appointment_id             BIGINT          NOT NULL,
    amount                     DECIMAL(10,2)   NOT NULL CHECK (amount > 0),
    currency                   CHAR(3)         NOT NULL DEFAULT 'eur',  -- ISO 4217
    payment_type               payment_type    NOT NULL,
    status                     payment_status  NOT NULL DEFAULT 'pending',
    paid_at                    TIMESTAMPTZ,    -- NULL until payment confirmed by Stripe webhook

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
    id                   BIGSERIAL       PRIMARY KEY,
    appointment_id       BIGINT          NOT NULL,
    issued_at            TIMESTAMPTZ     NOT NULL DEFAULT NOW(),
    total_amount         DECIMAL(10,2)   NOT NULL CHECK (total_amount >= 0),
    pdf_url              VARCHAR(255),

    CONSTRAINT uq_invoice_appointment UNIQUE (appointment_id),

    CONSTRAINT fk_invoice_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : review
--  provider_id removed: derive provider via appointment to avoid inconsistency
-- ────────────────────────────────────────────────────────────
CREATE TABLE review (
    id                   BIGSERIAL       PRIMARY KEY,
    appointment_id       BIGINT          NOT NULL,
    rating               SMALLINT        NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment              TEXT,
    reviewed_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_review_appointment UNIQUE (appointment_id),

    CONSTRAINT fk_review_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ────────────────────────────────────────────────────────────
--  TABLE : notification
-- ────────────────────────────────────────────────────────────
CREATE TABLE notification (
    id                   BIGSERIAL               PRIMARY KEY,
    appointment_id       BIGINT                  NOT NULL,
    recipient            recipient_type          NOT NULL,
    notification_type    notification_type       NOT NULL,
    sent_at              TIMESTAMPTZ             NOT NULL DEFAULT NOW(),
    status               notification_status     NOT NULL DEFAULT 'pending',

    CONSTRAINT fk_notification_appointment
        FOREIGN KEY (appointment_id) REFERENCES appointment (id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ============================================================
--  INDEXES
-- ============================================================

-- User / auth
CREATE INDEX idx_user_email                 ON user_account (email);

-- Client
CREATE INDEX idx_client_user_account        ON client       (user_account_id);
CREATE INDEX idx_client_stripe_customer     ON client       (stripe_customer_id);

-- Provider
CREATE INDEX idx_provider_user_account      ON provider     (user_account_id);

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

-- Reviews: provider derived via appointment join on idx_appointment_provider
CREATE INDEX idx_review_appointment         ON review       (appointment_id);

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

CREATE TRIGGER trg_user_account_updated_at
    BEFORE UPDATE ON user_account
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_client_updated_at
    BEFORE UPDATE ON client
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_provider_updated_at
    BEFORE UPDATE ON provider
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_service_updated_at
    BEFORE UPDATE ON service
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_availability_updated_at
    BEFORE UPDATE ON availability
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TRIGGER trg_appointment_updated_at
    BEFORE UPDATE ON appointment
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();
