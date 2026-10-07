# UAE Loan Analyzer & EMI Calculator

A Streamlit app with two connected modules:

| Module | Purpose |
|---|---|
| **Loan Analyzer** (default) | Upload your loan Excel file and understand your existing loans: outstanding balance, interest impact, repayment progress, completion dates and key insights |
| **EMI Calculator** | Explore what-if scenarios for Personal, Home and Auto loans with sliders and a month-by-month amortization schedule |

**Flow:** Upload Excel → Analyze Loan → Loan Overview & Key Insights → *Explore with EMI Calculator* (values pre-filled) → Scenarios.

## Excel format
One row per loan. Only `Loan_Amount`, `Interest_Rate` and `Tenure_Months` are required. Download the template from the app header, or use `data/sample_loans.xlsx`.

| Field | Required | Type | Sample Value | Description |
|---|---|---|---|---|
| Loan_ID | Optional | Text | HL-001 | Your reference |
| Loan_Type | Optional | Text | Home Loan | Personal / Home / Auto Loan |
| Bank | Optional | Text | Bank A | Lender |
| Loan_Amount | Required | Number | 1800000 | Original amount (AED) |
| Interest_Rate | Required | Number | 4.49 | % p.a. (0.0449 also works) |
| Tenure_Months | Required | Number/Text | 300 | "25 years" also works |
| Start_Date | Recommended | Date | 2021-03-01 | Used to work out EMIs already paid |
| EMI | Optional | Number | 9995 | Calculated if missing |
| Outstanding_Principal | Optional | Number | 1550000 | Statement balance, overrides the estimate |
| Prepayment | Optional | Number | 10000 | Total lump-sum prepaid so far |

## Run
```bash
uv sync
uv run streamlit run app.py
```

## Test
```bash
uv run pytest -q
```

## Project structure
```
app.py                                 # app shell: header, navigation, routing, in-page scripts
src/emi_calculator/core.py             # EMI + amortization maths (shared)
src/emi_calculator/analyzer.py         # Loan Analyzer engine (parsing, metrics, insights)
src/emi_calculator/analyzer_page.py    # Loan Analyzer UI
src/emi_calculator/calculator_page.py  # EMI Calculator UI
src/emi_calculator/styles.py           # design system (tokens, components, responsive)
data/sample_loans.xlsx                 # sample input
tests/                                 # pytest
```
