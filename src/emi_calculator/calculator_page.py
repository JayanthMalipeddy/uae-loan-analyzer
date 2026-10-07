"""Loan EMI Calculator module (existing feature).

Calculations, inputs, outputs, charts and layout are unchanged. Integration only:
  1. Widgets accept values pre-filled from the Loan Analyzer (via session state).
  2. A small banner shows which analyzed loan was loaded, with a "Reset" option.
"""
import plotly.graph_objects as go
import streamlit as st

from .core import LOAN_TYPES, amortization_schedule, calculate_emi

ICONS = {"Personal Loan": "👤", "Home Loan": "🏠", "Auto Loan": "🚗"}
ACCENTS = {"Personal Loan": "#6366F1", "Home Loan": "#0F766E", "Auto Loan": "#D97706"}
WIDGET_SUFFIXES = ("_amt", "_rate", "_def", "_ten")


def fmt(x: float) -> str:
    return f"AED {x:,.2f}"


def short(x: float) -> str:
    if x >= 1_000_000:
        return f"AED {x/1_000_000:,.2f}M"
    if x >= 1_000:
        return f"AED {x/1_000:,.1f}K"
    return f"AED {x:,.0f}"


def _v(key: str, default):
    """Pass the default only if the value is not already in session state (pre-filled or user-set)."""
    return {} if key in st.session_state else {"value": default}


def reset_calculator():
    for k in [k for k in st.session_state if k.endswith(WIDGET_SUFFIXES) and k.split("_")[0] in LOAN_TYPES]:
        del st.session_state[k]
    st.session_state.pop("calc_prefill_info", None)


# ---------------------------------------------------------------- inputs
def loan_card(key: str):
    d = LOAN_TYPES[key]
    accent = ACCENTS[key]
    st.markdown(f"""
    <div class="loan-head">
      <div class="ico" style="background:{accent}1A;">{ICONS[key]}</div>
      <div><h3>{key}</h3><small>Default tenure: {d.tenure_months} months</small></div>
    </div>""", unsafe_allow_html=True)

    amount = st.slider("Loan Amount (AED)", int(d.min_amount), int(d.max_amount),
                       step=5_000, key=f"{key}_amt", **_v(f"{key}_amt", int(d.amount)))
    rate = st.slider("Interest Rate (% p.a.)", 0.0, 20.0, step=0.01, key=f"{key}_rate",
                     **_v(f"{key}_rate", d.rate))
    use_default = st.toggle("Use UAE default tenure", key=f"{key}_def", **_v(f"{key}_def", True))
    tenure = d.tenure_months
    if not use_default:
        tenure = st.slider("Tenure (months)", 6, d.max_tenure_months,
                           step=1 if d.max_tenure_months <= 60 else 6, key=f"{key}_ten",
                           **_v(f"{key}_ten", d.tenure_months))

    emi = calculate_emi(amount, rate, tenure)
    total = emi * tenure
    st.markdown(f"""
    <div class="emi-box" style="background:linear-gradient(135deg,{accent} 0%,{accent}CC 100%);">
      <div class="lbl">Monthly EMI</div><div class="val">{fmt(emi)}</div>
    </div>
    <div class="stats">
      <div class="stat"><div class="lbl">Tenure</div><div class="val">{tenure} m</div></div>
      <div class="stat"><div class="lbl">Interest</div><div class="val">{short(total-amount)}</div></div>
      <div class="stat"><div class="lbl">Total</div><div class="val">{short(total)}</div></div>
    </div>""", unsafe_allow_html=True)
    return amount, rate, tenure, emi, total


def render():
    # ---------------------------------------------------------------- hero
    st.markdown("""
    <div class="hero">
      <div class="badge">🇦🇪 Central Bank of UAE guidelines</div>
      <h1>UAE Loan <span>EMI</span> Calculator</h1>
      <p>Explore what-if scenarios for Personal, Home and Auto loans. Adjust the amount, rate and tenure,
         then see exactly where every dirham goes, month by month.</p>
      <div class="chips">
        <div class="chip">👤 Personal · up to 48 months</div>
        <div class="chip">🚗 Auto · up to 60 months</div>
        <div class="chip">🏠 Home · up to 25 years</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # pre-fill banner (only when values came from the Loan Analyzer)
    info = st.session_state.get("calc_prefill_info")
    if info:
        b1, b2 = st.columns([5, 1], vertical_alignment="center")
        notes = "".join(f"<br><span style='opacity:.8'>• {n}</span>" for n in info["notes"])
        b1.markdown(f"<div class='prefill-banner'>📥 <b>{info['label']}</b> was loaded into the "
                    f"<b>{info['card']}</b> card. Move the sliders to explore what-if scenarios.{notes}</div>",
                    unsafe_allow_html=True)
        b2.button("↺ Reset to defaults", on_click=reset_calculator, width="stretch")

    cols = st.columns(3, gap="large")
    inputs = {}
    for col, key in zip(cols, LOAN_TYPES):
        with col:
            with st.container(border=True):
                inputs[key] = loan_card(key)

    # ---------------------------------------------------------------- schedule
    st.markdown('<div class="section-title"><div class="bar"></div><h2>Amortization Schedule</h2></div>',
                unsafe_allow_html=True)

    tab_order = list(LOAN_TYPES)
    if info:  # open the pre-filled loan's tab first
        tab_order.remove(info["card"])
        tab_order.insert(0, info["card"])
    tabs = st.tabs([f"{ICONS[k]}  {k}" for k in tab_order])
    for tab, key in zip(tabs, tab_order):
        with tab:
            amount, rate, tenure, emi, total = inputs[key]
            df = amortization_schedule(amount, rate, tenure, key)
            accent = ACCENTS[key]

            st.markdown(f"""
            <div class="summary-row">
              <div class="card"><div class="lbl">Principal</div><div class="val">{fmt(amount)}</div></div>
              <div class="card"><div class="lbl">Monthly EMI</div><div class="val" style="color:{accent}">{fmt(emi)}</div></div>
              <div class="card"><div class="lbl">Total Interest</div><div class="val">{fmt(total-amount)}</div></div>
              <div class="card"><div class="lbl">Total Payable</div><div class="val">{fmt(total)}</div></div>
            </div>""", unsafe_allow_html=True)

            with st.container(border=True):
                c1, c2 = st.columns([2.2, 1])
                with c1:
                    fig = go.Figure()
                    fig.add_bar(x=df["Month"], y=df["Principal Paid (AED)"], name="Principal",
                                marker_color=accent)
                    fig.add_bar(x=df["Month"], y=df["Interest Paid (AED)"], name="Interest",
                                marker_color="#FBBF24")
                    fig.add_scatter(x=df["Month"], y=df["Left-over Principal (AED)"],
                                    name="Left-over Principal", yaxis="y2", mode="lines",
                                    line=dict(color="#0F172A", width=2.5))
                    fig.update_layout(
                        barmode="stack", height=360, margin=dict(t=20, b=10, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter"),
                        xaxis=dict(title="Month", gridcolor="#EEF2F7"),
                        yaxis=dict(title="Monthly split (AED)", gridcolor="#EEF2F7"),
                        yaxis2=dict(title="Balance (AED)", overlaying="y", side="right", showgrid=False,
                                    rangemode="tozero"),
                        legend=dict(orientation="h", y=1.12, x=0),
                    )
                    st.plotly_chart(fig, width="stretch", key=f"{key}_bar")
                with c2:
                    donut = go.Figure(go.Pie(
                        labels=["Principal", "Interest"], values=[amount, max(total - amount, 0)],
                        hole=.68, marker=dict(colors=[accent, "#FBBF24"]), textinfo="percent",
                        sort=False))
                    donut.update_layout(
                        height=360, margin=dict(t=20, b=10, l=10, r=10), showlegend=True,
                        legend=dict(orientation="h", y=-0.05), paper_bgcolor="rgba(0,0,0,0)",
                        font=dict(family="Inter"),
                        annotations=[dict(text=f"<b>{short(total)}</b><br>Total", showarrow=False,
                                          font=dict(size=15))])
                    st.plotly_chart(donut, width="stretch", key=f"{key}_pie")

            st.dataframe(df, hide_index=True, width="stretch", height=430,
                         column_config={c: st.column_config.NumberColumn(format="%.2f")
                                        for c in df.columns if c != "Month"})
            st.download_button("⬇️  Download schedule (CSV)", df.to_csv(index=False),
                               file_name=f"{key.replace(' ', '_').lower()}_schedule.csv",
                               key=f"{key}_dl", type="primary")

    st.markdown('<div class="footer">Rates shown are indicative only. Actual EMI depends on your bank\'s '
                'offer, fees and eligibility.</div>', unsafe_allow_html=True)
