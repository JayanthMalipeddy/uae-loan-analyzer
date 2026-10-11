"""Loan EMI Calculator module - UI only.

Calculations are unchanged (core.calculate_emi / core.amortization_schedule).
Session-state keys are unchanged ({card}_amt, {card}_rate, {card}_def, {card}_ten), so the
Loan Analyzer hand-off keeps working. One product is shown at a time (design preview).
"""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .core import LOAN_TYPES, amortization_schedule, calculate_emi

NAVY, TEAL, GOLD, SLATE, LINE = "#142D42", "#237A68", "#B89658", "#677683", "#E4E8E7"
WIDGET_SUFFIXES = ("_amt", "_amt_sl", "_rate", "_def", "_ten")

_ICON = {
    "Personal Loan": "<circle cx='12' cy='7' r='4'/><path d='M4 21v-2a8 8 0 0 1 16 0v2'/>",
    "Home Loan": "<path d='m3 11 9-8 9 8M5 10v11h14V10M9 21v-7h6v7'/>",
    "Auto Loan": "<path d='m5 7-2 6v6h18v-6l-2-6H5ZM3 13h18M7 16h.01M17 16h.01M6 19v2M18 19v2'/>",
}
I_SHIELD = "<path d='m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z'/><path d='m8 12 3 3 5-6'/>"


def svg(path: str, size: int = 23) -> str:
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{path}</svg>')


def H(s: str):
    st.markdown("\n".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


def fmt(x: float) -> str:
    return f"AED {x:,.2f}"


def short(x: float) -> str:
    if x >= 1_000_000:
        return f"AED {x/1_000_000:,.2f}M"
    if x >= 1_000:
        return f"AED {x/1_000:,.1f}K"
    return f"AED {x:,.0f}"


def footer():
    H("""<footer class="ua-footer"><div><b>UAE Loan Analyzer</b><span>Independent loan planning</span></div>
         <p>Estimates, not a bank offer. Your lender's statement and terms remain the final reference.</p>
         <span class="ua-footer-note">All amounts in AED</span></footer>""")


def _v(key: str, default):
    """Pass the default only if the value is not already in session state (pre-filled or user-set)."""
    return {} if key in st.session_state else {"value": default}


def reset_calculator():
    for k in [k for k in st.session_state if k.endswith(WIDGET_SUFFIXES) and k.split("_")[0] in LOAN_TYPES]:
        del st.session_state[k]
    st.session_state.pop("calc_prefill_info", None)


def _scenario(key: str):
    """Current (amount, rate, tenure) for a product - from session state or the preset."""
    d, ss = LOAN_TYPES[key], st.session_state
    amount = ss.get(f"{key}_amt", int(d.amount))
    rate = ss.get(f"{key}_rate", d.rate)
    tenure = d.tenure_months if ss.get(f"{key}_def", True) else ss.get(f"{key}_ten", d.tenure_months)
    return amount, rate, tenure


def _sync_from_slider(key: str):
    st.session_state[f"{key}_amt"] = st.session_state[f"{key}_amt_sl"]


def _product_changed():
    if st.session_state.calc_product is None:  # clicking the active segment deselects it - keep current
        st.session_state.calc_product = st.session_state.get("_calc_last", "Personal Loan")


# ---------------------------------------------------------------- inputs
def _inputs(key: str):
    d = LOAN_TYPES[key]
    lo, hi = int(d.min_amount), int(d.max_amount)
    H(f"""<div class="ua-loan-head"><div class="ua-icon-tile">{svg(_ICON[key])}</div>
          <div><h3>{key}</h3><small>Adjust your scenario below</small></div></div>""")

    amount = st.number_input("Loan amount (AED)", lo, hi, step=5_000, key=f"{key}_amt", **_v(f"{key}_amt", int(d.amount)))
    # slider mirrors the number input (same value, coarser step)
    st.session_state[f"{key}_amt_sl"] = int(min(max(round(amount / 5_000) * 5_000, lo), hi))
    st.slider("Loan amount slider", lo, hi, step=5_000, key=f"{key}_amt_sl", label_visibility="collapsed",
              on_change=_sync_from_slider, args=(key,))
    H(f"<div class='ua-slider-range'><span>{short(lo)}</span><span>{short(hi)}</span></div>")

    rate = st.number_input("Annual interest rate (%)", 0.0, 20.0, step=0.01, format="%.2f", key=f"{key}_rate",
                           **_v(f"{key}_rate", d.rate))
    use_default = st.toggle(f"Use preset tenure · {d.tenure_months} months", key=f"{key}_def", **_v(f"{key}_def", True))
    tenure = d.tenure_months
    if use_default:
        st.caption(f"Repayment over {d.tenure_months} months. Turn off the preset to adjust.")
    else:
        tenure = st.slider("Tenure (months)", 6, d.max_tenure_months, step=1 if d.max_tenure_months <= 60 else 6,
                           key=f"{key}_ten", **_v(f"{key}_ten", d.tenure_months))
    H(f"<p class='ua-private-note'>{svg(I_SHIELD, 14)}<span>Presets are illustrative. Fees, insurance and "
      f"changing rates are not included.</span></p>")
    return amount, rate, tenure


def _estimate(amount, rate, tenure, emi, total):
    H(f"""<div class="ua-estimate"><div class="ua-eyebrow">Your repayment estimate</div>
          <div class="ua-emi-label">Monthly instalment</div>
          <div class="ua-emi"><small>AED</small>{emi:,.2f}</div>
          <div class="ua-emi-note">Fixed monthly payment · {rate:.2f}% annual reducing rate</div>
          <div class="ua-estimate-stats">
            <div><span class="label">Loan tenure</span><strong>{tenure} months</strong></div>
            <div><span class="label">Total interest</span><strong>AED {total - amount:,.0f}</strong></div>
            <div><span class="label">Total repayment</span><strong>AED {total:,.0f}</strong></div>
          </div></div>""")
    p = amount / total * 100 if total else 100
    with st.container(key="card_calc_split"):
        H(f"""<div class="panel-title">Where your payments go</div><div class="panel-sub">The split over the full loan term.</div>
              <div class="ua-split-bar" role="img" aria-label="Principal is {p:.1f} percent of total repayment">
              <i style="width:{p:.4f}%"></i><b></b></div>
              <div class="ua-split-labels"><div><span class="ua-legend-dot"></span>Principal · {p:.1f}%<b>AED {amount:,.0f}</b></div>
              <div><span class="ua-legend-dot gold"></span>Interest · {100 - p:.1f}%<b>AED {total - amount:,.0f}</b></div></div>""")


def _chart(df: pd.DataFrame):
    fig = go.Figure()
    fig.add_bar(x=df["Month"], y=df["Principal Paid (AED)"], name="Principal", marker=dict(color=TEAL, line_width=0))
    fig.add_bar(x=df["Month"], y=df["Interest Paid (AED)"], name="Interest", marker=dict(color=GOLD, line_width=0))
    fig.add_scatter(x=df["Month"], y=df["Left-over Principal (AED)"], name="Outstanding balance", yaxis="y2",
                    mode="lines", line=dict(color=NAVY, width=2))
    fig.update_layout(
        barmode="stack", bargap=.13 if len(df) <= 72 else 0, height=340, margin=dict(t=20, b=35, l=12, r=22), hovermode="x unified",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", separators=".,",
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=12, color=SLATE),
        hoverlabel=dict(bgcolor="white", bordercolor=LINE, font=dict(color=NAVY, size=12)),
        legend=dict(orientation="h", x=0, y=-0.18, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(title="Repayment month", showgrid=False, zeroline=False, linecolor=LINE, tickfont=dict(size=11)),
        yaxis=dict(title="Instalment split (AED)", gridcolor="#EDF0EE", zeroline=False, tickfont=dict(size=11)),
        yaxis2=dict(title="Balance (AED)", overlaying="y", side="right", showgrid=False, rangemode="tozero",
                    tickfont=dict(size=11)),
    )
    st.plotly_chart(fig, width="stretch", key="calc_chart", config={"displayModeBar": False})


def _compare_table() -> pd.DataFrame:
    rows = []
    for k in LOAN_TYPES:
        amount, rate, tenure = _scenario(k)
        emi = calculate_emi(amount, rate, tenure)
        rows.append({"Product": k, "Amount (AED)": amount, "Rate (%)": rate, "Months": tenure,
                     "Monthly EMI (AED)": round(emi, 2), "Interest (AED)": round(emi * tenure - amount, 0),
                     "Repayment (AED)": round(emi * tenure, 0)})
    return pd.DataFrame(rows)


def render():
    info = st.session_state.get("calc_prefill_info")

    h1, h2 = st.columns([3, 1], vertical_alignment="top")
    with h1:
        H("""<div class="ua-page-heading"><div class="ua-eyebrow">Plan / EMI calculator</div>
             <h1>Plan a better repayment.</h1>
             <p>Change the amount, rate and tenure. See the impact on every dirham.</p></div>""")
    with h2.container(key="calc_head_actions"):
        st.button("Reset all scenarios", on_click=reset_calculator, key="calc_reset", width="stretch")

    if info:
        notes = "".join(f"<br>· {n}" for n in info["notes"])
        H(f"<div class='ua-prefill'><b>{info['label']}</b> was loaded into the <b>{info['card']}</b> scenario. "
          f"Adjust the values to explore what-if scenarios.{notes}</div>")

    if st.session_state.get("calc_product") is None:
        st.session_state.calc_product = st.session_state.get("_calc_last", "Personal Loan")
    st.segmented_control("Loan product", list(LOAN_TYPES), key="calc_product", on_change=_product_changed,
                         label_visibility="collapsed")
    key = st.session_state.calc_product or "Personal Loan"
    st.session_state._calc_last = key

    with st.container(key="calc_row"):
        c1, c2 = st.columns([1, 1.15], gap="medium")
        with c1, st.container(key="card_calc_inputs"):
            amount, rate, tenure = _inputs(key)
        emi = calculate_emi(amount, rate, tenure)
        total = emi * tenure
        with c2:
            _estimate(amount, rate, tenure, emi, total)

    df = amortization_schedule(amount, rate, tenure, key)
    H("<div class='ua-section'><h2>Your repayment, month by month.</h2><span>Based on this scenario</span></div>")
    t1, t2, t3 = st.tabs(["Repayment journey", "Monthly schedule", "Compare loan types"])
    with t1, st.container(key="card_calc_chart"):
        _chart(df)
    with t2:
        st.dataframe(df, hide_index=True, width="stretch", height=430,
                     column_config={c: st.column_config.NumberColumn(format="localized")
                                    for c in df.columns if c != "Month"})
    with t3:
        st.dataframe(_compare_table(), hide_index=True, width="stretch", column_config={
            c: st.column_config.NumberColumn(format="localized")
            for c in ("Amount (AED)", "Monthly EMI (AED)", "Interest (AED)", "Repayment (AED)")})
        st.caption("Each row uses your most recent scenario for that product, or the original model preset. "
                   "These are different loan configurations, not competing bank offers.")
    st.download_button("Download this schedule ↓", df.to_csv(index=False),
                       file_name=f"{key.replace(' ', '_').lower()}_schedule.csv", key="calc_dl", width="stretch")
    footer()
