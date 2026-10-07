import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))

from emi_calculator.analyzer import (analyze_loans, balance_projection, build_insights, build_prefill,
                                     clean_loans, key_insights, map_loan_type, months_between,
                                     portfolio_summary, read_file, sample_loans, template_bytes, yearly_flows)
from emi_calculator.core import calculate_emi

AS_OF = date(2026, 10, 7)


def analyzed():
    return analyze_loans(clean_loans(sample_loans()).data, AS_OF)


def test_template_roundtrip_excel():
    res = clean_loans(read_file(template_bytes(), "loans.xlsx"))
    assert len(res.data) == 5 and not res.missing


def test_flexible_headers_and_formats():
    raw = pd.DataFrame({"Amount": ["AED 100,000"], "Rate": [0.065], "Term": ["4 years"],
                        "Disbursement Date": ["2025-01-01"]})
    df = clean_loans(raw).data
    assert df.loc[0, "Loan_Amount"] == 100_000
    assert abs(df.loc[0, "Interest_Rate"] - 6.5) < 1e-9
    assert df.loc[0, "Tenure_Months"] == 48


def test_missing_required_column_friendly():
    res = clean_loans(pd.DataFrame({"Amount": [1000]}))
    assert res.data.empty and res.missing == ["Interest rate", "Loan tenure"]


def test_invalid_rows_skipped():
    raw = pd.DataFrame({"Loan_Amount": [100000, -5, None], "Interest_Rate": [5, 5, 5], "Tenure_Months": [12, 12, 12]})
    res = clean_loans(raw)
    assert len(res.data) == 1 and res.skipped == 2


def test_months_between():
    assert months_between(date(2026, 1, 15), date(2026, 3, 14)) == 1
    assert months_between(date(2026, 1, 15), date(2026, 3, 15)) == 2
    assert months_between(date(2027, 1, 1), date(2026, 1, 1)) == 0


def test_outstanding_matches_core_schedule():
    a = analyzed().set_index("Loan_ID")
    hl = a.loc["HL-001"]
    assert hl["EMIs_Paid"] == 67
    assert abs(hl["EMI"] - calculate_emi(1_800_000, 4.49, 300)) < 1e-6
    assert abs(hl["Remaining_Months"] - (300 - 67)) <= 1
    assert a.loc["PL-004", "Status"] == "Closed"


def test_prepayment_shortens_tenure():
    pl = analyzed().set_index("Loan_ID").loc["PL-003"]
    assert pl["Remaining_Months"] < 48 - pl["EMIs_Paid"]


def test_summary_projection_insights():
    a = analyzed()
    s = portfolio_summary(a)
    assert s["active"] == 4 and s["closed"] == 1
    assert balance_projection(a, AS_OF).groupby("Loan")["Outstanding"].last().max() < 1
    texts = " ".join(t for _, t in build_insights(a, monthly_salary=40_000))
    assert "highest rate" in texts and "debt-burden" in texts
    titles = [i["title"] for i in key_insights(a, 40_000)]
    assert titles[:4] == ["Your outstanding balance", "Interest impact", "Repayment progress", "Next milestone"]


def test_yearly_flows_reconcile():
    a = analyzed()
    y = yearly_flows(a, AS_OF)
    # principal repaid + projected principal = everything borrowed minus prepayments on non-closed loans
    total_principal = y["Principal"].sum()
    expected = a["Loan_Amount"].sum() - a["Prepayment"].sum()
    assert abs(total_principal - expected) < 5
    assert abs(y["Interest"].sum() - a["Total_Interest"].sum()) < 5


def test_prefill_respects_calculator_limits():
    a = analyzed().set_index("Loan_ID")
    vals, _ = build_prefill(a.loc["HL-001"], "Home Loan", "remaining")
    assert vals["Home Loan_amt"] % 5000 == 0 and vals["Home Loan_ten"] % 6 == 0
    vals, _ = build_prefill(a.loc["PL-003"], "Personal Loan", "original")
    assert vals["Personal Loan_rate"] == 6.99 and vals["Personal Loan_def"] is True
    assert map_loan_type("Car finance") == "Auto Loan" and map_loan_type("Mortgage") == "Home Loan"
    assert map_loan_type("Credit card") is None
