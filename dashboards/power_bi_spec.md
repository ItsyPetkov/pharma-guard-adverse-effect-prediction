# Microsoft Power BI Pharmacovigilance Specification

## 1. Connection Architecture
- **Connector**: Azure Synapse Analytics / Azure SQL / Snowflake on Azure DirectQuery
- **Target Schema / View**: `pharma_safety.vw_power_bi_adr_kpis`
- **Data Refresh Schedule**: Scheduled Refresh / DirectQuery Real-Time (Every 4 Hours)

---

## 2. Calculated DAX Measures in Power BI

### Total Adverse Event Reports
```dax
Total Reports = COUNTROWS('vw_power_bi_adr_kpis')
```

### Serious Adverse Event Rate (%)
```dax
Serious ADR Rate = 
DIVIDE(
    CALCULATE(COUNTROWS('vw_power_bi_adr_kpis'), 'vw_power_bi_adr_kpis'[serious_adverse_event] = 1),
    COUNTROWS('vw_power_bi_adr_kpis'),
    0
)
```

### High Risk Patient Flag
```dax
High Risk Flag = 
IF(
    SELECTEDVALUE('vw_power_bi_adr_kpis'[clinical_vulnerability_profile]) = "Severe Hepatorenal Impairment" && 
    SELECTEDVALUE('vw_power_bi_adr_kpis'[polypharmacy_tier]) = "Major Polypharmacy (5+)", 
    1, 
    0
)
```

### Acute Onset Category Column (DAX)
```dax
Acute Onset Group = 
SWITCH(
    TRUE(),
    'vw_power_bi_adr_kpis'[time_to_onset_days] <= 3, "Acute (<= 3 Days)",
    'vw_power_bi_adr_kpis'[time_to_onset_days] <= 14, "Subacute (4-14 Days)",
    "Delayed (> 14 Days)"
)
```

## 3. Power BI Layout & Visual Dashboard Grid
1. Executive KPI Cards:
  - Total Patient Surveillance Cohort Size
  - Serious Adverse Reaction Prevalence Rate (%)
  - Geriatric & Renal High-Risk Patients Count
  - Median Onset Latency (Days)
2. Line and Clustered Column Chart: Temporal ADR Occurrence by Drug Class.
3. Bar Chart: Epidemiological Disproportionality Signal (ROR / PRR) by Drug Family.
4. Scatter Matrix: Dose Intensity (mg/kg) vs. Total Cumulative Exposure (mg) segmented by Reaction Severity.

