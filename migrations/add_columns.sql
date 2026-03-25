USE stockbit_data;

ALTER TABLE fundamental_data

  -- Section 0: Valuation (tambahan)
  ADD COLUMN IF NOT EXISTS ihsg_pe_ttm        DECIMAL(12,4) DEFAULT NULL AFTER peg,
  ADD COLUMN IF NOT EXISTS earnings_yield     DECIMAL(8,4)  DEFAULT NULL AFTER ihsg_pe_ttm,
  ADD COLUMN IF NOT EXISTS price_to_cashflow  DECIMAL(12,4) DEFAULT NULL AFTER earnings_yield,
  ADD COLUMN IF NOT EXISTS price_to_fcf       DECIMAL(12,4) DEFAULT NULL AFTER price_to_cashflow,
  ADD COLUMN IF NOT EXISTS ev_ebit            DECIMAL(12,4) DEFAULT NULL AFTER price_to_fcf,
  ADD COLUMN IF NOT EXISTS peg_3yr            DECIMAL(12,4) DEFAULT NULL AFTER ev_ebit,
  ADD COLUMN IF NOT EXISTS peg_forward        DECIMAL(12,4) DEFAULT NULL AFTER peg_3yr,

  -- Section 1: Per Share (tambahan)
  ADD COLUMN IF NOT EXISTS cash_per_share     DECIMAL(12,4) DEFAULT NULL AFTER revenue_per_share,
  ADD COLUMN IF NOT EXISTS fcf_per_share      DECIMAL(12,4) DEFAULT NULL AFTER cash_per_share,

  -- Section 2: Solvency (tambahan)
  ADD COLUMN IF NOT EXISTS quick_ratio        DECIMAL(12,4) DEFAULT NULL AFTER current_ratio,
  ADD COLUMN IF NOT EXISTS lt_debt_equity     DECIMAL(12,4) DEFAULT NULL AFTER der,
  ADD COLUMN IF NOT EXISTS total_liab_equity  DECIMAL(12,4) DEFAULT NULL AFTER lt_debt_equity,
  ADD COLUMN IF NOT EXISTS financial_leverage DECIMAL(12,4) DEFAULT NULL AFTER debt_to_assets,
  ADD COLUMN IF NOT EXISTS interest_coverage  DECIMAL(12,4) DEFAULT NULL AFTER financial_leverage,
  ADD COLUMN IF NOT EXISTS fcf_quarter        DECIMAL(20,2) DEFAULT NULL AFTER interest_coverage,
  ADD COLUMN IF NOT EXISTS altman_z_score     DECIMAL(8,4)  DEFAULT NULL AFTER fcf_quarter,

  -- Section 3: Management Effectiveness (tambahan)
  ADD COLUMN IF NOT EXISTS roce               DECIMAL(8,4)  DEFAULT NULL AFTER roic,
  ADD COLUMN IF NOT EXISTS days_sales_out     DECIMAL(8,2)  DEFAULT NULL AFTER roce,
  ADD COLUMN IF NOT EXISTS days_inventory     DECIMAL(8,2)  DEFAULT NULL AFTER days_sales_out,
  ADD COLUMN IF NOT EXISTS days_payables      DECIMAL(8,2)  DEFAULT NULL AFTER days_inventory,
  ADD COLUMN IF NOT EXISTS cash_conv_cycle    DECIMAL(8,2)  DEFAULT NULL AFTER days_payables,
  ADD COLUMN IF NOT EXISTS receivables_turn   DECIMAL(8,4)  DEFAULT NULL AFTER cash_conv_cycle,
  ADD COLUMN IF NOT EXISTS asset_turnover     DECIMAL(8,4)  DEFAULT NULL AFTER receivables_turn,
  ADD COLUMN IF NOT EXISTS inventory_turnover DECIMAL(8,4)  DEFAULT NULL AFTER asset_turnover,

  -- Section 5: Growth (tambahan)
  ADD COLUMN IF NOT EXISTS gross_profit_yoy   DECIMAL(8,4)  DEFAULT NULL AFTER revenue_yoy,

  -- Section 6: Dividend (tambahan)
  ADD COLUMN IF NOT EXISTS dividend_amount    DECIMAL(12,4) DEFAULT NULL AFTER payout_ratio,
  ADD COLUMN IF NOT EXISTS dividend_ttm       DECIMAL(12,4) DEFAULT NULL AFTER dividend_amount,
  ADD COLUMN IF NOT EXISTS dividend_ex_date   VARCHAR(30)   DEFAULT NULL AFTER dividend_ttm,

  -- Section 7: Market Rank
  ADD COLUMN IF NOT EXISTS eps_rating         DECIMAL(8,4)  DEFAULT NULL AFTER piotroski_score,
  ADD COLUMN IF NOT EXISTS relative_strength  DECIMAL(8,4)  DEFAULT NULL AFTER eps_rating,
  ADD COLUMN IF NOT EXISTS rank_market_cap    DECIMAL(8,4)  DEFAULT NULL AFTER relative_strength,
  ADD COLUMN IF NOT EXISTS rank_pe_ttm        DECIMAL(8,4)  DEFAULT NULL AFTER rank_market_cap,
  ADD COLUMN IF NOT EXISTS rank_earnings_yld  DECIMAL(8,4)  DEFAULT NULL AFTER rank_pe_ttm,
  ADD COLUMN IF NOT EXISTS rank_ps            DECIMAL(8,4)  DEFAULT NULL AFTER rank_earnings_yld,
  ADD COLUMN IF NOT EXISTS rank_pb            DECIMAL(8,4)  DEFAULT NULL AFTER rank_ps,
  ADD COLUMN IF NOT EXISTS rank_near_52wk_high DECIMAL(8,4) DEFAULT NULL AFTER rank_pb,

  -- Section 8: Income Statement (dalam miliar IDR)
  ADD COLUMN IF NOT EXISTS revenue_ttm        DECIMAL(20,2) DEFAULT NULL AFTER rank_near_52wk_high,
  ADD COLUMN IF NOT EXISTS gross_profit_ttm   DECIMAL(20,2) DEFAULT NULL AFTER revenue_ttm,
  ADD COLUMN IF NOT EXISTS ebitda_ttm         DECIMAL(20,2) DEFAULT NULL AFTER gross_profit_ttm,
  ADD COLUMN IF NOT EXISTS net_income_ttm     DECIMAL(20,2) DEFAULT NULL AFTER ebitda_ttm,

  -- Section 9: Balance Sheet (dalam miliar IDR)
  ADD COLUMN IF NOT EXISTS cash_bs            DECIMAL(20,2) DEFAULT NULL AFTER net_income_ttm,
  ADD COLUMN IF NOT EXISTS total_assets       DECIMAL(20,2) DEFAULT NULL AFTER cash_bs,
  ADD COLUMN IF NOT EXISTS total_liabilities  DECIMAL(20,2) DEFAULT NULL AFTER total_assets,
  ADD COLUMN IF NOT EXISTS working_capital    DECIMAL(20,2) DEFAULT NULL AFTER total_liabilities,
  ADD COLUMN IF NOT EXISTS common_equity      DECIMAL(20,2) DEFAULT NULL AFTER working_capital,
  ADD COLUMN IF NOT EXISTS lt_debt            DECIMAL(20,2) DEFAULT NULL AFTER common_equity,
  ADD COLUMN IF NOT EXISTS st_debt            DECIMAL(20,2) DEFAULT NULL AFTER lt_debt,
  ADD COLUMN IF NOT EXISTS total_debt         DECIMAL(20,2) DEFAULT NULL AFTER st_debt,
  ADD COLUMN IF NOT EXISTS net_debt           DECIMAL(20,2) DEFAULT NULL AFTER total_debt,
  ADD COLUMN IF NOT EXISTS total_equity       DECIMAL(20,2) DEFAULT NULL AFTER net_debt,

  -- Section 10: Cash Flow (dalam miliar IDR)
  ADD COLUMN IF NOT EXISTS cfo_ttm            DECIMAL(20,2) DEFAULT NULL AFTER total_equity,
  ADD COLUMN IF NOT EXISTS cfi_ttm            DECIMAL(20,2) DEFAULT NULL AFTER cfo_ttm,
  ADD COLUMN IF NOT EXISTS cff_ttm            DECIMAL(20,2) DEFAULT NULL AFTER cfi_ttm,
  ADD COLUMN IF NOT EXISTS capex_ttm          DECIMAL(20,2) DEFAULT NULL AFTER cff_ttm,
  ADD COLUMN IF NOT EXISTS fcf_ttm            DECIMAL(20,2) DEFAULT NULL AFTER capex_ttm,

  -- Section 11: Price Performance (%)
  ADD COLUMN IF NOT EXISTS return_1w          DECIMAL(8,4)  DEFAULT NULL AFTER fcf_ttm,
  ADD COLUMN IF NOT EXISTS return_1m          DECIMAL(8,4)  DEFAULT NULL AFTER return_1w,
  ADD COLUMN IF NOT EXISTS return_3m          DECIMAL(8,4)  DEFAULT NULL AFTER return_1m,
  ADD COLUMN IF NOT EXISTS return_6m          DECIMAL(8,4)  DEFAULT NULL AFTER return_3m,
  ADD COLUMN IF NOT EXISTS return_1y          DECIMAL(8,4)  DEFAULT NULL AFTER return_6m,
  ADD COLUMN IF NOT EXISTS return_3y          DECIMAL(8,4)  DEFAULT NULL AFTER return_1y,
  ADD COLUMN IF NOT EXISTS return_5y          DECIMAL(8,4)  DEFAULT NULL AFTER return_3y,
  ADD COLUMN IF NOT EXISTS return_10y         DECIMAL(8,4)  DEFAULT NULL AFTER return_5y,
  ADD COLUMN IF NOT EXISTS return_ytd         DECIMAL(8,4)  DEFAULT NULL AFTER return_10y;
