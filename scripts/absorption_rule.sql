-- Query untuk menjalankan Aturan "Serapan 50%" (Absorption Rule)
-- Mencari saham yang dalam 5 hari terakhir diakumulasi secara tersembunyi
-- Syarat: Retail jualan, Big Money beli, Serapan > 50%

SELECT 
    symbol,
    SUM(retail_net_val) AS total_retail_buysell,
    SUM(big_money_net_val) AS total_bigmoney_accum,
    ABS(SUM(big_money_net_val) / SUM(retail_net_val)) * 100 AS absorption_pct
FROM stock_daily_metrics
WHERE date >= DATE_SUB(CURDATE(), INTERVAL 5 DAY)
GROUP BY symbol
HAVING total_retail_buysell < 0 -- Retail jualan
   AND total_bigmoney_accum > 0  -- Big Money serap
   AND absorption_pct >= 50     -- Serapan minimal 50%
ORDER BY absorption_pct DESC;
