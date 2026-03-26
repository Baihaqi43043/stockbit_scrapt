USE stockbit_data;

DROP TABLE IF EXISTS broker_transaction_daily;
DROP TABLE IF EXISTS foreign_flow_daily;
DROP TABLE IF EXISTS market_detector_summary;
DROP TABLE IF EXISTS stock_daily_metrics;
DROP TABLE IF EXISTS broker_master;

-- 1. Tabel Master Kategori Broker (Penting untuk mapping Retail vs Big Money)
CREATE TABLE IF NOT EXISTS broker_master (
    code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) DEFAULT NULL,
    is_retail BOOLEAN DEFAULT FALSE
);

-- Insert default retail brokers
INSERT IGNORE INTO broker_master (code, name, is_retail) VALUES 
('YP', 'Mirae Asset Sekuritas', TRUE),
('PD', 'Indo Premier Sekuritas', TRUE),
('XL', 'Ajaib Sekuritas', TRUE),
('XC', 'Ajaib Sekuritas', TRUE),
('NI', 'BNI Sekuritas', TRUE),
('CC', 'Mandiri Sekuritas', TRUE),
('SQ', 'BCA Sekuritas', TRUE),
('EP', 'MNC Sekuritas', TRUE),
('KK', 'Phillip Sekuritas', TRUE);

-- 2. Transaksi Broker (Disederhanakan untuk Agregasi)
CREATE TABLE IF NOT EXISTS broker_transaction_daily (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    broker_code VARCHAR(10) NOT NULL,
    net_lot BIGINT NOT NULL,    -- Positif = Beli, Negatif = Jual
    net_val BIGINT NOT NULL,    -- Positif = Beli, Negatif = Jual
    avg_price DECIMAL(12,2),
    UNIQUE KEY idx_symbol_date_broker (symbol, date, broker_code)
);

-- 3. Data Harga dan Daily Metrics (Wajib ada untuk Flow Tracker)
CREATE TABLE IF NOT EXISTS stock_daily_metrics (
    symbol VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    close_price DECIMAL(12,2),
    volume BIGINT,
    foreign_net_val BIGINT,   -- Pindahkan net foreign ke sini agar efisien
    retail_net_val BIGINT,    -- Hasil kalkulasi Python: total net_val broker retail
    big_money_net_val BIGINT, -- Hasil kalkulasi Python: total net_val broker non-retail
    
    -- Market Detector info if needed
    accdist_status VARCHAR(50) DEFAULT NULL,
    
    PRIMARY KEY (symbol, date)
);
