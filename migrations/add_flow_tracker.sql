USE stockbit_data;

-- Rekapan Bandarmologi Harian dari Stockbit (Market Detector)
CREATE TABLE IF NOT EXISTS market_detector_summary (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol        VARCHAR(10)  NOT NULL,
    date          DATE         NOT NULL,
    accdist_status VARCHAR(50) DEFAULT NULL, -- contoh: "Normal Dist", "Big Acc"
    amount        BIGINT       DEFAULT NULL,
    percent       DECIMAL(12,4) DEFAULT NULL,
    broker_accdist VARCHAR(50) DEFAULT NULL, -- contoh: "Dist", "Acc"
    total_buyer   INT          DEFAULT NULL,
    total_seller  INT          DEFAULT NULL,
    total_volume  BIGINT       DEFAULT NULL,
    total_value   BIGINT       DEFAULT NULL,
    fetched_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY idx_symbol_date (symbol, date)
);

-- Transaksi Broker Harian (Rincian Beli/Jual per broker)
CREATE TABLE IF NOT EXISTS broker_transaction_daily (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol        VARCHAR(10)  NOT NULL,
    date          DATE         NOT NULL,
    broker_code   VARCHAR(10)  NOT NULL,
    broker_type   VARCHAR(50)  DEFAULT NULL, -- Lokal / Asing / Pemerintah
    is_buyer      BOOLEAN      NOT NULL,     -- TRUE kalau beli, FALSE kalau jual
    lot           BIGINT       NOT NULL,     -- net quantity
    val           BIGINT       NOT NULL,     -- net value (Rupiah)
    avg_price     DECIMAL(12,2) DEFAULT NULL,
    freq          INT          DEFAULT NULL,
    fetched_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,

    INDEX idx_symbol_date_broker (symbol, date, broker_code)
);

-- Rekapan Net Foreign Flow Harian
CREATE TABLE IF NOT EXISTS foreign_flow_daily (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol        VARCHAR(10)  NOT NULL,
    date          DATE         NOT NULL,
    foreign_buy   BIGINT       DEFAULT NULL, -- dalam Rupiah
    foreign_sell  BIGINT       DEFAULT NULL, -- dalam Rupiah
    net_foreign   BIGINT       DEFAULT NULL, -- dalam Rupiah
    fetched_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,

    UNIQUE KEY idx_symbol_date (symbol, date)
);
