-- =========================================================================
-- CURATED ANALYTICAL VIEW FOR GOOGLE LOOKER STUDIO DASHBOARD
-- Target Platform: Azure Synapse Analytics / Azure SQL / Snowflake on Azure
-- =========================================================================

CREATE OR REPLACE VIEW `pharma_safety.vw_power_bi_adr_kpis` AS
SELECT 
    report_id,
    report_date,
    patient_age,
    patient_sex,
    drug_class,
    route_of_administration,
    daily_dose_mg,
    treatment_duration_days,
    concomitant_drug_count,
    interaction_risk_index,
    renal_impairment_flag,
    hepatic_impairment_flag,
    reporting_source,
    time_to_onset_days,
    serious_adverse_event,
    -- Engineered clinical risk tiers
    CASE 
        WHEN concomitant_drug_count >= 5 THEN 'Major Polypharmacy (5+)'
        WHEN concomitant_drug_count BETWEEN 2 AND 4 THEN 'Moderate Polypharmacy (2-4)'
        ELSE 'Monotherapy / Low (0-1)'
    END AS polypharmacy_tier,
    CASE 
        WHEN patient_age >= 65 AND (renal_impairment_flag = 1 OR hepatic_impairment_flag = 1) THEN 'High Clinical Vulnerability'
        WHEN patient_age >= 65 OR renal_impairment_flag = 1 OR hepatic_impairment_flag = 1 THEN 'Moderate Clinical Vulnerability'
        ELSE 'Standard Risk Baseline'
    END AS clinical_vulnerability_profile,
    ROUND(daily_dose_mg / NULLIF(patient_weight_kg, 0), 2) AS dose_intensity_per_kg
FROM `pharma_safety.adverse_events_curated`;