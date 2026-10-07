"""Loan Analyzer module (default / home) - premium banking UI.

Business logic lives in analyzer.py and core.py; this file is presentation only.
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
from .core import LOAN_TYPES, amortization_schedule

CALC = "Loan EMI Calculator"
NAVY, TEAL, GOLD, SLATE, MIST, LINE = "#0B1F3A", "#0E7C66", "#A8823F", "#5B6B7F", "#8A97A8", "#E3E7ED"
SERIES = ["#0B1F3A", "#0E7C66", "#A8823F", "#4A6A8A", "#7FA99B", "#9AA7B6", "#5C4B7A", "#B4A27A"]


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
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)


def months_txt(m: int) -> str:
    y, r = divmod(int(m), 12)
    if y and r:
        return f"{y} yr {r} mo"
    return f"{y} yr" if y else f"{r} mo"


def _init(key, default):
    if key not in st.session_state:
        st.session_state[key] = default


def chart_theme(fig: go.Figure, h: int = 320, **kw) -> go.Figure:
    base = dict(
        height=h, margin=dict(t=36, b=8, l=8, r=8), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color=SLATE, size=12), separators=".,",
        legend=dict(orientation="h", x=0, y=1.13, font=dict(size=12, color=SLATE), bgcolor="rgba(0,0,0,0)",
                    traceorder="normal"),
        hoverlabel=dict(bgcolor="#FFFFFF", bordercolor=LINE, font=dict(family="Inter", color=NAVY, size=12)),
        bargap=.28)
    base.update(kw)
    fig.update_layout(**base)
    fig.update_xaxes(showgrid=False, linecolor=LINE, tickcolor=LINE, ticks="outside", ticklen=4, zeroline=False)
    fig.update_yaxes(gridcolor="#EEF1F5", zeroline=False, linecolor="rgba(0,0,0,0)")
    return fig


PLOT_CFG = {"displayModeBar": False, "responsive": True}


def _rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{alpha})"

# ================================================================ icons (monoline, restrained)
def _svg(path: str, size=26, color=NAVY, sw=1.6) -> str:
    return (f"<svg width='{size}' height='{size}' viewBox='0 0 24 24' fill='none' stroke='{color}' "
            f"stroke-width='{sw}' stroke-linecap='round' stroke-linejoin='round'>{path}</svg>")


I_DOC = "<path d='M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z'/><path d='M14 3v5h5'/><path d='M9 13h6M9 17h6M9 9h2'/>"
I_UPLOAD = "<path d='M12 16V4'/><path d='m7 9 5-5 5 5'/><path d='M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3'/>"
I_ANALYZE = "<path d='M4 19V5'/><path d='M4 19h16'/><path d='M8 15l3-4 3 2 4-6'/>"
I_INSIGHT = "<circle cx='12' cy='12' r='8'/><path d='M12 8v4l2.5 2.5'/>"
I_CALC = "<rect x='5' y='3' width='14' height='18' rx='2'/><path d='M8 7h8M8 11h2M12 11h2M16 11h0M8 15h2M12 15h2M8 18h2M12 18h4'/>"
I_LOCK = "<rect x='5' y='11' width='14' height='9' rx='2'/><path d='M8 11V8a4 4 0 0 1 8 0v3'/>"
I_SHIELD = "<path d='M12 3 5 6v5c0 4.5 3 8 7 10 4-2 7-5.5 7-10V6z'/><path d='m9 12 2 2 4-4'/>"
I_SPARK = "<path d='M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M6 18l2.5-2.5M15.5 8.5 18 6'/>"
I_CHECK = "<path d='m5 12 4.5 4.5L19 7'/>"
I_ALERT = "<circle cx='12' cy='12' r='9'/><path d='M12 7v6M12 16.5v.01'/>"

SLIDES = [
    ("01", "Upload", I_UPLOAD, "Upload your loan data", "Provide your Excel loan statement or repayment data. One row per loan."),
    ("02", "Analyze", I_ANALYZE, "We organize the numbers",
     "Your loan data is processed to identify key repayment and interest metrics."),
    ("03", "Understand", I_INSIGHT, "See the bigger picture",
     "Review your outstanding balance, interest, repayment progress and other insights."),
    ("04", "Explore", I_CALC, "Want to explore scenarios?",
     "Take your loan details into the EMI Calculator and compare different repayment scenarios."),
]


# ================================================================ callbacks
def go_calculator():
    st.session_state.module = CALC


def _slide(step: int):
    st.session_state.howto_idx = (st.session_state.howto_idx + step) % len(SLIDES)


def show_howto():
    st.session_state.howto_hidden = False
    st.session_state.howto_force = True       # also show it on top of an analyzed dashboard
    st.session_state.howto_idx = 0
    st.session_state.scroll_to = "card_howto"


def _hide_howto():
    st.session_state.howto_hidden = True
    st.session_state.howto_force = False


def _scroll_upload():
    st.session_state.scroll_to = "card_upload"


def _load_sample():
    st.session_state.az_data = clean_loans(sample_loans())
    st.session_state.az_source = "sample_loans.xlsx"
    st.session_state.az_error = None


def _analyze():
    st.session_state.az_analyzed = True
    st.session_state.az_animate = True
    st.session_state.scroll_to = "top"


def _new_file():
    for k in ("az_data", "az_source", "az_analyzed", "az_error", "az_file_id", "az_result"):
        st.session_state.pop(k, None)
    st.session_state.az_upload_n = st.session_state.get("az_upload_n", 0) + 1
    st.session_state.scroll_to = "card_upload"


def _send_to_calculator(loan_id: str, card: str, mode: str):
    a = st.session_state.get("az_result")
    if a is None or loan_id not in set(a["Loan_ID"]):
        return
    loan = a.set_index("Loan_ID").loc[loan_id]
    values, notes = build_prefill(loan, card, mode)
    st.session_state.pop(f"{card}_ten", None)
    st.session_state.update(values)
    what = "remaining balance" if mode == "remaining" else "original terms"
    st.session_state.calc_prefill_info = {"card": card, "label": f"{loan_id} ({what})", "notes": notes}
    st.session_state.module = CALC


# ================================================================ pre-analysis screens
def _hero():
    with st.container(key="az_hero"):
        c1, c2 = st.columns([1.7, 1], gap="large", vertical_alignment="center")
        with c1:
            H("""<div class="hero-copy"><div class="eyebrow">Loan Analyzer</div>
                 <h1>Understand your loan in minutes</h1>
                 <p>Upload your loan statement or Excel file and get a clear view of your repayment, interest,
                 outstanding balance and key loan insights.</p></div>""")
            st.write("")
            with st.container(key="hero_btns"):
                b1, b2 = st.columns(2)
            b1.button("Upload Excel", type="primary", on_click=_scroll_upload, key="hero_upload", width="stretch")
            b2.button("See how it works", on_click=show_howto, key="hero_howto", width="stretch")
        with c2:
            H(f"""<div class="trust">
                <div class="t">{_svg(I_LOCK, 20, '#9FD6C8')}<div><b>Private by design</b>Your file is processed in this session only and is never stored.</div></div>
                <div class="t">{_svg(I_SHIELD, 20, '#9FD6C8')}<div><b>UAE Central Bank context</b>Debt-burden checks against the 50% guideline.</div></div>
                <div class="t">{_svg(I_SPARK, 20, '#9FD6C8')}<div><b>Clear, actionable insights</b>Progress, interest impact and payoff milestones.</div></div>
              </div>""")


def _upload_card():
    _init("az_upload_n", 0)
    with st.container(key="card_upload"):
        H(f"""<div class="upload-head"><div class="doc">{_svg(I_DOC, 22, TEAL)}</div>
              <div><div class="panel-title">Analyze your loan</div>
              <div class="panel-sub" style="margin:0">Upload your Excel file to get started.</div></div></div>""")

        res = st.session_state.get("az_data")
        err = st.session_state.get("az_error")
        has_valid = res is not None and not res.data.empty

        if not has_valid or err:
            up = st.file_uploader("Loan file", type=["xlsx", "xls", "csv"], label_visibility="collapsed",
                                  key=f"az_upload_{st.session_state.az_upload_n}")
            if up is not None and up.file_id != st.session_state.get("az_file_id"):
                st.session_state.az_file_id = up.file_id
                with st.spinner("Reading your file…"):
                    try:
                        st.session_state.az_data = clean_loans(read_file(up.getvalue(), up.name))
                        st.session_state.az_source = up.name
                        st.session_state.az_error = None
                    except Exception:
                        st.session_state.az_data = None
                        st.session_state.az_error = "read"
                st.rerun()

        res = st.session_state.get("az_data")
        err = st.session_state.get("az_error")
        if err == "read":
            H(f"""<div class="alert err">{_svg(I_ALERT, 22, '#B42318')}<div><div class="t">We couldn't read this file</div>
                  <div class="d">Please upload a valid <code>.xlsx</code>, <code>.xls</code> or <code>.csv</code> file.</div></div></div>""")
            st.write("")
            st.button("Choose another file", on_click=_new_file, key="az_retry_read")
        elif res is not None and res.data.empty:
            items = "".join(f"<li>{m}</li>" for m in res.missing) or "<li>No rows with a valid amount, rate and tenure</li>"
            H(f"""<div class="alert err">{_svg(I_ALERT, 22, '#B42318')}<div><div class="t">Some information is missing</div>
                  <div class="d">We found the file, but some required loan information could not be identified:
                  <ul>{items}</ul>Column names are matched flexibly (e.g. <i>Amount</i>, <i>Rate</i>, <i>Tenure</i>).
                  The template shows the expected format.</div></div></div>""")
            st.write("")
            c1, c2 = st.columns(2)
            c1.button("Choose another file", on_click=_new_file, key="az_retry_missing", width="stretch")
            c2.download_button("Download template", template_bytes(), file_name="loan_template.xlsx",
                               key="az_tpl_err", width="stretch")
        elif res is not None:
            n = len(res.data)
            H(f"""<div class="file-ok"><div class="ic">{_svg(I_DOC, 20, TEAL)}</div><div>
                  <div class="fn">{st.session_state.az_source}</div>
                  <div class="meta"><span class="okc">✓ File uploaded successfully</span>
                  <span><b>{n:,}</b> loan record{'s' if n != 1 else ''} detected</span><span>Ready to analyze</span></div>
                  </div></div>""")
            notes = [i for i in res.issues if not i.startswith("Missing")]
            if notes:
                H("<div class='alert warn' style='margin-top:.7rem'><div><div class='t'>Please note</div><div class='d'>"
                  + "<br>".join(notes) + "</div></div></div>")
            st.write("")
            c1, c2 = st.columns([1.3, 1])
            c1.button("Analyze Loan  →", type="primary", on_click=_analyze, key="az_analyze", width="stretch")
            c2.button("Choose another file", on_click=_new_file, key="az_replace", width="stretch")
        else:
            H("""<div class="formats">Required in your file: loan amount, interest rate and tenure.
                 A start date gives the most accurate results.</div>""")
            st.write("")
            c1, c2 = st.columns(2)
            c1.button("Try with sample data", on_click=_load_sample, key="az_sample", width="stretch")
            c2.download_button("Download Excel template", template_bytes(), file_name="loan_template.xlsx",
                               key="az_template", width="stretch")

        with st.expander("What should my file contain?"):
            st.dataframe(TEMPLATE_GUIDE, hide_index=True, width="stretch")


def _how_it_works():
    _init("howto_idx", 0)
    i = st.session_state.howto_idx
    no, short_lbl, icon, title, text = SLIDES[i]
    with st.container(key="card_howto"):
        bars = "".join(f"<i class='{'on' if j == i else ('done' if j < i else '')}'></i>" for j in range(len(SLIDES)))
        H(f"""<div class="howto-top"><span class="lbl">How it works</span><span class="lbl">{no} / 04</span></div>
              <div class="bars">{bars}</div>
              <div class="slide" key="{i}"><div class="ico">{_svg(icon, 26, NAVY)}</div>
              <div><div class="no">{no} — {short_lbl.upper()}</div><div class="st">{title}</div>
              <div class="sx">{text}</div></div></div>""")
        if i == len(SLIDES) - 1:
            st.button("Open EMI Calculator  →", type="primary", on_click=go_calculator, key="howto_cta", width="stretch")
        c1, c2, c3 = st.columns([1, 1, 1])
        c1.button("‹  Previous", on_click=_slide, args=(-1,), disabled=i == 0, key="howto_prev", width="stretch")
        c2.button("Skip", on_click=_hide_howto, key="howto_skip", type="tertiary", width="stretch")
        c3.button("Next  ›" if i < len(SLIDES) - 1 else "Start again", on_click=_slide, args=(1,),
                  key="howto_next", width="stretch")


def _progress_screen(ph):
    stages = ["Reading loan data", "Identifying repayment history", "Calculating loan metrics", "Preparing your insights"]
    for k in range(len(stages) + 1):
        rows = "".join(
            f"<div class='stage {'done' if j < k else ('now' if j == k else '')}'><span class='dot'>"
            f"{_svg(I_CHECK, 12, '#fff', 2.4) if j < k else ''}</span>{s}</div>" for j, s in enumerate(stages))
        with ph.container():
            H(f"""<div class="progress-card"><h4>Analyzing your loan</h4><div class="sub">Processing your repayment data…</div>
                  {rows}<div class="pbar"><i style="width:{k / len(stages) * 100:.0f}%"></i></div></div>""")
        time.sleep(.38)
    ph.empty()


# ================================================================ dashboard
def _context_bar(n: int):
    with st.container(key="card_context"):
        c1, c2, c3 = st.columns([2.4, 1.2, .9], vertical_alignment="center")
        c1.markdown(f"""<div class="ctx"><span class="file">{_svg(I_DOC, 16, TEAL)} {st.session_state.az_source}</span>
            <span class="sep"></span><span>{n} loan record{'s' if n != 1 else ''}</span><span class="sep"></span>
            <span>Figures as of {date.today():%d %b %Y}</span><span class="badge ok">Analyzed</span></div>""",
                    unsafe_allow_html=True)
        c2.number_input("Monthly salary (AED) · optional", min_value=0, step=1000, key="az_salary",
                        help="Used only to check your debt-burden ratio against the UAE Central Bank's 50% limit.")
        c3.button("Upload new file", on_click=_new_file, key="az_new", width="stretch")


def _overview(a: pd.DataFrame, s: dict):
    single = s["loans"] == 1
    L0 = a.iloc[0]
    rate_lbl = "Interest rate" if single else "Avg. interest rate"
    rate_sub = "per annum" if single else "weighted by balance"
    tenure_sub = (f"ends {s['debt_free']:%b %Y}" if s["debt_free"] else "fully repaid")
    status = (f"<span class='badge ok'>{s['active']} active</span> " if s["active"] else "") + \
             (f"<span class='badge muted'>{s['closed']} closed</span>" if s["closed"] else "")
    with st.container(key="card_overview"):
        H(f"""<div class="ov-head"><div><div class="eyebrow">Portfolio</div><h2>Loan Overview</h2></div>
              <div>{status}</div></div>
              <div class="hero-metrics">
                <div class="hero-metric"><div class="l">Original loan amount</div>
                  <div class="v"><span class="cur">AED</span>{num(s['borrowed'])}</div>
                  <div class="s">{'1 loan' if single else f"{s['loans']} loans"}{'' if single else ' combined'}</div></div>
                <div class="hero-metric key"><div class="l">Outstanding balance</div>
                  <div class="v"><span class="cur">AED</span>{num(s['outstanding'])}</div>
                  <div class="s">{s['outstanding'] / s['borrowed'] * 100 if s['borrowed'] else 0:.0f}% of original principal</div></div>
                <div class="hero-metric"><div class="l">Monthly EMI</div>
                  <div class="v"><span class="cur">AED</span>{num(s['monthly_emi'])}</div>
                  <div class="s">{'across active loans' if not single else ('current instalment' if s['active'] else 'loan closed')}</div></div>
              </div>
              <div class="sec-metrics">
                <div class="metric"><div class="l">{rate_lbl}</div><div class="v">{num(s['weighted_rate'] if s['active'] else L0['Interest_Rate'], 2, '%')}</div><div class="s">{rate_sub}</div></div>
                <div class="metric"><div class="l">Remaining tenure</div><div class="v">{num(s['remaining_months'])} months</div><div class="s">{tenure_sub}</div></div>
                <div class="metric"><div class="l">Interest paid to date</div><div class="v">AED {num(s['interest_paid'])}</div><div class="s">estimated</div></div>
                <div class="metric"><div class="l">Total interest</div><div class="v">AED {num(s['interest_paid'] + s['interest_remaining'])}</div><div class="s">AED {s['interest_remaining']:,.0f} still to pay</div></div>
              </div>
              <div class="progress-line"><div class="top"><span>Repayment progress</span>
                <span><b>{s['progress']:.0f}%</b> repaid · AED {s['repaid']:,.0f} of AED {s['borrowed']:,.0f}</span></div>
                <div class="track"><div class="fill" style="width:{min(s['progress'], 100):.1f}%"></div></div></div>""")


def _progress_and_details(a: pd.DataFrame, s: dict):
    c1, c2 = st.columns([1.7, 1], gap="medium")
    with c1, st.container(key="card_progress"):
        H("<div class='panel-title'>Repayment Progress</div><div class='panel-sub'>Principal repaid versus remaining principal.</div>")
        if len(a) == 1:
            fig = go.Figure(go.Pie(labels=["Principal repaid", "Remaining principal"],
                                   values=[s["repaid"], s["outstanding"]], hole=.72, sort=False,
                                   marker=dict(colors=[TEAL, "#D9E0E8"], line=dict(color="#fff", width=2)),
                                   textinfo="none", hovertemplate="%{label}<br>AED %{value:,.0f}<extra></extra>"))
            chart_theme(fig, 300, showlegend=True,
                        annotations=[dict(text=f"<b style='font-size:22px;color:{NAVY}'>{s['progress']:.0f}%</b><br>repaid",
                                          showarrow=False, font=dict(size=12, color=SLATE))])
            fig.update_layout(legend=dict(orientation="h", y=-0.05, x=.5, xanchor="center"))
        else:
            cd = a[["Principal_Repaid", "Outstanding_Principal", "Loan_Type"]].values
            fig = go.Figure()
            fig.add_bar(y=a["Loan_ID"], x=a["Progress_Pct"], name="Principal repaid", orientation="h",
                        marker=dict(color=TEAL), customdata=cd, text=[f"{p:.0f}%" for p in a["Progress_Pct"]],
                        textposition="inside", insidetextanchor="start", textfont=dict(color="#fff", size=11),
                        hovertemplate="<b>%{y}</b> · %{customdata[2]}<br>Repaid: AED %{customdata[0]:,.0f}<extra></extra>")
            fig.add_bar(y=a["Loan_ID"], x=100 - a["Progress_Pct"], name="Remaining principal", orientation="h",
                        marker=dict(color="#D9E0E8"), customdata=cd,
                        hovertemplate="<b>%{y}</b> · %{customdata[2]}<br>Remaining: AED %{customdata[1]:,.0f}<extra></extra>")
            chart_theme(fig, max(220, 52 * len(a) + 70), barmode="stack")
            fig.update_xaxes(range=[0, 100.5], tickvals=[0, 25, 50, 75, 100], ticksuffix="%", showgrid=True,
                             gridcolor="#EEF1F5", ticks="")
            fig.update_yaxes(autorange="reversed", gridcolor="rgba(0,0,0,0)", tickfont=dict(color=NAVY, size=12))
        st.plotly_chart(fig, width="stretch", key="az_progress_chart", config=PLOT_CFG)
    with c2, st.container(key="card_details"):
        H("<div class='panel-title'>Loan Details</div><div class='panel-sub'>Key facts from your file.</div>")
        single = len(a) == 1
        L0 = a.iloc[0]
        rows = []
        if single:
            rows += [("Loan", f"{L0['Loan_ID']} · {L0['Loan_Type']}"), ("Lender", L0["Bank"]),
                     ("Interest rate", f"{L0['Interest_Rate']:.2f}% p.a."),
                     ("Original tenure", f"{L0['Tenure_Months']} months ({months_txt(L0['Tenure_Months'])})"),
                     ("Start date", f"{L0['Start_Date']:%d %b %Y}"), ("EMIs paid", f"{L0['EMIs_Paid']}")]
        else:
            banks = a["Bank"][a["Bank"] != "-"].nunique()
            rows += [("Loans in file", f"{s['loans']}"), ("Active / closed", f"{s['active']} / {s['closed']}"),
                     ("Lenders", f"{banks}" if banks else "—"),
                     ("Rate range", f"{a['Interest_Rate'].min():.2f}% – {a['Interest_Rate'].max():.2f}%"),
                     ("First loan started", f"{s['first_start']:%b %Y}")]
        rows.append(("Projected completion", f"{s['debt_free']:%b %Y}" if s["debt_free"] else "Completed"))
        if a["Prepayment"].sum() > 0:
            rows.append(("Prepayments recorded", aed(a["Prepayment"].sum())))
        basis = a["Outstanding_Source"].value_counts()
        rows.append(("Balance basis", "Bank statement" if basis.get("Statement", 0) == len(a)
                     else ("Estimated from schedule" if basis.get("Estimated", 0) == len(a) else "Mixed")))
        H("<div class='dl'>" + "".join(f"<div class='row'><span class='k'>{k}</span><span class='v'>{v}</span></div>"
                                       for k, v in rows) + "</div>")


def _interest_vs_principal(a: pd.DataFrame):
    y = yearly_flows(a, date.today())
    with st.container(key="card_flows"):
        H("""<div class='panel-title'>Interest vs Principal</div>
             <div class='panel-sub'>What each year's repayments cover, paid to date (solid) and projected (light).</div>""")
        if y.empty:
            st.info("No repayment history to show yet.")
            return
        fig = go.Figure()
        for kind, op in (("Paid", 1), ("Projected", .42)):
            d = y[y["Kind"] == kind]
            if d.empty:
                continue
            fig.add_bar(x=d["Year"], y=d["Principal"], name=f"Principal · {kind.lower()}", marker=dict(color=NAVY, opacity=op),
                        hovertemplate="%{x} · principal: AED %{y:,.0f}<extra>" + kind + "</extra>", legendgroup=kind)
            fig.add_bar(x=d["Year"], y=d["Interest"], name=f"Interest · {kind.lower()}", marker=dict(color=GOLD, opacity=op),
                        hovertemplate="%{x} · interest: AED %{y:,.0f}<extra>" + kind + "</extra>", legendgroup=kind)
        chart_theme(fig, 360, barmode="relative", margin=dict(t=24, b=8, l=8, r=8),
                    legend=dict(orientation="h", x=0, y=-0.14, font=dict(size=11, color=SLATE), traceorder="normal"))
        fig.update_yaxes(tickprefix="AED ", tickformat="~s")
        fig.update_xaxes(dtick=1 if y["Year"].nunique() <= 12 else 2, tickformat="d")
        fig.add_vline(x=date.today().year, line=dict(color=TEAL, width=1.5, dash="dot"))
        fig.add_annotation(x=date.today().year, y=1.0, yref="paper", text="Today", showarrow=False,
                           font=dict(size=11, color=TEAL), yanchor="bottom", xanchor="left", xshift=4)
        with st.container(key="scroll_flows"):
            st.plotly_chart(fig, width="stretch", key="az_flows_chart", config=PLOT_CFG)


def _outstanding_balance(a: pd.DataFrame):
    proj = balance_projection(a, date.today())
    with st.container(key="card_outlook"):
        H("""<div class='panel-title'>Outstanding Balance</div>
             <div class='panel-sub'>Projected decline of your remaining principal if you keep paying the current EMI.</div>""")
        if proj.empty:
            st.success("Nothing outstanding — all loans are fully repaid.")
            return
        fig = go.Figure()
        for i, (loan, g) in enumerate(proj.groupby("Loan", sort=False)):
            c = SERIES[i % len(SERIES)]
            fig.add_scatter(x=g["Date"], y=g["Outstanding"], name=loan, stackgroup="one", mode="lines",
                            line=dict(width=1, color=c), fillcolor=_rgba(c, .72),
                            hovertemplate="%{x|%b %Y}: AED %{y:,.0f}<extra>" + loan + "</extra>")
        chart_theme(fig, 330, hovermode="x unified")
        fig.update_yaxes(tickprefix="AED ", tickformat="~s")
        with st.container(key="scroll_outlook"):
            st.plotly_chart(fig, width="stretch", key="az_outlook_chart", config=PLOT_CFG)
        yearly = (proj.assign(Year=pd.to_datetime(proj["Date"]).dt.year)
                  .groupby(["Year", "Loan"])["Outstanding"].last().unstack(fill_value=0))
        yearly["Total"] = yearly.sum(axis=1)
        with st.expander("Year-end balances"):
            st.dataframe(yearly.round(0), width="stretch",
                         column_config={c: st.column_config.NumberColumn(f"{c} (AED)", format="localized") for c in yearly})


def _insights(a: pd.DataFrame, salary):
    H("<div class='h-section'><h3>Key Insights</h3><span>Based only on the data in your file</span></div>")
    cards = key_insights(a, salary or None)
    H("<div class='insights-grid'>" + "".join(
        f"<div class='insight {c['tone']}' style='animation-delay:{i * 60}ms'><div class='t'>{c['title']}</div>"
        f"<div class='x'>{bold(c['text'])}</div></div>" for i, c in enumerate(cards)) + "</div>")


def _loan_table(a: pd.DataFrame):
    H("<div class='h-section'><h3>Loan Breakdown</h3><span>Sortable · download available</span></div>")
    view = a[["Loan_ID", "Loan_Type", "Bank", "Status", "Loan_Amount", "Interest_Rate", "Tenure_Months", "Start_Date",
              "EMI", "EMIs_Paid", "Remaining_Months", "Outstanding_Principal", "Interest_Paid_To_Date",
              "Interest_Remaining", "Progress_Pct", "Payoff_Date"]]
    N = st.column_config.NumberColumn
    view = view.copy()
    money_cols = ["Loan_Amount", "EMI", "Outstanding_Principal", "Interest_Paid_To_Date", "Interest_Remaining"]
    view[money_cols] = view[money_cols].round(0)
    st.dataframe(view, hide_index=True, width="stretch", column_config={
        "Loan_ID": "Loan", "Loan_Type": "Type", "Bank": "Lender",
        "Loan_Amount": N("Original (AED)", format="localized"), "Interest_Rate": N("Rate", format="%.2f%%"),
        "Tenure_Months": N("Tenure (mo)"), "Start_Date": st.column_config.DateColumn("Start", format="DD MMM YYYY"),
        "EMI": N("EMI (AED)", format="localized"), "EMIs_Paid": N("EMIs paid"), "Remaining_Months": N("Months left"),
        "Outstanding_Principal": N("Outstanding (AED)", format="localized"),
        "Interest_Paid_To_Date": N("Interest paid (AED)", format="localized"),
        "Interest_Remaining": N("Interest left (AED)", format="localized"),
        "Progress_Pct": st.column_config.ProgressColumn("Repaid", format="%.0f%%", min_value=0, max_value=100),
        "Payoff_Date": st.column_config.DateColumn("Completion", format="MMM YYYY"),
    })
    st.download_button("Download analysis (CSV)", a.to_csv(index=False), file_name="loan_analysis.csv", key="az_dl")


def _loan_focus(a: pd.DataFrame) -> str:
    H("<div class='h-section'><h3>Loan Focus</h3><span>Look closer at a single loan</span></div>")
    ids = list(a["Loan_ID"])
    if st.session_state.get("az_loan_sel") not in ids:
        st.session_state.az_loan_sel = next(iter(a.loc[a["Status"] != "Closed", "Loan_ID"]), ids[0])
    idx = a.set_index("Loan_ID")
    with st.container(key="card_focus"):
        c1, c2 = st.columns([1, 2.2], gap="large")
        with c1:
            sel = st.selectbox("Loan", ids, key="az_loan_sel",
                               format_func=lambda i: f"{i} · {idx.loc[i, 'Loan_Type']}")
            L = idx.loc[sel]
            H("<div class='dl' style='margin-top:.4rem'>" + "".join(
                f"<div class='row'><span class='k'>{k}</span><span class='v'>{v}</span></div>" for k, v in [
                    ("Status", L["Status"]), ("Monthly EMI", aed(L["EMI"])),
                    ("Outstanding", aed(L["Outstanding_Principal"])),
                    ("Remaining", f"{L['Remaining_Months']} months"),
                    ("Interest left", aed(L["Interest_Remaining"])),
                    ("Completion", f"{L['Payoff_Date']:%b %Y}"),
                ]) + "</div>")
        with c2:
            sched = amortization_schedule(L["Loan_Amount"], L["Interest_Rate"], int(L["Tenure_Months"]))
            fig = go.Figure()
            fig.add_bar(x=sched["Month"], y=sched["Principal Paid (AED)"], name="Principal", marker=dict(color=NAVY),
                        hovertemplate="Month %{x}<br>Principal: AED %{y:,.0f}<extra></extra>")
            fig.add_bar(x=sched["Month"], y=sched["Interest Paid (AED)"], name="Interest", marker=dict(color=GOLD),
                        hovertemplate="Month %{x}<br>Interest: AED %{y:,.0f}<extra></extra>")
            chart_theme(fig, 320, barmode="stack", bargap=.08, margin=dict(t=24, b=8, l=8, r=8),
                        legend=dict(orientation="h", x=0, y=-0.22, font=dict(size=11, color=SLATE)))
            fig.update_yaxes(tickprefix="AED ", tickformat="~s")
            fig.update_xaxes(title=dict(text="Instalment (original schedule)", font=dict(size=11)))
            if 0 < L["EMIs_Paid"] < L["Tenure_Months"]:
                fig.add_vline(x=L["EMIs_Paid"] + .5, line=dict(color=TEAL, width=1.5, dash="dot"))
                fig.add_annotation(x=L["EMIs_Paid"] + .5, y=1, yref="paper", text="Today", showarrow=False,
                                   font=dict(size=11, color=TEAL), yanchor="bottom", bgcolor="#fff")
            with st.container(key="scroll_focus"):
                st.plotly_chart(fig, width="stretch", key="az_focus_chart", config=PLOT_CFG)
    return sel


def _cta(a: pd.DataFrame, sel: str):
    L = a.set_index("Loan_ID").loc[sel]
    closed = L["Status"] == "Closed"
    mode_key, card_key = f"az_mode_{sel}", f"az_card_{sel}"
    _init(mode_key, "original" if closed else "remaining")
    _init(card_key, L["Calculator_Card"] or "Personal Loan")
    with st.container(key="az_cta"):
        c1, c2 = st.columns([1.35, 1], gap="large", vertical_alignment="center")
        with c1:
            H(f"""<div class="cta-copy"><div class="eyebrow">Scenario planning</div><h3>Want to explore different scenarios?</h3>
                  <p>Use the details of <b style="color:#fff">{sel}</b> to see how changes in tenure, interest rate or
                  loan amount could affect your EMI and total interest. Values are pre-filled for you.</p></div>""")
        with c2:
            r1, r2 = st.columns(2)
            r1.radio("Start from", ["remaining", "original"], key=mode_key, disabled=closed,
                     format_func=lambda m: "Remaining balance" if m == "remaining" else "Original loan")
            r2.selectbox("Open as", list(LOAN_TYPES), key=card_key,
                         help=None if L["Calculator_Card"] else "Loan type not recognised — pick the closest.")
            b1, b2 = st.columns([1.5, 1])
            b1.button("Explore with EMI Calculator  →", type="primary", key="az_send", width="stretch",
                      on_click=_send_to_calculator, args=(sel, st.session_state[card_key], st.session_state[mode_key]))
            b2.button("Blank calculator", key="az_blank", on_click=go_calculator, width="stretch")


# ================================================================ page
def render():
    _init("howto_hidden", False)
    res = st.session_state.get("az_data")
    analyzed = st.session_state.get("az_analyzed") and res is not None and not res.data.empty

    if not analyzed:
        st.session_state.az_analyzed = False
        _hero()
        st.write("")
        if st.session_state.howto_hidden:
            _upload_card()
        else:
            c1, c2 = st.columns([1.45, 1], gap="medium")
            with c1:
                _upload_card()
            with c2:
                _how_it_works()
        H("<div class='foot'>Estimates use standard reducing-balance EMI calculations. Your bank statement remains the "
          "final reference.</div>")
        return

    # ---- analysis
    ph = st.empty()
    animate = st.session_state.pop("az_animate", False)
    if animate:
        _progress_screen(ph)
    a = analyze_loans(res.data, date.today())
    st.session_state.az_result = a
    s = portfolio_summary(a)

    if st.session_state.get("howto_force") and not st.session_state.howto_hidden:
        c1, _ = st.columns([1, 1.2])
        with c1:
            _how_it_works()
        st.write("")
    _context_bar(len(a))
    st.write("")
    _overview(a, s)
    st.write("")
    _progress_and_details(a, s)
    st.write("")
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        _interest_vs_principal(a)
    with c2:
        _outstanding_balance(a)
    _insights(a, st.session_state.get("az_salary"))
    _loan_table(a)
    sel = _loan_focus(a)
    _cta(a, sel)
    H("<div class='foot'>Figures are estimates based on standard reducing-balance EMI calculations and the data in your "
      "file. Your bank statement remains the final reference. Not financial advice.</div>")
    if animate:
        st.session_state.run_countup = True
