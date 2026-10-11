"""Loan Analyzer module (default / home) - UI only.

Business logic lives in analyzer.py and core.py (unchanged); this file is presentation.
Layout follows the approved design preview: landing (hero + upload), dashboard
(overview, path to debt-free, repayment snapshot, insights, detail tabs, next move).
"""
from __future__ import annotations

import re
import time
from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .analyzer import (TEMPLATE_GUIDE, analyze_loans, balance_projection, build_prefill, clean_loans,
                       key_insights, portfolio_summary, read_file, sample_loans, template_bytes, yearly_flows)
from .calculator_page import footer, reset_calculator, svg
from .core import LOAN_TYPES, amortization_schedule

CALC = "Loan EMI Calculator"
NAVY, TEAL, GOLD, SLATE, LINE = "#142D42", "#237A68", "#B89658", "#677683", "#E4E8E7"
SERIES = ["#142D42", "#237A68", "#B89658", "#6E8C9F", "#9AB5AA", "#8C7E96"]
PLOT_CFG = {"displayModeBar": False, "responsive": True}

# monoline icons from the design preview
I = {
    "logo": "<path d='M4 18 12 4l8 14M7 13h10M8 18h8'/>",
    "person": "<circle cx='12' cy='7' r='4'/><path d='M4 21v-2a8 8 0 0 1 16 0v2'/>",
    "home": "<path d='m3 11 9-8 9 8M5 10v11h14V10M9 21v-7h6v7'/>",
    "car": "<path d='m5 7-2 6v6h18v-6l-2-6H5ZM3 13h18M7 16h.01M17 16h.01M6 19v2M18 19v2'/>",
    "trend": "<path d='M4 4v16h16M8 15l4-5 4 2 4-7'/>",
    "upload": "<path d='M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5'/>",
    "shield": "<path d='m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z'/><path d='m8 12 3 3 5-6'/>",
    "wallet": "<path d='M20 8V5H5a2 2 0 0 0 0 4h15v11H5a2 2 0 0 1-2-2V7'/><path d='M20 12h-5v5h5M17 14.5h.01'/>",
    "spark": "<path d='m12 3 2.3 6.7L21 12l-6.7 2.3L12 21l-2.3-6.7L3 12l6.7-2.3L12 3Z'/>",
    "calc": "<rect x='5' y='2' width='14' height='20' rx='2'/><path d='M8 6h8M8 11h1m3 0h1m3 0h.01M8 15h1m3 0h1m3 0h.01M8 19h1m3 0h4'/>",
    "clock": "<circle cx='12' cy='12' r='9'/><path d='M12 7v5l3 2'/>",
    "doc": "<path d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/><path d='M14 3v5h5'/>",
    "check": "<path d='m5 12 4.5 4.5L19 7'/>",
    "alert": "<circle cx='12' cy='12' r='9'/><path d='M12 7v6M12 16.5v.01'/>",
}


# ================================================================ helpers
def H(s: str):
    """Render HTML (strip indentation so Markdown never treats it as a code block)."""
    st.markdown("\n".join(line.strip() for line in s.strip().splitlines()), unsafe_allow_html=True)


def aed(x: float, dec: int = 0) -> str:
    return f"AED {x:,.{dec}f}"


def num(x: float, dec: int = 0, suffix: str = "") -> str:
    """Number with count-up hook (animated once, right after analysis)."""
    return f"<span class='num' data-v='{x:.{dec}f}' data-d='{dec}' data-s='{suffix}'>{x:,.{dec}f}{suffix}</span>"


def bold(t: str) -> str:
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)


def months_txt(m: int) -> str:
    y, r = divmod(int(m), 12)
    if y and r:
        return f"{y} yr {r} mo"
    return f"{y} yr" if y else f"{r} mo"


def section(title: str, note: str = ""):
    H(f"<div class='ua-section'><h2>{title}</h2>{f'<span>{note}</span>' if note else ''}</div>")


def _init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def chart_theme(fig: go.Figure, h: int = 290, **kw) -> go.Figure:
    base = dict(
        height=h, margin=dict(t=20, b=12, l=8, r=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=12, color=SLATE), separators=".,",
        legend=dict(orientation="h", x=0, y=-0.18, font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor="white", bordercolor=LINE, font=dict(color=NAVY, size=12)),
        colorway=SERIES, hovermode="x unified", bargap=.3)
    base.update(kw)
    fig.update_layout(**base)
    fig.update_xaxes(showgrid=False, zeroline=False, linecolor=LINE, tickfont=dict(size=11))
    fig.update_yaxes(gridcolor="#EDF0EE", zeroline=False, tickfont=dict(size=11))
    return fig


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"


# ================================================================ callbacks
def go_calculator():
    st.session_state.module = CALC


def _load_sample():
    st.session_state.az_data = clean_loans(sample_loans())
    st.session_state.az_source = "Sample portfolio"
    st.session_state.az_is_sample = True
    st.session_state.az_error = None
    _analyze()


def _analyze():
    st.session_state.az_analyzed = True
    st.session_state.az_animate = True
    st.session_state.scroll_to = "top"


def _new_file():
    for k in ("az_data", "az_source", "az_analyzed", "az_error", "az_file_id", "az_result", "az_is_sample"):
        st.session_state.pop(k, None)
    st.session_state.az_upload_n = st.session_state.get("az_upload_n", 0) + 1
    st.session_state.scroll_to = "top"


def _send_to_calculator(loan_id: str, card: str, mode: str):
    a = st.session_state.get("az_result")
    if a is None or loan_id not in set(a["Loan_ID"]):
        return
    loan = a.set_index("Loan_ID").loc[loan_id]
    values, notes = build_prefill(loan, card, mode)
    reset_calculator()                 # clear earlier pre-fills so only the chosen product gets this loan
    st.session_state.update(values)
    what = "remaining balance" if mode == "remaining" else "original terms"
    st.session_state.calc_prefill_info = {"card": card, "label": f"{loan_id} ({what})", "notes": notes}
    st.session_state.calc_product = card
    st.session_state.module = CALC


# ================================================================ landing
def _hero():
    H(f"""<section class="ua-landing-hero">
      <div><div class="ua-eyebrow">Your loans. In perspective.</div>
        <h1>A clearer view.<br>A smarter<br><em>repayment.</em></h1>
        <p class="ua-lead">Turn your loan data into a clear picture of what you owe, what interest costs, and what comes next.</p>
        <div class="ua-product-chips"><span>{svg(I['person'], 14)} Personal</span><span>{svg(I['home'], 14)} Home</span>
        <span>{svg(I['car'], 14)} Auto</span></div></div>
      <div class="ua-hero-bottom"><div class="ua-emblem">{svg(I['trend'], 21)}</div>
        <div><b>One view. Every loan.</b><span>From your first instalment to your final payment.</span></div></div>
    </section>""")


def _upload_card():
    _init("az_upload_n", 0)
    with st.container(key="card_upload"):
        H(f"""<div class="ua-card-top"><div class="ua-icon-tile">{svg(I['upload'])}</div><span class="ua-step">01 / GET STARTED</span></div>
              <div class="panel-title">Start with your loan file.</div>
              <div class="panel-sub">Upload your loan details. We will help you make sense of the numbers.</div>""")

        res, err = st.session_state.get("az_data"), st.session_state.get("az_error")
        if res is None or res.data.empty or err:
            up = st.file_uploader("Loan file", type=["xlsx", "xls", "csv"], label_visibility="collapsed",
                                  key=f"az_upload_{st.session_state.az_upload_n}")
            if up is not None and up.file_id != st.session_state.get("az_file_id"):
                st.session_state.az_file_id = up.file_id
                st.session_state.az_is_sample = False
                with st.spinner("Reading your file…"):
                    try:
                        st.session_state.az_data = clean_loans(read_file(up.getvalue(), up.name))
                        st.session_state.az_source = up.name
                        st.session_state.az_error = None
                    except Exception:
                        st.session_state.az_data = None
                        st.session_state.az_error = "read"
                st.rerun()

        res, err = st.session_state.get("az_data"), st.session_state.get("az_error")
        if err == "read":
            H(f"""<div class="ua-alert err">{svg(I['alert'], 20)}<div><b>We couldn't read this file</b>
                  Please upload a valid .xlsx, .xls or .csv file.</div></div>""")
            st.button("Choose another file", on_click=_new_file, key="az_retry_read", width="stretch")
        elif res is not None and res.data.empty:
            items = "".join(f"<li>{m}</li>" for m in res.missing) or "<li>No rows with a valid amount, rate and tenure</li>"
            H(f"""<div class="ua-alert err">{svg(I['alert'], 20)}<div><b>Some information is missing</b>
                  We found the file, but some required loan information could not be identified:<ul>{items}</ul>
                  Column names are matched flexibly (e.g. Amount, Rate, Tenure).</div></div>""")
            c1, c2 = st.columns(2)
            c1.button("Choose another file", on_click=_new_file, key="az_retry_missing", width="stretch")
            c2.download_button("Download template", template_bytes(), file_name="loan_template.xlsx",
                               key="az_tpl_err", width="stretch")
        elif res is not None:
            n = len(res.data)
            H(f"""<div class="ua-file-ok">{svg(I['doc'], 22)}<div><b>{st.session_state.az_source}</b>
                  <span>✓ File uploaded successfully · {n:,} loan record{'s' if n != 1 else ''} detected · Ready to analyze</span></div></div>""")
            notes = [i for i in res.issues if not i.startswith("Missing")]
            if notes:
                H("<div class='ua-alert warn'><div><b>Please note</b>" + "<br>".join(notes) + "</div></div>")
            st.button("Analyze Loan  →", type="primary", on_click=_analyze, key="az_analyze", width="stretch")
            st.button("Choose another file", on_click=_new_file, key="az_replace", width="stretch")
        else:
            H("""<p class="ua-formats">Required: loan amount, annual interest rate and tenure.<br>
                 Add a start date for a more useful repayment estimate.</p>
                 <div class="ua-or">Or explore before you upload</div>""")
            st.button("Explore a sample dashboard  →", on_click=_load_sample, key="az_sample", width="stretch")

        with st.expander("File format & Excel template"):
            st.caption("One row per loan. PDF statements and scanned documents are not supported.")
            st.dataframe(TEMPLATE_GUIDE, hide_index=True, width="stretch")
            st.download_button("Download Excel template", template_bytes(), file_name="loan_template.xlsx",
                               key="az_template", width="stretch")
        H(f"""<div class="ua-private-note">{svg(I['shield'], 14)}<span>No bank sign-in needed. Remove account numbers
              and personal identifiers before uploading.</span></div>""")


def _benefits():
    section("From numbers to next steps.", "ONE CONNECTED WORKSPACE")
    items = [("wallet", "Know what you owe", "Your outstanding balance, monthly commitments and repayment progress, together."),
             ("trend", "See the cost of interest", "Separate principal from interest and understand your projected repayment journey."),
             ("spark", "Explore your next move", "Take any loan into the calculator to compare amounts, interest rates and tenures.")]
    H("<div class='ua-benefits'>" + "".join(
        f"<article class='ua-benefit'><div class='ua-benefit-top'>{svg(I[ic], 22)}<span>0{i + 1}</span></div>"
        f"<h3>{t}</h3><p>{d}</p></article>" for i, (ic, t, d) in enumerate(items)) + "</div>")


def _progress_screen(ph):
    stages = ["Reading loan data", "Identifying repayment history", "Calculating loan metrics", "Preparing your insights"]
    for k in range(len(stages) + 1):
        rows = "".join(f"<div class='ua-stage {'done' if j < k else ('now' if j == k else '')}'><span class='dot'>"
                       f"{svg(I['check'], 12) if j < k else ''}</span>{s}</div>" for j, s in enumerate(stages))
        with ph.container():
            H(f"""<div class="ua-progress"><h4>Analyzing your loan</h4><div class="sub">Processing your repayment data…</div>
                  {rows}<div class="ua-pbar"><i style="width:{k / len(stages) * 100:.0f}%"></i></div></div>""")
        time.sleep(.35)
    ph.empty()


# ================================================================ dashboard
def _heading(a: pd.DataFrame, s: dict):
    c1, c2 = st.columns([3, 1], vertical_alignment="top")
    with c1:
        demo = "<span class='ua-badge demo'>Sample data</span> " if st.session_state.get("az_is_sample") else ""
        stat = (f"<span class='ua-badge'>{s['active']} active</span>" if s["active"] else "") + \
               (f"<span class='ua-badge closed'>{s['closed']} closed</span>" if s["closed"] else "")
        H(f"""<div class="ua-page-heading"><div class="ua-eyebrow">Portfolio / Loan analyzer</div>
              <h1>Your loan overview.</h1>
              <p>{demo}{st.session_state.az_source} · As of {date.today():%d %b %Y}</p>
              <div class="ua-statuses">{stat}</div></div>""")
    with c2.container(key="az_head_actions"):
        st.button("Upload another file", on_click=_new_file, key="az_new", width="stretch")
        st.download_button("Export full analysis ↓", a.to_csv(index=False), file_name="loan_analysis.csv",
                           key="az_dl", width="stretch")


def _metrics(s: dict):
    out_pct = s["outstanding"] / s["borrowed"] * 100 if s["borrowed"] else 0
    debt_free = f"{s['debt_free']:%b %Y}" if s["debt_free"] else "Debt-free"
    left = f"{months_txt(s['remaining_months'])} remaining" if s["remaining_months"] else "All loans repaid"
    cards = [
        ("featured", "Outstanding balance", "wallet", f"<small>AED</small>{num(s['outstanding'])}", f"{out_pct:.1f}% of original principal"),
        ("", "Monthly commitments", "calc", f"<small>AED</small>{num(s['monthly_emi'])}", f"Across {s['active']} active loan{'s' if s['active'] != 1 else ''}"),
        ("", "Interest remaining", "trend", f"<small>AED</small>{num(s['interest_remaining'])}", "Projected at your current EMI"),
        ("date", "Debt-free target", "clock", debt_free, left),
    ]
    H("<div class='ua-metrics'>" + "".join(
        f"<div class='ua-metric {c}'><div class='top'><span class='label'>{l}</span>{svg(I[ic], 20)}</div>"
        f"<div class='value'>{v}</div><div class='sub'>{sub}</div></div>" for c, l, ic, v, sub in cards) + "</div>")


def _path_to_debt_free(a: pd.DataFrame, s: dict):
    with st.container(key="card_outlook"):
        H("<div class='panel-title'>Your path to debt-free</div>"
          "<div class='panel-sub'>Projected outstanding principal, at your current repayment pace.</div>")
        proj = balance_projection(a, date.today())
        if proj.empty:
            st.success("Nothing outstanding. All loans are fully repaid.")
            return
        if st.session_state.get("az_projection_view") is None:
            st.session_state.az_projection_view = "Combined"
        st.segmented_control("View", ["Combined", "By loan"], key="az_projection_view", label_visibility="collapsed")
        fig = go.Figure()
        if st.session_state.az_projection_view == "By loan":
            for i, (loan, g) in enumerate(proj.groupby("Loan", sort=False)):
                c = SERIES[i % len(SERIES)]
                fig.add_scatter(x=g["Date"], y=g["Outstanding"], name=str(loan), stackgroup="one", mode="lines",
                                line=dict(width=1, color=c), fillcolor=_rgba(c, .55),
                                hovertemplate="AED %{y:,.0f}<extra>" + str(loan) + "</extra>")
            chart_theme(fig, 290, showlegend=True)
        else:
            tot = proj.groupby("Date", as_index=False)["Outstanding"].sum()
            fig.add_scatter(x=tot["Date"], y=tot["Outstanding"], name="Outstanding", mode="lines", fill="tozeroy",
                            line=dict(color=TEAL, width=2.6), fillcolor="rgba(35,122,104,.09)",
                            hovertemplate="AED %{y:,.0f}<extra></extra>")
            chart_theme(fig, 290, showlegend=False)
        fig.update_xaxes(tickformat="%Y", nticks=6)
        fig.update_yaxes(tickprefix="AED ", tickformat="~s", rangemode="tozero")
        st.plotly_chart(fig, width="stretch", key="az_outlook_chart", config=PLOT_CFG)
        H(f"""<div class="ua-chart-foot">{svg(I['clock'], 15)}Estimated final payment: <b>{s['debt_free']:%B %Y}</b>.
              Rates and repayments held constant.</div>""")
        yearly = (proj.assign(Year=pd.to_datetime(proj["Date"]).dt.year)
                  .groupby(["Year", "Loan"])["Outstanding"].last().unstack(fill_value=0))
        yearly["Total"] = yearly.sum(axis=1)
        with st.expander("View year-end balances"):
            st.dataframe(yearly.round(0), width="stretch",
                         column_config={c: st.column_config.NumberColumn(f"{c} (AED)", format="localized") for c in yearly})


def _snapshot(a: pd.DataFrame, s: dict):
    with st.container(key="card_progress"):
        H(f"""<div class='panel-title'>Repayment snapshot</div>
              <div class='panel-sub'>Original principal repaid across your portfolio.</div>
              <div class="ua-ring-wrap"><div class="ua-ring" style="--progress:{s['progress']:.4f}" role="img"
                aria-label="{s['progress']:.1f} percent of principal repaid"><div class="inner">
                <strong>{s['progress']:.1f}%</strong><small>principal repaid</small></div></div></div>
              <div class="ua-dl">
                <div class="row"><span class="k">Original borrowing</span><span class="v">{aed(s['borrowed'])}</span></div>
                <div class="row"><span class="k">Principal repaid</span><span class="v">{aed(s['repaid'])}</span></div>
                <div class="row"><span class="k">Interest paid · estimated</span><span class="v">{aed(s['interest_paid'])}</span></div>
                <div class="row"><span class="k">Weighted active rate</span><span class="v">{s['weighted_rate']:.2f}% p.a.</span></div>
              </div>""")
        with st.expander("Income & monthly commitments"):
            sal = st.number_input("Monthly income (AED)", min_value=0, step=1000, key="az_salary")
            if sal and s["active"]:
                dbr = s["monthly_emi"] / sal * 100
                st.markdown(f"Your EMIs use **{dbr:.0f}%** of your monthly income "
                            + ("(within the UAE Central Bank's 50% limit)." if dbr <= 50 else "(above the UAE Central Bank's 50% limit)."))
            st.caption("Excludes other debts, credit cards, living costs and lender-specific eligibility rules.")


def _insights(a: pd.DataFrame):
    section("What the numbers are telling you", "Calculated from your loan data")
    cards = key_insights(a, st.session_state.get("az_salary") or None)
    first = ["Opportunity", "Interest impact", "Repayment progress"]
    top = [c for t in first for c in cards if c["title"] == t]
    top += [c for c in cards if c not in top][:3 - len(top)]
    rest = [c for c in cards if c not in top]
    icon = {"Opportunity": "spark"}

    def card(c):
        cls = "opportunity" if c["title"] == "Opportunity" else ""
        return (f"<article class='ua-insight {cls}'><div class='top'>{svg(I[icon.get(c['title'], 'trend')], 19)}"
                f"<h3>{c['title'].capitalize() if c['title'].isupper() else c['title']}</h3></div><p>{bold(c['text'])}</p></article>")

    H("<div class='ua-insights'>" + "".join(card(c) for c in top) + "</div>"
      "<p class='ua-insight-note'>Model estimates only. Savings exclude prepayment fees and assume unchanged interest rates.</p>")
    if rest:
        with st.expander("More portfolio insights"):
            H("<div class='ua-more-insights'>" + "".join(card(c) for c in rest) + "</div>")


def _breakdown(a: pd.DataFrame):
    H("<div class='panel-title'>Every loan, at a glance.</div>"
      "<div class='panel-sub'>Select column headers to sort. Export above includes all analysis fields.</div>")
    view = pd.DataFrame({
        "Loan": a["Loan_ID"].astype(str), "Product": a["Loan_Type"], "Lender": a["Bank"], "Status": a["Status"],
        "Outstanding (AED)": a["Outstanding_Principal"].round(0), "Monthly EMI (AED)": a["EMI"].round(0),
        "Rate": a["Interest_Rate"], "Repaid": a["Progress_Pct"].round(0), "Target": a["Payoff_Date"],
    })
    N = st.column_config.NumberColumn
    st.dataframe(view, hide_index=True, width="stretch", column_config={
        "Outstanding (AED)": N(format="localized"), "Monthly EMI (AED)": N(format="localized"),
        "Rate": N(format="%.2f%%"), "Repaid": N(format="%.0f%%"),
        "Target": st.column_config.DateColumn(format="MMM YYYY")})
    with st.expander("Full loan details & analysis assumptions"):
        st.dataframe(a, hide_index=True, width="stretch")
        st.caption("Reducing-balance calculations. Past interest uses the original repayment schedule. A supplied "
                   "outstanding balance overrides the estimated balance; missing start dates are treated as today.")
        st.caption("A lender's transaction history, fees, changing rates, payment holidays or missed instalments may "
                   "produce different figures.")


def _flows(a: pd.DataFrame):
    with st.container(key="card_flows"):
        H("<div class='panel-title'>Where your repayments go</div>"
          "<div class='panel-sub'>Principal and interest by year. Solid bars show scheduled history; lighter bars show projections.</div>")
        y = yearly_flows(a, date.today())
        if y.empty:
            st.info("No repayment history to show yet.")
            return
        fig = go.Figure()
        for kind, op in (("Paid", 1.0), ("Projected", .45)):
            d = y[y["Kind"] == kind]
            if d.empty:
                continue
            fig.add_bar(x=d["Year"], y=d["Principal"], name=f"Principal · {kind.lower()}", marker=dict(color=TEAL, opacity=op),
                        hovertemplate="AED %{y:,.0f}<extra>Principal · " + kind.lower() + "</extra>")
            fig.add_bar(x=d["Year"], y=d["Interest"], name=f"Interest · {kind.lower()}", marker=dict(color=GOLD, opacity=op),
                        hovertemplate="AED %{y:,.0f}<extra>Interest · " + kind.lower() + "</extra>")
        chart_theme(fig, 340, barmode="relative")
        fig.update_xaxes(tickformat="d", nticks=10)
        fig.update_yaxes(tickprefix="AED ", tickformat="~s")
        st.plotly_chart(fig, width="stretch", key="az_flows_chart", config=PLOT_CFG)


def _focus(a: pd.DataFrame) -> str:
    ids = list(a["Loan_ID"])
    if st.session_state.get("az_loan_sel") not in ids:
        st.session_state.az_loan_sel = next(iter(a.loc[a["Status"] != "Closed", "Loan_ID"]), ids[0])
    idx = a.set_index("Loan_ID")
    with st.container(key="card_focus"):
        H("<div class='panel-title'>Look closer at one loan</div>"
          "<div class='panel-sub'>Original monthly schedule. Use the scenario planner for today's remaining balance.</div>")
        c1, c2 = st.columns([1, 2.1], gap="large")
        with c1:
            sel = st.selectbox("Choose a loan", ids, key="az_loan_sel",
                               format_func=lambda i: f"{i} · {idx.loc[i, 'Loan_Type']}")
            L = idx.loc[sel]
            H("<div class='ua-dl'>" + "".join(
                f"<div class='row'><span class='k'>{k}</span><span class='v'>{v}</span></div>" for k, v in [
                    ("Lender", L["Bank"]), ("Status", L["Status"]), ("Monthly EMI", aed(L["EMI"])),
                    ("Outstanding", aed(L["Outstanding_Principal"])),
                    ("Remaining", months_txt(L["Remaining_Months"]) if L["Remaining_Months"] else "—"),
                    ("Balance source", L["Outstanding_Source"])]) + "</div>")
        with c2:
            sched = amortization_schedule(L["Loan_Amount"], L["Interest_Rate"], int(L["Tenure_Months"]))
            fig = go.Figure()
            fig.add_bar(x=sched["Month"], y=sched["Principal Paid (AED)"], name="Principal", marker=dict(color=TEAL, line_width=0))
            fig.add_bar(x=sched["Month"], y=sched["Interest Paid (AED)"], name="Interest", marker=dict(color=GOLD, line_width=0))
            chart_theme(fig, 290, barmode="stack", bargap=.12 if len(sched) <= 72 else 0)
            fig.update_xaxes(title="Instalment · original schedule")
            fig.update_yaxes(tickprefix="AED ", tickformat="~s")
            if 0 < L["EMIs_Paid"] < L["Tenure_Months"]:
                fig.add_vline(x=L["EMIs_Paid"] + .5, line=dict(color=NAVY, width=1.5, dash="dot"))
                fig.add_annotation(x=L["EMIs_Paid"] + .5, y=1, yref="paper", text="Today", showarrow=False,
                                   font=dict(size=11, color=NAVY), yanchor="bottom", xanchor="left", xshift=4)
            st.plotly_chart(fig, width="stretch", key="az_focus_chart", config=PLOT_CFG)
    return sel


def _cta(a: pd.DataFrame, sel: str):
    L = a.set_index("Loan_ID").loc[sel]
    closed = L["Status"] == "Closed"
    mode_key, card_key = f"az_mode_{sel}", f"az_card_{sel}"
    _init(mode_key, "original" if closed else "remaining")
    _init(card_key, L["Calculator_Card"] or "Personal Loan")
    with st.container(key="az_cta"):
        c1, c2 = st.columns([1.25, 1], gap="large", vertical_alignment="center")
        with c1:
            H(f"""<div class="ua-eyebrow">Your next move</div><h3>Make the numbers work for you.</h3>
                  <p>Explore a different repayment scenario for <strong style="color:#fff">{sel}</strong>. Your loan amount,
                  rate and tenure will be carried into the calculator.</p>""")
        with c2:
            r1, r2 = st.columns(2)
            r1.radio("Start with", ["remaining", "original"], key=mode_key, disabled=closed,
                     format_func=lambda m: "Remaining balance" if m == "remaining" else "Original terms")
            r2.selectbox("Loan product", list(LOAN_TYPES), key=card_key,
                         help=None if L["Calculator_Card"] else "Loan type not recognised. Pick the closest.")
            st.button("Explore this scenario  →", type="primary", key="az_send", width="stretch",
                      on_click=_send_to_calculator, args=(sel, st.session_state[card_key], st.session_state[mode_key]))


# ================================================================ page
def render():
    res = st.session_state.get("az_data")
    analyzed = st.session_state.get("az_analyzed") and res is not None and not res.data.empty

    if not analyzed:
        st.session_state.az_analyzed = False
        with st.container(key="landing_row"):
            c1, c2 = st.columns([1.05, 1], gap="medium")
            with c1:
                _hero()
            with c2:
                _upload_card()
        _benefits()
        footer()
        return

    ph = st.empty()
    animate = st.session_state.pop("az_animate", False)
    if animate:
        _progress_screen(ph)
    a = analyze_loans(res.data, date.today())
    st.session_state.az_result = a
    s = portfolio_summary(a)

    _heading(a, s)
    _metrics(s)
    with st.container(key="dashboard_pair"):
        c1, c2 = st.columns([1.55, 1], gap="medium")
        with c1:
            _path_to_debt_free(a, s)
        with c2:
            _snapshot(a, s)
    _insights(a)
    section("The detail behind your dashboard.")
    t1, t2, t3 = st.tabs(["Loan breakdown", "Repayment analysis", "Scenario planner"])
    with t1:
        _breakdown(a)
    with t2:
        _flows(a)
    with t3:
        sel = _focus(a)
        _cta(a, sel)
    footer()
    if animate:
        st.session_state.run_countup = True
