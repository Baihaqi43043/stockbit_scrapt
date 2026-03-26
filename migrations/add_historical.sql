USE stockbit_data;

CREATE TABLE IF NOT EXISTS historical_quarterly (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol       VARCHAR(10)   NOT NULL,
    year         SMALLINT      NOT NULL,
    quarter      TINYINT       NOT NULL,
    revenue      DECIMAL(20,2) DEFAULT NULL,
    net_income   DECIMAL(20,2) DEFAULT NULL,
    eps          DECIMAL(12,4) DEFAULT NULL,
    fetched_at   DATETIME      DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_hist (symbol, year, quarter),
    INDEX idx_symbol (symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
