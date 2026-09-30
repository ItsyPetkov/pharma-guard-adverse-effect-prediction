-- =========================================================================
-- PHARMACOVIGILANCE ADVANCED SQL EXPLORATORY DATA ANALYSIS (EDA)
-- Safety Signals, Reporting Odds Ratio (ROR), and Disproportionality Metrics
-- Target Platform: Azure Synapse Analytics / Snowflake on Azure / Azure Databricks
-- =========================================================================

-- 1. Patient Demographics & Event Severity Across Age Cohorts
SELECT 
    CASE 
        WHEN patient_age < 18 THEN 'Pediatric (<18)'
        WHEN patient_age BETWEEN 18 AND 45 THEN 'Adult (18-45)'
        WHEN patient_age BETWEEN 46 AND 64 THEN 'Middle-aged (46-64)'
        ELSE 'Geriatric (65+)'
    END AS age_cohort,
    COUNT(report_id) AS total_reports,
    SUM(serious_adverse_event) AS total_serious_events,
    ROUND(AVG(serious_adverse_event) * 100, 2) AS serious_event_rate_pct,
    ROUND(AVG(daily_dose_mg), 2) AS avg_daily_dose_mg,
    ROUND(AVG(concomitant_drug_count), 2) AS avg_concomitant_drugs
FROM `pharma_safety.adverse_events_curated`
GROUP BY 1
ORDER BY total_reports DESC;

-- 2. Pharmacovigilance Signal Detection: Reporting Odds Ratio (ROR) by Drug Class
-- ROR = (a / b) / (c / d)
-- a = Target drug class with serious event
-- b = Target drug class with non-serious event
-- c = Other drug classes with serious event
-- d = Other drug classes with non-serious event
WITH cohort_counts AS (
    SELECT 
        drug_class,
        SUM(CASE WHEN serious_adverse_event = 1 THEN 1 ELSE 0 END) AS a,
        SUM(CASE WHEN serious_adverse_event = 0 THEN 1 ELSE 0 END) AS b,
        (SELECT COUNT(*) FROM `pharma_safety.adverse_events_curated` WHERE serious_adverse_event = 1) AS total_serious,
        (SELECT COUNT(*) FROM `pharma_safety.adverse_events_curated` WHERE serious_adverse_event = 0) AS total_non_serious
    FROM `pharma_safety.adverse_events_curated`
    GROUP BY drug_class
)
SELECT 
    drug_class,
    a AS serious_case_count,
    b AS non_serious_case_count,
    ROUND((CAST(a AS FLOAT64) / NULLIF(b, 0)) / 
          (NULLIF(CAST(total_serious - a AS FLOAT64), 0) / NULLIF(total_non_serious - b, 0)), 3) AS reporting_odds_ratio_ror,
    ROUND((CAST(a AS FLOAT64) / NULLIF(a + b, 0)) / 
          (NULLIF(CAST(total_serious - a AS FLOAT64), 0) / NULLIF((total_serious - a) + (total_non_serious - b), 0)), 3) AS proportional_reporting_ratio_prr
FROM cohort_counts
WHERE (a + b) > 0
ORDER BY reporting_odds_ratio_ror DESC;

-- 3. Window Function: Drug Specific Event Severity Ranking within Indication
SELECT 
    drug_class,
    route_of_administration,
    COUNT(report_id) AS total_cases,
    ROUND(AVG(serious_adverse_event), 4) AS severity_rate,
    DENSE_RANK() OVER (PARTITION BY drug_class ORDER BY AVG(serious_adverse_event) DESC) as route_risk_rank,
    ROUND(AVG(time_to_onset_days), 1) as avg_latency_days
FROM `pharma_safety.adverse_events_curated`
GROUP BY drug_class, route_of_administration
HAVING total_cases >= 1
ORDER BY drug_class, route_risk_rank;