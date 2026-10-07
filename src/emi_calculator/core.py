"""EMI calculation logic (pure Python, no UI)."""
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class LoanDefaults:
    name: str
    amount: float
    rate: float          # annual % (indicative)
    tenure_months: int   # UAE default = CBUAE maximum tenure
    min_amount: float
    max_amount: float
    max_tenure_months: int


# UAE standards (Central Bank of UAE caps):
#   Personal loan : max 48 months
#   Auto loan     : max 60 months
#   Home loan     : max 25 years (300 months)
LOAN_TYPES: dict[str, LoanDefaults] = {
    "Personal Loan": LoanDefaults("Personal Loan", 100_000, 6.5, 48, 5_000, 1_000_000, 48),
    "Home Loan": LoanDefaults("Home Loan", 1_500_000, 4.5, 300, 100_000, 20_000_000, 300),
    "Auto Loan": LoanDefaults("Auto Loan", 120_000, 3.5, 60, 10_000, 2_000_000, 60),
}


def calculate_emi(principal: float, annual_rate: float, months: int) -> float:
    """EMI = P * r * (1+r)^n / ((1+r)^n - 1)"""
    if months <= 0:
        raise ValueError("Tenure must be > 0 months")
    if principal <= 0:
        return 0.0
    r = annual_rate / 12 / 100
    if r == 0:
        return principal / months
    factor = (1 + r) ** months
    return principal * r * factor / (factor - 1)


def amortization_schedule(principal: float, annual_rate: float, months: int | None,
                          loan_type: str = "Personal Loan") -> pd.DataFrame:
    """Month-wise schedule. If months is None, the UAE default tenure for loan_type is used."""
    if not months:
        months = LOAN_TYPES[loan_type].tenure_months

    emi = calculate_emi(principal, annual_rate, months)
    r = annual_rate / 12 / 100
    balance = principal
    total_paid = 0.0
    cum_interest = 0.0
    cum_principal = 0.0
    rows = []

    for m in range(1, months + 1):
        interest = balance * r
        principal_part = emi - interest
        if m == months:  # absorb rounding on last instalment
            principal_part = balance
        balance -= principal_part
        total_paid += interest + principal_part
        cum_interest += interest
        cum_principal += principal_part
        total_payable = emi * months
        rows.append({
            "Month": m,
            "EMI (AED)": round(interest + principal_part, 2),
            "Principal Paid (AED)": round(principal_part, 2),
            "Interest Paid (AED)": round(interest, 2),
            "Cumulative Interest (AED)": round(cum_interest, 2),
            "Cumulative Principal (AED)": round(cum_principal, 2),
            "Left-over Principal (AED)": round(max(balance, 0), 2),
            "Remaining Balance incl. Interest (AED)": round(max(total_payable - total_paid, 0), 2),
        })
    return pd.DataFrame(rows)
