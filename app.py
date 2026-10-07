"""UAE Loan Analyzer & EMI Calculator - app shell (header, navigation, page routing)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

import streamlit as st

from emi_calculator import analyzer_page, calculator_page
from emi_calculator.analyzer import template_bytes
from emi_calculator.core import LOAN_TYPES
from emi_calculator.styles import CSS, JS_COUNTUP, JS_UPLOAD_DRAG, js_scroll

st.set_page_config(page_title="UAE Loan Analyzer & EMI Calculator", page_icon="🏦", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

ANALYZER, CALC = "Loan Analyzer", "Loan EMI Calculator"
MODULES = {ANALYZER: "Loan Analyzer", CALC: "EMI Calculator"}

# Keep each module's inputs when the user switches modules (Streamlit drops state of hidden widgets)
_KEEP_PREFIX = tuple(LOAN_TYPES) + ("az_salary", "az_loan_sel", "az_mode_", "az_card_")
for k in list(st.session_state):
    if k.startswith(_KEEP_PREFIX) and not k.endswith(("_dl", "_bar", "_pie")):
        st.session_state[k] = st.session_state[k]

# Loan Analyzer is the default module
if "module" not in st.session_state:
    st.session_state.module = ANALYZER
st.session_state.setdefault("_last_module", st.session_state.module)


def _on_nav():
    if st.session_state.module is None:  # clicking the active segment deselects it - keep current
        st.session_state.module = st.session_state._last_module


def _help():
    st.session_state.module = ANALYZER
    analyzer_page.show_howto()


# ---------------------------------------------------------------- header
with st.container(key="appbar"):
    brand, nav, actions = st.columns([1.15, 1.3, 1.05], vertical_alignment="center")
    brand.markdown("""<div class="brand"><div class="logo">AED</div>
      <div><div class="name">UAE Loan Analyzer</div><div class="tag">Understand your loan · Explore scenarios</div></div>
    </div>""", unsafe_allow_html=True)
    nav.segmented_control("Module", list(MODULES), format_func=MODULES.get, key="module",
                          on_change=_on_nav, label_visibility="collapsed")
    with actions.container(key="appbar_actions"):
        a1, a2 = st.columns([1, 1.15])
        a1.button("How it works", type="tertiary", on_click=_help, key="hdr_help", width="stretch")
        a2.download_button("Excel template", template_bytes(), file_name="loan_template.xlsx",
                           key="hdr_tpl", width="stretch")

module = st.session_state.module or st.session_state._last_module
if module != st.session_state._last_module:
    st.session_state.setdefault("scroll_to", "top")
st.session_state._last_module = module

# ---------------------------------------------------------------- page
if module == CALC:
    with st.container(key="page_calc"):
        calculator_page.render()
else:
    with st.container(key="page_az"):
        analyzer_page.render()

# ---------------------------------------------------------------- in-page scripts (st.html, no iframe)
scripts = [JS_UPLOAD_DRAG]
target = st.session_state.pop("scroll_to", None)
if target:
    scripts.append(js_scroll(target))
if st.session_state.pop("run_countup", False):
    scripts.append(JS_COUNTUP)
with st.container(key="js_runner"):
    st.html(f"<!-- {time.time_ns()} -->" + "".join(scripts), unsafe_allow_javascript=True)
