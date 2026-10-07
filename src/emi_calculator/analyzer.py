"""Loan Analyzer engine (pure Python, no UI).

Reads a loan file (Excel/CSV), normalises columns, and computes per-loan and
portfolio metrics. Re-uses the EMI maths from core.py - nothing is duplicated.
"""
from __future__ import annotations

import io
import math
import re
from dataclasses import dataclass, field
from datetime import date

import pandas as pd

from .core import LOAN_TYPES, amortization_schedule, calculate_emi

# ------------------------------------------------------------------ schema
# canonical name -> accepted header spellings (compared lower-case, alphanumerics only)
COLUMN_ALIASES: dict[str, list[str]] = {
    "Loan_ID": ["loanid", "id", "loanno", "loannumber", "accountno", "accountnumber", "account", "reference"],
    "Loan_Type": ["loantype", "type", "product", "category", "loancategory"],
    "Bank": ["bank", "lender", "bankname", "provider"],
    "Loan_Amount": ["loanamount", "amount", "principal", "sanctionedamount", "originalamount", "loanamountaed"],
    "Interest_Rate": ["interestrate", "rate", "interest", "annualrate", "roi", "interestrate%", "interestratepa"],
    "Tenure_Months": ["tenuremonths", "tenure", "term", "months", "duration", "loantenure"],
    "Start_Date": ["startdate", "disbursementdate", "loanstartdate", "date", "disbursaldate"],
    "EMI": ["emi", "monthlyemi", "installment", "instalment", "monthlypayment", "emiaed"],
    "Outstanding_Principal": ["outstandingprincipal", "outstanding", "balance", "outstandingbalance", "currentbalance"],
    "Prepayment": ["prepayment", "prepaidamount", "prepayments", "lumpsumpaid", "partpayment"],
}
REQUIRED = ["Loan_Amount", "Interest_Rate", "Tenure_Months"]
FRIENDLY = {"Loan_Amount": "Loan amount", "Interest_Rate": "Interest rate", "Tenure_Months": "Loan tenure"}

TEMPLATE_GUIDE = pd.DataFrame([
    ["Loan_ID", "Optional", "Text", "HL-001", "Your own reference for the loan"],
    ["Loan_Type", "Optional", "Text", "Home Loan", "Personal Loan, Home Loan or Auto Loan"],
    ["Bank", "Optional", "Text", "Bank A", "Lender name"],
    ["Loan_Amount", "Required", "Number (AED)", "1800000", "Original amount borrowed"],
    ["Interest_Rate", "Required", "Number (% p.a.)", "4.49", "Annual rate - 4.49 or 0.0449 both work"],
    ["Tenure_Months", "Required", "Number / text", "300", "Total tenure - '25 years' also works"],
    ["Start_Date", "Recommended", "Date", "2021-03-01", "Loan start - used to work out what is already paid"],
    ["EMI", "Optional", "Number (AED)", "10000", "Bank's EMI - calculated if missing"],
    ["Outstanding_Principal", "Optional", "Number (AED)", "1500000", "Current balance from your statement - overrides the estimate"],
    ["Prepayment", "Optional", "Number (AED)", "10000", "Total lump-sum prepaid so far"],
], columns=["Field", "Required", "Type", "Sample Value", "Description"])


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9%]", "", str(s).lower())


def _to_number(v) -> float | None:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = re.sub(r"[^0-9.\-]", "", str(v))
    try:
        return float(s) if s not in ("", ".", "-") else None
    except ValueError:
        return None


def _to_months(v) -> int | None:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return None
    n = _to_number(v)
    if n is None:
        return None
    if isinstance(v, str) and re.search(r"y(ea)?r", v.lower()):
        n *= 12
    return int(round(n))


def map_loan_type(raw) -> str | None:
    """Map free text to one of the calculator's loan cards, or None."""
    s = str(raw or "").lower()
    has = lambda *ws: any(re.search(rf"\b{w}s?\b", s) for w in ws)  # noqa: E731
    if has("home", "mortgage", "house", "property"):
        return "Home Loan"
    if has("auto", "car", "vehicle", "motor"):
        return "Auto Loan"
    if has("personal"):
        return "Personal Loan"
    return None


# ------------------------------------------------------------------ loading
@dataclass
class LoadResult:
    data: pd.DataFrame
    issues: list[str] = field(default_factory=list)
    mapped: dict[str, str] = field(default_factory=dict)   # canonical -> original header
    missing: list[str] = field(default_factory=list)       # required fields not found (friendly names)
    skipped: int = 0


def read_file(content: bytes, filename: str) -> pd.DataFrame:
    if filename.lower().endswith(".csv"):
        return pd.read_csv(io.BytesIO(content))
    return pd.read_excel(io.BytesIO(content))  # first sheet


def clean_loans(raw: pd.DataFrame) -> LoadResult:
    issues: list[str] = []
    lookup = {_norm(c): c for c in raw.columns}
    mapped: dict[str, str] = {}
    for canon, aliases in COLUMN_ALIASES.items():
        for a in [_norm(canon)] + aliases:
            if a in lookup:
                mapped[canon] = lookup[a]
                break

    missing = [c for c in REQUIRED if c not in mapped]
    if missing:
        issues.append("Missing required column(s): " + ", ".join(missing)
                      + ". Download the template to see the expected format.")
        return LoadResult(pd.DataFrame(), issues, mapped, [FRIENDLY[m] for m in missing])

    df = pd.DataFrame({c: raw[src] for c, src in mapped.items()})
    df = df.dropna(how="all")

    df["Loan_Amount"] = df["Loan_Amount"].map(_to_number)
    df["Interest_Rate"] = df["Interest_Rate"].map(_to_number)
    df["Tenure_Months"] = df["Tenure_Months"].map(_to_months)
    # rates given as decimals (0.0449) -> percent
    df.loc[df["Interest_Rate"].notna() & (df["Interest_Rate"] < 1) & (df["Interest_Rate"] > 0),
           "Interest_Rate"] *= 100
    for c in ("EMI", "Outstanding_Principal", "Prepayment"):
        df[c] = df[c].map(_to_number) if c in df else None
    df["Start_Date"] = (pd.to_datetime(df["Start_Date"], errors="coerce", dayfirst=False)
                        if "Start_Date" in df else pd.NaT)
    if "Loan_ID" not in df:
        df["Loan_ID"] = [f"Loan {i + 1}" for i in range(len(df))]
    df["Loan_ID"] = df["Loan_ID"].fillna(pd.Series([f"Loan {i + 1}" for i in range(len(df))],
                                                   index=df.index)).astype(str)
    df["Loan_Type"] = df["Loan_Type"].fillna("Loan").astype(str) if "Loan_Type" in df else "Loan"
    df["Bank"] = df["Bank"].fillna("-").astype(str) if "Bank" in df else "-"

    bad = (df["Loan_Amount"].isna() | (df["Loan_Amount"] <= 0)
           | df["Interest_Rate"].isna() | (df["Interest_Rate"] < 0) | (df["Interest_Rate"] > 50)
           | df["Tenure_Months"].isna() | (df["Tenure_Months"] <= 0))
    skipped = int(bad.sum())
    if bad.any():
        issues.append(f"Skipped {skipped} row(s) with a missing or invalid amount, rate or tenure: "
                      + ", ".join(df.loc[bad, "Loan_ID"].head(5)))
    df = df[~bad].copy()
    df["Tenure_Months"] = df["Tenure_Months"].astype(int)
    if df["Start_Date"].isna().any() and len(df):
        issues.append("Some loans have no start date - they are treated as starting today.")
    if df["Loan_ID"].duplicated().any():
        df["Loan_ID"] = df["Loan_ID"] + df.groupby("Loan_ID").cumcount().map(lambda n: "" if n == 0 else f"-{n + 1}")
    return LoadResult(df.reset_index(drop=True), issues, mapped, [], skipped)


# ------------------------------------------------------------------ maths helpers
def months_between(start: date, as_of: date) -> int:
    """Number of monthly instalments due between start and as_of (first EMI one month after start)."""
    m = (as_of.year - start.year) * 12 + (as_of.month - start.month)
    if as_of.day < start.day:
        m -= 1
    return max(m, 0)


def add_months(d: date, n: int) -> date:
    y, m = divmod(d.month - 1 + n, 12)
    y += d.year
    m += 1
    day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 or y % 400 == 0) else 28,
                      31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date(y, m, day)


def simulate(balance: float, annual_rate: float, emi: float, max_months: int = 1200):
    """Repay `balance` with a fixed `emi`. Returns (months, total_interest, balances_after_each_month)."""
    r = annual_rate / 12 / 100
    balances, interest_total, months = [], 0.0, 0
    while balance > 0.005 and months < max_months:
        interest = balance * r
        principal = min(emi - interest, balance)
        if principal <= 0:  # EMI does not cover interest
            return math.inf, math.inf, balances
        interest_total += interest
        balance -= principal
        months += 1
        balances.append(max(balance, 0.0))
    return months, interest_total, balances


# ------------------------------------------------------------------ analysis
def analyze_loans(df: pd.DataFrame, as_of: date | None = None) -> pd.DataFrame:
    as_of = as_of or date.today()
    rows = []
    for _, L in df.iterrows():
        P, rate, n = float(L["Loan_Amount"]), float(L["Interest_Rate"]), int(L["Tenure_Months"])
        start = L["Start_Date"].date() if pd.notna(L["Start_Date"]) else as_of
        calc_emi = calculate_emi(P, rate, n)
        emi = float(L["EMI"]) if pd.notna(L.get("EMI")) and L.get("EMI") else calc_emi

        sched = amortization_schedule(P, rate, n)
        paid = min(months_between(start, as_of), n)
        sched_bal = float(sched["Left-over Principal (AED)"].iloc[paid - 1]) if paid else P
        interest_to_date = float(sched["Cumulative Interest (AED)"].iloc[paid - 1]) if paid else 0.0

        prepay = float(L["Prepayment"]) if pd.notna(L.get("Prepayment")) else 0.0
        if pd.notna(L.get("Outstanding_Principal")):
            outstanding, source = max(float(L["Outstanding_Principal"]), 0.0), "Statement"
        else:
            outstanding, source = max(sched_bal - prepay, 0.0), "Estimated"

        rem_months, rem_interest, _ = simulate(outstanding, rate, emi)
        if rem_months is math.inf:  # EMI too low to ever clear - fall back to schedule
            rem_months, rem_interest = n - paid, max(emi * (n - paid) - outstanding, 0.0)

        status = "Closed" if outstanding <= 0.5 else ("Not started" if paid == 0 else "Active")
        rows.append({
            "Loan_ID": L["Loan_ID"], "Bank": L["Bank"], "Loan_Type": L["Loan_Type"],
            "Calculator_Card": map_loan_type(L["Loan_Type"]),
            "Loan_Amount": P, "Interest_Rate": rate, "Tenure_Months": n, "Start_Date": start,
            "EMI": emi, "EMI_Calculated": calc_emi,
            "EMIs_Paid": paid, "Remaining_Months": int(rem_months),
            "Prepayment": prepay, "Outstanding_Principal": outstanding, "Outstanding_Source": source,
            "Principal_Repaid": P - outstanding,
            "Interest_Paid_To_Date": interest_to_date, "Interest_Remaining": rem_interest,
            "Total_Interest": interest_to_date + rem_interest,
            "Progress_Pct": (P - outstanding) / P * 100 if P else 0,
            "Payoff_Date": add_months(as_of, int(rem_months)) if status != "Closed" else add_months(start, paid),
            "Status": status,
        })
    return pd.DataFrame(rows)


def portfolio_summary(a: pd.DataFrame) -> dict:
    active = a[a["Status"] != "Closed"]
    out = active["Outstanding_Principal"].sum()
    return {
        "loans": len(a), "active": len(active), "closed": int((a["Status"] == "Closed").sum()),
        "borrowed": a["Loan_Amount"].sum(),
        "outstanding": out,
        "repaid": a["Principal_Repaid"].sum(),
        "monthly_emi": active["EMI"].sum(),
        "interest_paid": a["Interest_Paid_To_Date"].sum(),
        "interest_remaining": active["Interest_Remaining"].sum(),
        "weighted_rate": (active["Interest_Rate"] * active["Outstanding_Principal"]).sum() / out if out else 0,
        "debt_free": active["Payoff_Date"].max() if len(active) else None,
        "progress": a["Principal_Repaid"].sum() / a["Loan_Amount"].sum() * 100 if len(a) else 0,
        "remaining_months": int(active["Remaining_Months"].max()) if len(active) else 0,
        "first_start": a["Start_Date"].min() if len(a) else None,
    }


def balance_projection(a: pd.DataFrame, as_of: date | None = None) -> pd.DataFrame:
    """Month-by-month projected outstanding principal per active loan (long format)."""
    as_of = as_of or date.today()
    recs = []
    for _, L in a[a["Status"] != "Closed"].iterrows():
        _, _, bals = simulate(L["Outstanding_Principal"], L["Interest_Rate"], L["EMI"])
        recs.append({"Date": as_of, "Loan": L["Loan_ID"], "Outstanding": L["Outstanding_Principal"]})
        recs += [{"Date": add_months(as_of, i + 1), "Loan": L["Loan_ID"], "Outstanding": b}
                 for i, b in enumerate(bals)]
    return pd.DataFrame(recs, columns=["Date", "Loan", "Outstanding"])


def yearly_flows(a: pd.DataFrame, as_of: date | None = None) -> pd.DataFrame:
    """Principal vs interest per calendar year, across all loans.

    Paid years use each loan's original schedule up to today; future years use the
    projection from today's outstanding balance and EMI (so prepayments are respected).
    """
    as_of = as_of or date.today()
    recs = []
    for _, L in a.iterrows():
        sched = amortization_schedule(L["Loan_Amount"], L["Interest_Rate"], int(L["Tenure_Months"]))
        for m in range(1, int(L["EMIs_Paid"]) + 1):
            row = sched.iloc[m - 1]
            recs.append((add_months(L["Start_Date"], m).year, "Paid",
                         row["Principal Paid (AED)"], row["Interest Paid (AED)"]))
        if L["Status"] == "Closed":
            continue
        bal, r = L["Outstanding_Principal"], L["Interest_Rate"] / 1200
        _, _, bals = simulate(bal, L["Interest_Rate"], L["EMI"])
        for i, nb in enumerate(bals):
            interest = bal * r
            recs.append((add_months(as_of, i + 1).year, "Projected", bal - nb, interest))
            bal = nb
    df = pd.DataFrame(recs, columns=["Year", "Kind", "Principal", "Interest"])
    if df.empty:
        return df
    return df.groupby(["Year", "Kind"], as_index=False)[["Principal", "Interest"]].sum()


def prepayment_whatif(loan: pd.Series, extra_pct: float = 10) -> dict | None:
    """Effect of paying `extra_pct`% more than the EMI every month on the remaining balance."""
    if loan["Status"] == "Closed" or loan["Outstanding_Principal"] <= 0:
        return None
    m0, i0, _ = simulate(loan["Outstanding_Principal"], loan["Interest_Rate"], loan["EMI"])
    m1, i1, _ = simulate(loan["Outstanding_Principal"], loan["Interest_Rate"], loan["EMI"] * (1 + extra_pct / 100))
    if math.inf in (m0, m1):
        return None
    return {"extra": loan["EMI"] * extra_pct / 100, "interest_saved": i0 - i1, "months_saved": m0 - m1}


def _best_prepayment(active: pd.DataFrame):
    options = [(prepayment_whatif(L), L) for _, L in active.iterrows()]
    options = [(w, L) for w, L in options if w and w["interest_saved"] > 1]
    return max(options, key=lambda o: o[0]["interest_saved"]) if options else (None, None)


def build_insights(a: pd.DataFrame, monthly_salary: float | None = None) -> list[tuple[str, str]]:
    """Plain-English insights as (icon, text) tuples (compact form)."""
    s = portfolio_summary(a)
    ins: list[tuple[str, str]] = []
    ins.append(("📈", f"You have repaid **{s['progress']:.0f}%** of the AED {s['borrowed']:,.0f} you borrowed "
                      f"across {s['loans']} loan{'s' if s['loans'] != 1 else ''}."))
    active = a[a["Status"] != "Closed"]
    if s["closed"]:
        ins.append(("✅", f"**{s['closed']}** loan{'s are' if s['closed'] > 1 else ' is'} fully repaid."))
    if len(active):
        ins.append(("💸", f"If you keep paying as scheduled you will still pay **AED {s['interest_remaining']:,.0f}** "
                          f"in interest. You'll be debt-free by **{s['debt_free']:%B %Y}**."))
        top = active.sort_values("Interest_Rate", ascending=False).iloc[0]
        if len(active) > 1:
            ins.append(("🎯", f"**{top['Loan_ID']}** ({top['Loan_Type']}) has your highest rate at "
                              f"**{top['Interest_Rate']:.2f}%**. Every extra dirham you pay on it saves the most interest."))
        w, L = _best_prepayment(active)
        if w:
            m = w["months_saved"]
            ins.append(("⚡", f"Paying **AED {w['extra']:,.0f}/month extra** (10% more) on {L['Loan_ID']} would save "
                              f"about **AED {w['interest_saved']:,.0f}** in interest"
                              + (f" and finish **{m} month{'s' if m != 1 else ''}** sooner." if m else ".")))
        heavy = active.sort_values("Interest_Remaining", ascending=False).iloc[0]
        if len(active) > 1 and heavy["Loan_ID"] != top["Loan_ID"]:
            share = heavy["Interest_Remaining"] / s["interest_remaining"] * 100 if s["interest_remaining"] else 0
            ins.append(("🏠", f"**{heavy['Loan_ID']}** accounts for **{share:.0f}%** of your remaining interest "
                              f"because of its long tenure."))
    if monthly_salary and monthly_salary > 0 and len(active):
        dbr = s["monthly_emi"] / monthly_salary * 100
        if dbr <= 50:
            ins.append(("🛡️", f"Your EMIs use **{dbr:.0f}%** of your salary, within the UAE Central Bank's 50% "
                               f"debt-burden limit (room of AED {monthly_salary * 0.5 - s['monthly_emi']:,.0f}/month)."))
        else:
            ins.append(("⚠️", f"Your EMIs use **{dbr:.0f}%** of your salary, above the UAE Central Bank's 50% "
                               f"debt-burden limit. New credit may be hard to get."))
    return ins


def key_insights(a: pd.DataFrame, monthly_salary: float | None = None) -> list[dict]:
    """Structured insights for the dashboard: {title, text, tone}. Every figure comes from the analysis."""
    s = portfolio_summary(a)
    active = a[a["Status"] != "Closed"]
    plural = "s" if s["loans"] != 1 else ""
    out: list[dict] = []
    if s["borrowed"]:
        out.append({"title": "Your outstanding balance", "tone": "navy",
                    "text": f"Your outstanding principal is **AED {s['outstanding']:,.0f}**, "
                            f"**{s['outstanding'] / s['borrowed'] * 100:.0f}%** of the AED {s['borrowed']:,.0f} "
                            f"originally borrowed."})
    out.append({"title": "Interest impact", "tone": "gold",
                "text": f"You have paid approximately **AED {s['interest_paid']:,.0f}** in interest to date"
                        + (f", with about **AED {s['interest_remaining']:,.0f}** still to come if you pay as scheduled."
                           if len(active) else ".")})
    out.append({"title": "Repayment progress", "tone": "teal",
                "text": f"You have completed approximately **{s['progress']:.0f}%** of your repayment journey"
                        + (f" across {s['loans']} loan{plural}" if s["loans"] > 1 else "")
                        + (f". **{s['closed']}** loan{'s are' if s['closed'] > 1 else ' is'} fully repaid." if s["closed"] else ".")})
    if len(active):
        nxt = active.sort_values("Remaining_Months").iloc[0]
        if len(active) > 1:
            out.append({"title": "Next milestone", "tone": "teal",
                        "text": f"**{nxt['Loan_ID']}** is projected to close in **{nxt['Payoff_Date']:%B %Y}**, "
                                f"freeing up **AED {nxt['EMI']:,.0f}** a month. All loans are projected to end by "
                                f"**{s['debt_free']:%B %Y}**."})
        else:
            out.append({"title": "Next milestone", "tone": "teal",
                        "text": f"Your projected loan completion date is **{s['debt_free']:%B %Y}**, "
                                f"in {s['remaining_months']} months."})
        w, L = _best_prepayment(active)
        if w:
            m = w["months_saved"]
            out.append({"title": "Opportunity", "tone": "gold",
                        "text": f"Paying **AED {w['extra']:,.0f} a month more** (10% above the EMI) on {L['Loan_ID']} "
                                f"would save about **AED {w['interest_saved']:,.0f}** in interest"
                                + (f" and finish **{m} month{'s' if m != 1 else ''}** sooner." if m else ".")})
        if len(active) > 1:
            top = active.sort_values("Interest_Rate", ascending=False).iloc[0]
            out.append({"title": "Highest rate", "tone": "navy",
                        "text": f"**{top['Loan_ID']}** ({top['Loan_Type']}) carries your highest rate at "
                                f"**{top['Interest_Rate']:.2f}%**. Extra payments there save the most per dirham."})
    if monthly_salary and monthly_salary > 0 and len(active):
        dbr = s["monthly_emi"] / monthly_salary * 100
        ok = dbr <= 50
        out.append({"title": "Debt-burden ratio", "tone": "teal" if ok else "warn",
                    "text": f"Your EMIs use **{dbr:.0f}%** of your monthly salary, "
                            + ("within the UAE Central Bank's 50% limit." if ok
                               else "above the UAE Central Bank's 50% limit. New credit may be difficult.")})
    return out


# ------------------------------------------------------------------ calculator hand-off
def _snap(v: float, lo: float, hi: float, step: float) -> float:
    v = min(max(v, lo), hi)
    return lo + round((v - lo) / step) * step


def build_prefill(loan: pd.Series, card: str, mode: str = "remaining") -> tuple[dict, list[str]]:
    """Session-state values for the EMI Calculator card + notes on any adjustments.

    mode = "remaining" (outstanding balance & remaining months) or "original" (original terms).
    """
    d = LOAN_TYPES[card]
    notes: list[str] = []
    if mode == "remaining":
        amount, months = float(loan["Outstanding_Principal"]), int(loan["Remaining_Months"])
    else:
        amount, months = float(loan["Loan_Amount"]), int(loan["Tenure_Months"])

    amt = int(_snap(amount, d.min_amount, d.max_amount, 5_000))
    if abs(amt - amount) >= 1:
        notes.append(f"Amount set to AED {amt:,} (the calculator moves in AED 5,000 steps"
                     + (" and has limits" if not d.min_amount <= amount <= d.max_amount else "") + ").")
    rate = round(_snap(float(loan["Interest_Rate"]), 0.0, 20.0, 0.01), 2)
    if abs(rate - loan["Interest_Rate"]) > 1e-9:
        notes.append(f"Rate rounded to {rate:.2f}%.")

    values = {f"{card}_amt": amt, f"{card}_rate": rate}
    tstep = 1 if d.max_tenure_months <= 60 else 6
    if months == d.tenure_months:
        values[f"{card}_def"] = True
    else:
        ten = int(_snap(months, 6, d.max_tenure_months, tstep))
        values[f"{card}_def"] = False
        values[f"{card}_ten"] = ten
        if ten != months:
            notes.append(f"Tenure set to {ten} months (allowed range for {card}: 6-{d.max_tenure_months}).")
    return values, notes


# ------------------------------------------------------------------ sample / template
def sample_loans() -> pd.DataFrame:
    return pd.DataFrame([
        ["HL-001", "Home Loan", "Bank A", 1_800_000, 4.49, 300, "2021-03-01", None, None, None],
        ["AL-002", "Auto Loan", "Bank B", 140_000, 3.25, 60, "2023-07-15", None, None, None],
        ["PL-003", "Personal Loan", "Bank C", 120_000, 6.99, 48, "2024-01-10", None, None, 10_000],
        ["PL-004", "Personal Loan", "Bank A", 60_000, 7.50, 36, "2022-05-01", None, None, None],
        ["AL-005", "Auto Loan", "Bank D", 95_000, 2.99, 48, "2026-09-01", None, None, None],
    ], columns=["Loan_ID", "Loan_Type", "Bank", "Loan_Amount", "Interest_Rate", "Tenure_Months",
                "Start_Date", "EMI", "Outstanding_Principal", "Prepayment"])


def template_bytes() -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as xw:
        sample_loans().to_excel(xw, sheet_name="Loans", index=False)
        TEMPLATE_GUIDE.to_excel(xw, sheet_name="Field Guide", index=False)
        for ws in xw.book.worksheets:
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = max(len(str(c.value or "")) for c in col) + 3
    return buf.getvalue()
