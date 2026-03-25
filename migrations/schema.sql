CREATE DATABASE IF NOT EXISTS stockbit_data CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stockbit_data;

-- Daftar saham yang ditrack
CREATE TABLE IF NOT EXISTS tickers (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    symbol      VARCHAR(10)  NOT NULL UNIQUE,
    company_name VARCHAR(255) DEFAULT NULL,
    sector      VARCHAR(100) DEFAULT NULL,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Snapshot fundamental per hari
CREATE TABLE IF NOT EXISTS fundamental_data (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol        VARCHAR(10)  NOT NULL,
    fetched_at    DATETIME     NOT NULL,

    -- Valuation
    pe_ratio      DECIMAL(12,4) DEFAULT NULL,   -- P/E TTM
    pe_annual     DECIMAL(12,4) DEFAULT NULL,
    forward_pe    DECIMAL(12,4) DEFAULT NULL,
    pb_ratio      DECIMAL(12,4) DEFAULT NULL,   -- P/B
    ps_ratio      DECIMAL(12,4) DEFAULT NULL,
    ev_ebitda     DECIMAL(12,4) DEFAULT NULL,
    peg           DECIMAL(12,4) DEFAULT NULL,

    -- Per Share
    eps_ttm       DECIMAL(12,4) DEFAULT NULL,
    eps_annual    DECIMAL(12,4) DEFAULT NULL,
    bvps          DECIMAL(12,4) DEFAULT NULL,   -- Book Value per Share
    revenue_per_share DECIMAL(12,4) DEFAULT NULL,

    -- Solvency
    current_ratio DECIMAL(12,4) DEFAULT NULL,
    der           DECIMAL(12,4) DEFAULT NULL,   -- Debt to Equity
    debt_to_assets DECIMAL(12,4) DEFAULT NULL,

    -- Profitability
    gross_margin  DECIMAL(8,4)  DEFAULT NULL,   -- %
    op_margin     DECIMAL(8,4)  DEFAULT NULL,
    net_margin    DECIMAL(8,4)  DEFAULT NULL,

    -- Management Effectiveness
    roe           DECIMAL(8,4)  DEFAULT NULL,   -- %
    roa           DECIMAL(8,4)  DEFAULT NULL,
    roic          DECIMAL(8,4)  DEFAULT NULL,

    -- Growth
    revenue_qoq   DECIMAL(8,4)  DEFAULT NULL,   -- %
    revenue_yoy   DECIMAL(8,4)  DEFAULT NULL,
    net_income_qoq DECIMAL(8,4) DEFAULT NULL,
    net_income_yoy DECIMAL(8,4) DEFAULT NULL,

    -- Dividend
    dividend_yield DECIMAL(8,4) DEFAULT NULL,
    payout_ratio   DECIMAL(8,4) DEFAULT NULL,

    -- Market
    market_cap     DECIMAL(20,2) DEFAULT NULL,
    enterprise_value DECIMAL(20,2) DEFAULT NULL,

    -- Piotroski
    piotroski_score TINYINT     DEFAULT NULL,

    raw_json      LONGTEXT      DEFAULT NULL,   -- simpan response mentah

    INDEX idx_symbol_date (symbol, fetched_at)
);

-- Harga real-time snapshot
CREATE TABLE IF NOT EXISTS price_data (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol        VARCHAR(10)  NOT NULL,
    fetched_at    DATETIME     NOT NULL,

    last_price    DECIMAL(12,2) DEFAULT NULL,
    open_price    DECIMAL(12,2) DEFAULT NULL,
    high_price    DECIMAL(12,2) DEFAULT NULL,
    low_price     DECIMAL(12,2) DEFAULT NULL,
    close_price   DECIMAL(12,2) DEFAULT NULL,
    volume        BIGINT        DEFAULT NULL,
    frequency     INT           DEFAULT NULL,
    change_val    DECIMAL(12,2) DEFAULT NULL,
    change_pct    DECIMAL(8,4)  DEFAULT NULL,

    week52_high   DECIMAL(12,2) DEFAULT NULL,
    week52_low    DECIMAL(12,2) DEFAULT NULL,

    INDEX idx_symbol_date (symbol, fetched_at)
);
