## GEM 2023/24 Women’s Entrepreneurship – Female Gap Analysis

This project studies the female entrepreneurship gap using the GEM 2023/24 Women’s Entrepreneurship Report (Women’s Edition).

### What this does
- Extracts the core indicators needed to study the female entrepreneurship gap:
  - Total Early-stage Entrepreneurial Activity (TEA) by gender
  - Perceived capabilities by gender
  - Fear of failure by gender
- Cleans and merges these into a single cross-country dataset
- Computes FemaleGap = Female TEA − Male TEA
- Fits a simple linear model: FemaleGap ~ FearOfFailure_Female + PerceivedCapability_Female

### Data sources
- Report PDF: `open.pdf` (GEM 2023/24 Women’s Entrepreneurship Report – Women’s Edition)
- This run used CSVs exported from the PDF tables (pages provided by the user):
  - `TEA_by_gender.csv`
  - `Perceived_capabilities_by_gender.csv`
  - `Fear_of_failure_by_gender.csv`

### How to run
1) Ensure the three CSVs are present in the project folder (as above).
2) From the project directory, run:
```
venv\Scripts\python.exe analysis_from_csvs.py
```
3) The script prints:
   - A 5-row preview of the merged CSV
   - The full merged CSV (all complete rows)
   - Regression summary (coefficients, standard errors, R-squared) and a brief interpretation

### Outputs (from current run)
- Regression: FemaleGap ~ FearOfFailure_Female + PerceivedCapability_Female
  - Coefficients (StdErr):
    - const: -4.320489 (3.373871)
    - FearOfFailure_Female: 0.021536 (0.055143)
    - PerceivedCapability_Female: -0.003027 (0.030270)
  - R-squared: 0.0037

### How we evaluated success/performance
We evaluated the solution primarily on three fronts:
1) Data integrity and completeness
   - All numeric fields were coerced to numbers (percent signs removed; text cleaned).
   - Only rows with complete values across TEA, Fear of Failure, and Perceived Capabilities were included.
   - Spot-checks against the report tables ensured values matched the source.
2) Model interpretability and statistical diagnostics
   - We inspected coefficient signs and magnitudes to see if they align with intuition:
     - Higher fear of failure (female) is associated with a larger negative gap (expected to reduce female TEA relative to male), while higher perceived capability (female) is expected to shrink the gap. In this sample, estimates were small and imprecise.
   - We reported standard errors to convey uncertainty around each coefficient estimate.
   - We reported R-squared to assess explanatory power.
3) Practical usefulness
   - We produced a clean, analysis-ready CSV and a minimal, reproducible script (`analysis_from_csvs.py`).

### What the results mean (candid)
- The R-squared (~0.004) is very low, so this simple model explains almost none of the cross-country variation in the female TEA gap. The individual coefficients are small relative to their standard errors, suggesting the effects are statistically imprecise.
- In plain terms: with only two predictors, the relationship between these attitudes and the female entrepreneurship gap is weak in this snapshot. The gap is likely driven by additional factors (e.g., labor regulations, access to finance, culture, childcare infrastructure, sector composition, education, macro conditions) not included here.

### Limitations
- Single-year cross-section: no panel variation or fixed effects.
- Manual table export from the PDF (potential for transcription errors if the source tables change or if different page versions are used).
- Omitted variables: many relevant structural and policy variables are not included.
- Linear functional form; no interactions or non-linearities.

### Next steps (if extending)
- Expand to a multi-year panel; include country fixed effects.
- Add additional predictors (policy, finance, childcare, education, culture indices).
- Explore non-linear models or interactions (e.g., capability × culture).
- Robustness: alternative specifications, influence diagnostics, and outlier checks.

### File overview
- `analysis_from_csvs.py`: loads the three CSVs, cleans/merges, computes FemaleGap, and runs the regression.
- `extract_gem_women_report.py`: utilities to try PDF extraction; optional (not required when using CSVs).
- `TEA_by_gender.csv`, `Perceived_capabilities_by_gender.csv`, `Fear_of_failure_by_gender.csv`: inputs exported from the GEM report tables.


