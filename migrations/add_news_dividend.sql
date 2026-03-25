USE stockbit_data;

-- Berita per ticker
CREATE TABLE IF NOT EXISTS news (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol       VARCHAR(10)   NOT NULL,
    news_id      VARCHAR(150)  NOT NULL,
    title        TEXT          DEFAULT NULL,
    summary      TEXT          DEFAULT NULL,
    url          VARCHAR(500)  DEFAULT NULL,
    image_url    VARCHAR(500)  DEFAULT NULL,
    published_at DATETIME      DEFAULT NULL,
    source       VARCHAR(100)  DEFAULT NULL,
    fetched_at   DATETIME      DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_news (symbol, news_id),
    INDEX idx_symbol_date (symbol, published_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Historical dividen per tahun
CREATE TABLE IF NOT EXISTS dividend_history (
    id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol       VARCHAR(10)   NOT NULL,
    year         SMALLINT      NOT NULL,
    dps          DECIMAL(14,4) DEFAULT NULL,   -- Dividend Per Share (IDR)
    ex_date      DATE          DEFAULT NULL,
    payment_date DATE          DEFAULT NULL,
    div_type     VARCHAR(30)   DEFAULT NULL,   -- interim / final / special
    fetched_at   DATETIME      DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uniq_div (symbol, year),
    INDEX idx_symbol (symbol)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
