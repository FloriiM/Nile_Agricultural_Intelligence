-- ============================================================================
-- NILE.AG - FARM INTELLIGENCE PLATFORM
-- Purpose: Fresh Produce Quality Tracking | Market Intelligence | Harvest Optimization
-- Compatible: PostgreSQL (adapt for MySQL/SQLite)
-- ============================================================================

-- ============================================================================
-- 0. BASE VIEW (STANDARDIZED FOUNDATION)
-- ============================================================================
CREATE OR REPLACE VIEW v_farm_base AS
SELECT
    batch_id,
    harvest_date,
    produce_type,
    category,
    subcategory,
    quantity_kg,
    quality_score,
    quality_grade,
    grade_description,
    remaining_shelf_life_days,
    storage_temperature_c,
    storage_humidity_pct,
    days_since_harvest,
    initial_value_zar,
    current_value_zar,
    value_lost_zar,
    value_loss_percent,
    recommended_market,
    expected_revenue_at_recommended_market,
    harvest_recommendation,
    harvest_urgency,
    sell_urgency,
    sell_action,
    urgency_score,
    profit_margin_pct,
    is_peak_season,
    season,
    DATE_TRUNC('month', harvest_date) AS harvest_month,
    DATE_TRUNC('week', harvest_date) AS harvest_week
FROM farm_intelligence_data;


-- ============================================================================
-- 1. EXECUTIVE DASHBOARD (FARM KPIs)
-- ============================================================================
CREATE OR REPLACE VIEW v_executive_summary AS
SELECT
    COUNT(*) AS total_batches,
    ROUND(AVG(quality_score), 1) AS avg_quality_score,
    ROUND(SUM(current_value_zar), 0) AS total_current_value,
    ROUND(SUM(value_lost_zar), 0) AS total_value_lost,
    ROUND(SUM(value_lost_zar) / NULLIF(SUM(initial_value_zar), 0) * 100, 1) AS loss_percentage,
    ROUND(AVG(profit_margin_pct), 1) AS avg_profit_margin,
    COUNT(CASE WHEN sell_urgency = 'IMMEDIATE' THEN 1 END) AS urgent_batches,
    COUNT(CASE WHEN quality_grade LIKE '%Premium%' THEN 1 END) AS premium_batches,
    COUNT(DISTINCT produce_type) AS unique_products,
    COUNT(DISTINCT recommended_market) AS active_markets,
    
    CASE 
        WHEN AVG(quality_score) >= 80 THEN '🟢 EXCELLENT'
        WHEN AVG(quality_score) >= 60 THEN '🟡 GOOD'
        ELSE '🔴 CRITICAL'
    END AS farm_health_status
FROM v_farm_base;


-- ============================================================================
-- 2. QUALITY ANALYSIS VIEWS
-- ============================================================================

-- Quality Distribution by Grade
CREATE OR REPLACE VIEW v_quality_distribution AS
SELECT
    quality_grade,
    COUNT(*) AS batch_count,
    ROUND(SUM(quantity_kg), 0) AS total_quantity_kg,
    ROUND(SUM(current_value_zar), 0) AS total_value,
    ROUND(AVG(quality_score), 1) AS avg_score,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percentage
FROM v_farm_base
GROUP BY quality_grade
ORDER BY avg_score DESC;

-- Declining Quality Products (Trend Analysis)
CREATE OR REPLACE VIEW v_declining_quality_products AS
WITH weekly_quality AS (
    SELECT
        produce_type,
        harvest_week,
        AVG(quality_score) AS avg_quality,
        AVG(value_loss_percent) AS avg_loss
    FROM v_farm_base
    GROUP BY produce_type, harvest_week
),
quality_trend AS (
    SELECT
        produce_type,
        AVG(avg_quality) FILTER (WHERE harvest_week >= CURRENT_DATE - INTERVAL '4 weeks') AS recent_quality,
        AVG(avg_quality) FILTER (WHERE harvest_week < CURRENT_DATE - INTERVAL '4 weeks') AS past_quality
    FROM weekly_quality
    GROUP BY produce_type
)
SELECT
    produce_type,
    ROUND(recent_quality, 1) AS current_quality,
    ROUND(past_quality, 1) AS previous_quality,
    ROUND(recent_quality - past_quality, 1) AS quality_change,
    CASE
        WHEN recent_quality < past_quality * 0.85 THEN 'CRITICAL DECLINE'
        WHEN recent_quality < past_quality * 0.92 THEN 'DECLINING'
        WHEN recent_quality > past_quality * 1.05 THEN 'IMPROVING'
        ELSE 'STABLE'
    END AS trend_status
FROM quality_trend
WHERE recent_quality IS NOT NULL AND past_quality IS NOT NULL
ORDER BY quality_change;


-- ============================================================================
-- 3. MARKET INTELLIGENCE VIEWS
-- ============================================================================

-- Market Performance Comparison
CREATE OR REPLACE VIEW v_market_performance AS
SELECT
    recommended_market,
    COUNT(*) AS batches_sent,
    ROUND(SUM(quantity_kg), 0) AS total_quantity,
    ROUND(SUM(expected_revenue_at_recommended_market), 0) AS total_revenue,
    ROUND(AVG(expected_revenue_at_recommended_market / NULLIF(quantity_kg, 0)), 2) AS avg_price_per_kg,
    ROUND(AVG(profit_margin_pct), 1) AS avg_profit_margin,
    ROW_NUMBER() OVER (ORDER BY SUM(expected_revenue_at_recommended_market) DESC) AS revenue_rank
FROM v_farm_base
GROUP BY recommended_market
ORDER BY total_revenue DESC;

-- Best Market for Each Product
CREATE OR REPLACE VIEW v_product_market_optimization AS
WITH product_market_perf AS (
    SELECT
        produce_type,
        recommended_market,
        COUNT(*) AS batch_count,
        ROUND(AVG(expected_revenue_at_recommended_market / NULLIF(quantity_kg, 0)), 2) AS avg_price,
        ROW_NUMBER() OVER (PARTITION BY produce_type ORDER BY AVG(expected_revenue_at_recommended_market / NULLIF(quantity_kg, 0)) DESC) AS price_rank
    FROM v_farm_base
    GROUP BY produce_type, recommended_market
)
SELECT
    produce_type,
    recommended_market AS best_market,
    avg_price AS best_price,
    batch_count
FROM product_market_perf
WHERE price_rank = 1
ORDER BY produce_type;


-- ============================================================================
-- 4. URGENCY & PRIORITY VIEWS
-- ============================================================================

-- Priority Action Queue (What to do NOW)
CREATE OR REPLACE VIEW v_priority_queue AS
SELECT
    batch_id,
    produce_type,
    quantity_kg,
    quality_score,
    remaining_shelf_life_days,
    value_lost_zar,
    current_value_zar,
    sell_urgency,
    sell_action,
    recommended_market,
    urgency_score,
    
    CASE
        WHEN sell_urgency = 'IMMEDIATE' THEN 1
        WHEN sell_urgency = 'HIGH' THEN 2
        WHEN sell_urgency = 'MEDIUM' THEN 3
        ELSE 4
    END AS priority_order
FROM v_farm_base
WHERE sell_urgency IN ('IMMEDIATE', 'HIGH')
ORDER BY priority_order, urgency_score DESC
LIMIT 50;

-- Harvest Recommendations
CREATE OR REPLACE VIEW v_harvest_recommendations AS
SELECT
    produce_type,
    harvest_recommendation AS recommendation,
    harvest_urgency,
    COUNT(*) AS affected_batches,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(current_market_price_estimate), 2) AS current_price,
    ROUND(AVG(forecast_price_in_3_days), 2) AS forecast_price,
    ROUND(AVG(forecast_price_in_3_days - current_market_price_estimate), 2) AS price_change
FROM v_farm_base
WHERE harvest_urgency IN ('CRITICAL', 'HIGH')
GROUP BY produce_type, harvest_recommendation, harvest_urgency
ORDER BY CASE harvest_urgency WHEN 'CRITICAL' THEN 1 WHEN 'HIGH' THEN 2 ELSE 3 END;


-- ============================================================================
-- 5. LOSS ANALYSIS VIEWS
-- ============================================================================

-- Loss by Category
CREATE OR REPLACE VIEW v_loss_by_category AS
SELECT
    category,
    COUNT(*) AS batch_count,
    ROUND(SUM(initial_value_zar), 0) AS initial_value,
    ROUND(SUM(current_value_zar), 0) AS current_value,
    ROUND(SUM(value_lost_zar), 0) AS total_loss,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_percentage,
    ROUND(SUM(value_lost_zar) / NULLIF(SUM(initial_value_zar), 0) * 100, 1) AS loss_rate
FROM v_farm_base
GROUP BY category
ORDER BY total_loss DESC;

-- Top Loss-Making Products
CREATE OR REPLACE VIEW v_top_loss_products AS
SELECT
    produce_type,
    category,
    COUNT(*) AS batch_count,
    ROUND(SUM(value_lost_zar), 0) AS total_loss,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(remaining_shelf_life_days), 1) AS avg_shelf_life
FROM v_farm_base
GROUP BY produce_type, category
ORDER BY total_loss DESC
LIMIT 20;


-- ============================================================================
-- 6. SEASONAL & TIME ANALYSIS
-- ============================================================================

-- Seasonal Performance Patterns
CREATE OR REPLACE VIEW v_seasonal_performance AS
SELECT
    season,
    category,
    COUNT(*) AS batch_count,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(profit_margin_pct), 1) AS avg_profit_margin,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct,
    ROUND(AVG(urgency_score), 1) AS avg_urgency
FROM v_farm_base
GROUP BY season, category
ORDER BY season, avg_quality DESC;

-- Monthly Quality Trends
CREATE OR REPLACE VIEW v_monthly_quality_trend AS
SELECT
    EXTRACT(YEAR FROM harvest_date) AS year,
    EXTRACT(MONTH FROM harvest_date) AS month,
    TO_CHAR(harvest_date, 'Month') AS month_name,
    COUNT(*) AS batch_count,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY quality_score), 1) AS median_quality,
    ROUND(STDDEV(quality_score), 1) AS quality_volatility,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct
FROM v_farm_base
GROUP BY year, month, month_name
ORDER BY year, month;


-- ============================================================================
-- 7. SUPPLIER/FARMER PERFORMANCE (if applicable)
-- ============================================================================

-- Farmer Performance Scorecard
CREATE OR REPLACE VIEW v_farmer_performance AS
SELECT
    COALESCE(farmer_id, 'UNKNOWN') AS farmer_id,
    COUNT(*) AS total_batches,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(profit_margin_pct), 1) AS avg_profit_margin,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct,
    COUNT(CASE WHEN quality_grade LIKE '%Premium%' THEN 1 END) AS premium_batches,
    COUNT(CASE WHEN sell_urgency IN ('IMMEDIATE', 'HIGH') THEN 1 END) AS urgent_batches,
    ROUND(AVG(remaining_shelf_life_days), 1) AS avg_shelf_life,
    
    -- Score (0-100)
    ROUND(
        (AVG(quality_score) * 0.4) +
        (100 - AVG(value_loss_percent)) * 0.3 +
        (AVG(profit_margin_pct) * 0.3)
    , 1) AS farmer_score,
    
    CASE
        WHEN AVG(quality_score) >= 80 AND AVG(value_loss_percent) < 20 THEN 'A - Premium Producer'
        WHEN AVG(quality_score) >= 70 AND AVG(value_loss_percent) < 30 THEN 'B - Good Producer'
        WHEN AVG(quality_score) >= 60 THEN 'C - Average Producer'
        ELSE 'D - Needs Improvement'
    END AS performance_grade
FROM v_farm_base
GROUP BY farmer_id
HAVING COUNT(*) >= 5
ORDER BY farmer_score DESC;


-- ============================================================================
-- 8. ALERT & WARNING SYSTEM
-- ============================================================================

-- Active Alerts
CREATE OR REPLACE VIEW v_active_alerts AS
SELECT
    'QUALITY ALERT' AS alert_type,
    'HIGH' AS severity,
    produce_type,
    batch_id,
    CONCAT('Quality dropped to ', quality_score, '%') AS message,
    'Immediate sale recommended' AS action
FROM v_farm_base
WHERE quality_score < 50 AND sell_urgency = 'IMMEDIATE'

UNION ALL

SELECT
    'LOSS ALERT' AS alert_type,
    'HIGH' AS severity,
    produce_type,
    batch_id,
    CONCAT('Value loss of ', value_loss_percent, '% detected') AS message,
    'Review storage conditions' AS action
FROM v_farm_base
WHERE value_loss_percent > 50

UNION ALL

SELECT
    'SHELF LIFE ALERT' AS alert_type,
    'MEDIUM' AS severity,
    produce_type,
    batch_id,
    CONCAT('Only ', remaining_shelf_life_days, ' days remaining') AS message,
    'Expedite to market' AS action
FROM v_farm_base
WHERE remaining_shelf_life_days <= 2

ORDER BY severity DESC;


-- ============================================================================
-- 9. MARKET PRICE OPTIMIZATION
-- ============================================================================

-- Price Optimization Recommendations
CREATE OR REPLACE VIEW v_price_optimization AS
SELECT
    produce_type,
    recommended_market AS current_best_market,
    avg_price_per_kg AS current_best_price,
    second_best_market,
    second_best_price,
    ROUND(avg_price_per_kg - second_best_price, 2) AS price_advantage,
    ROUND((avg_price_per_kg - second_best_price) / second_best_price * 100, 1) AS premium_percentage
FROM (
    SELECT
        produce_type,
        recommended_market,
        avg_price_per_kg,
        LEAD(recommended_market) OVER (PARTITION BY produce_type ORDER BY avg_price_per_kg DESC) AS second_best_market,
        LEAD(avg_price_per_kg) OVER (PARTITION BY produce_type ORDER BY avg_price_per_kg DESC) AS second_best_price,
        ROW_NUMBER() OVER (PARTITION BY produce_type ORDER BY avg_price_per_kg DESC) AS rn
    FROM v_product_market_optimization
) ranked
WHERE rn = 1 AND second_best_price IS NOT NULL
ORDER BY premium_percentage DESC;


-- ============================================================================
-- 10. DAILY OPERATIONS DASHBOARD
-- ============================================================================

CREATE OR REPLACE VIEW v_daily_operations AS
SELECT
    harvest_date::DATE AS date,
    COUNT(*) AS batches_harvested,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(SUM(quantity_kg), 0) AS total_quantity_kg,
    ROUND(SUM(initial_value_zar), 0) AS harvest_value,
    COUNT(CASE WHEN sell_urgency IN ('IMMEDIATE', 'HIGH') THEN 1 END) AS urgent_actions,
    ROUND(AVG(urgency_score), 1) AS avg_urgency
FROM v_farm_base
WHERE harvest_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY harvest_date
ORDER BY harvest_date DESC;


-- ============================================================================
-- 11. PRODUCT RISK RANKING
-- ============================================================================

CREATE OR REPLACE VIEW v_product_risk_ranking AS
SELECT
    produce_type,
    category,
    COUNT(*) AS batch_count,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct,
    ROUND(AVG(urgency_score), 1) AS avg_urgency,
    ROUND(AVG(profit_margin_pct), 1) AS avg_profit_margin,
    
    -- Risk Score (0-100, higher = more risk)
    ROUND(
        (100 - AVG(quality_score)) * 0.4 +
        AVG(value_loss_percent) * 0.3 +
        AVG(urgency_score) * 0.3
    , 1) AS risk_score,
    
    CASE
        WHEN AVG(quality_score) < 60 OR AVG(value_loss_percent) > 40 THEN '🔴 HIGH RISK'
        WHEN AVG(quality_score) < 75 OR AVG(value_loss_percent) > 25 THEN '🟡 MEDIUM RISK'
        ELSE '🟢 LOW RISK'
    END AS risk_level
FROM v_farm_base
GROUP BY produce_type, category
HAVING COUNT(*) >= 10
ORDER BY risk_score DESC;


-- ============================================================================
-- 12. STORAGE EFFICIENCY ANALYSIS
-- ============================================================================

CREATE OR REPLACE VIEW v_storage_efficiency AS
SELECT
    CASE 
        WHEN storage_temperature_c < 4 THEN 'Too Cold (<4°C)'
        WHEN storage_temperature_c BETWEEN 4 AND 8 THEN 'Optimal (4-8°C)'
        WHEN storage_temperature_c BETWEEN 8 AND 12 THEN 'Warm (8-12°C)'
        ELSE 'Too Hot (>12°C)'
    END AS temperature_zone,
    CASE
        WHEN storage_humidity_pct < 75 THEN 'Too Dry (<75%)'
        WHEN storage_humidity_pct BETWEEN 75 AND 90 THEN 'Optimal (75-90%)'
        ELSE 'Too Humid (>90%)'
    END AS humidity_zone,
    COUNT(*) AS batch_count,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    ROUND(AVG(value_loss_percent), 1) AS avg_loss_pct,
    ROUND(AVG(remaining_shelf_life_days), 1) AS avg_shelf_life
FROM v_farm_base
GROUP BY temperature_zone, humidity_zone
ORDER BY avg_quality DESC;


-- ============================================================================
-- 13. BUYER MATCHING (Market Demand)
-- ============================================================================

CREATE OR REPLACE VIEW v_buyer_matching AS
SELECT
    recommended_market AS market,
    produce_type,
    AVG(expected_revenue_at_recommended_market / NULLIF(quantity_kg, 0)) AS avg_price,
    COUNT(*) AS available_batches,
    ROUND(SUM(quantity_kg), 0) AS total_available_kg,
    ROUND(AVG(quality_score), 1) AS avg_quality,
    MIN(remaining_shelf_life_days) AS min_shelf_life
FROM v_farm_base
WHERE remaining_shelf_life_days > 0
GROUP BY recommended_market, produce_type
HAVING SUM(quantity_kg) > 100
ORDER BY recommended_market, avg_price DESC;


-- ============================================================================
-- 14. WEEKLY FORECAST (Predictive)
-- ============================================================================

CREATE OR REPLACE VIEW v_weekly_forecast AS
WITH weekly_trend AS (
    SELECT
        harvest_week,
        AVG(quality_score) AS avg_quality,
        AVG(profit_margin_pct) AS avg_margin,
        LAG(AVG(quality_score)) OVER (ORDER BY harvest_week) AS prev_quality
    FROM v_farm_base
    WHERE harvest_week >= CURRENT_DATE - INTERVAL '12 weeks'
    GROUP BY harvest_week
)
SELECT
    'Next 7 Days' AS forecast_period,
    ROUND(AVG(avg_quality) + (AVG(avg_quality) - AVG(prev_quality)), 1) AS forecast_quality,
    ROUND(AVG(avg_margin) + (AVG(avg_margin) - LAG(AVG(avg_margin)) OVER ()), 1) AS forecast_margin,
    CASE
        WHEN (AVG(avg_quality) - AVG(prev_quality)) > 0 THEN 'IMPROVING'
        WHEN (AVG(avg_quality) - AVG(prev_quality)) < 0 THEN 'DECLINING'
        ELSE 'STABLE'
    END AS quality_trend
FROM weekly_trend
WHERE prev_quality IS NOT NULL;


-- ============================================================================
-- 15. COMPLIANCE & QUALITY CERTIFICATION
-- ============================================================================

CREATE OR REPLACE VIEW v_quality_compliance AS
SELECT
    produce_type,
    COUNT(*) AS total_batches,
    COUNT(CASE WHEN quality_score >= 90 THEN 1 END) AS premium_grade,
    COUNT(CASE WHEN quality_score >= 75 AND quality_score < 90 THEN 1 END) AS good_grade,
    COUNT(CASE WHEN quality_score >= 60 AND quality_score < 75 THEN 1 END) AS fair_grade,
    COUNT(CASE WHEN quality_score < 60 THEN 1 END) AS poor_grade,
    ROUND(100.0 * COUNT(CASE WHEN quality_score >= 75 THEN 1 END) / COUNT(*), 1) AS export_ready_percentage,
    ROUND(AVG(remaining_shelf_life_days), 1) AS avg_shelf_life_for_export
FROM v_farm_base
GROUP BY produce_type
ORDER BY export_ready_percentage DESC;


-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_harvest_date ON farm_intelligence_data(harvest_date);
CREATE INDEX IF NOT EXISTS idx_produce_type ON farm_intelligence_data(produce_type);
CREATE INDEX IF NOT EXISTS idx_quality_grade ON farm_intelligence_data(quality_grade);
CREATE INDEX IF NOT EXISTS idx_recommended_market ON farm_intelligence_data(recommended_market);
CREATE INDEX IF NOT EXISTS idx_sell_urgency ON farm_intelligence_data(sell_urgency);
CREATE INDEX IF NOT EXISTS idx_quality_score ON farm_intelligence_data(quality_score);

-- ============================================================================
-- END OF SQL SCRIPT
-- ============================================================================
