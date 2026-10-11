"""Design system + page CSS.

The visual language follows the approved design preview (uae_loan_ui_preview.html):
  Navy #142D42 (primary) · Teal #237A68 (positive) · Gold #B89658 (highlights)
  Ink #1B2B37 · Slate #677683 · Line #E4E8E7 · Canvas #F7F8F5 · Cards 18px radius
The first block is the preview's stylesheet; the second block adds the states that only
exist in the live Streamlit app (upload errors, progress screen, popover guide, etc.).
"""

CSS = """
<style>
:root {
 --navy:#142D42; --navy-deep:#102536; --teal:#237A68; --teal-soft:#EAF3EE;
 --gold:#B89658; --gold-light:#E2C68C; --gold-soft:#F6F1E7; --ink:#1B2B37;
 --slate:#677683; --mist:#83918C; --line:#E4E8E7; --canvas:#F7F8F5;
 --surface:#FFFFFF; --r:18px; --shadow:0 12px 35px -27px rgba(20,45,66,.35);
}
html, body, .stApp, input, button, select, textarea {
 font-family:Inter,"Segoe UI",Arial,sans-serif; -webkit-font-smoothing:antialiased;
}
.stApp { background:var(--canvas); color:var(--ink); }
[data-testid="stMainBlockContainer"], .block-container {
 max-width:1320px; padding:0 44px 28px !important; margin:auto;
}
[data-testid="stHeader"] { background:transparent; height:0; }
[data-testid="stToolbar"] { display:none; }
[data-testid="stMain"] { scroll-behavior:smooth; }
[data-testid="stVerticalBlock"] { gap:1rem; }
h1,h2,h3,h4,p { overflow-wrap:break-word; }
button, a, input { -webkit-tap-highlight-color:transparent; }
button:focus-visible, a:focus-visible, input:focus-visible {
 outline:3px solid #B89658 !important; outline-offset:3px;
}
.stButton button, .stDownloadButton button, .stLinkButton a {
 min-height:44px; border:1px solid var(--line); border-radius:9px;
 padding:10px 17px; font-size:13px; font-weight:600; color:var(--navy);
 background:white; box-shadow:none; transition:background .18s,border-color .18s;
}
.stButton button p, .stDownloadButton button p { font-size:13px; font-weight:600; }
.stButton button:hover, .stDownloadButton button:hover { border-color:#98AAA7; background:#F5F8F5; color:var(--navy); }
button[kind="primary"], [data-testid="stBaseButton-primary"] {
 background:var(--navy) !important; color:white !important; border-color:var(--navy) !important;
}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover { background:#23475C !important; }
button[kind="primary"] p, [data-testid="stBaseButton-primary"] p { color:inherit !important; }
button[kind="tertiary"], [data-testid="stBaseButton-tertiary"] { background:transparent !important; border-color:transparent !important; }
button:disabled { opacity:.5; cursor:not-allowed; }
[data-testid="stWidgetLabel"] p { color:var(--slate); font-size:12px; font-weight:600; }
[data-testid="stNumberInputContainer"], [data-baseweb="select"] > div,
.stTextInput input { background:#FBFCFA !important; border:1px solid var(--line) !important; border-radius:9px !important; }
[data-testid="stNumberInputContainer"] input { font-variant-numeric:tabular-nums; color:var(--navy); font-weight:600; }
[data-testid="stExpander"] { border:1px solid var(--line); border-radius:10px; background:transparent; }
[data-testid="stExpander"] summary { font-size:12px; color:var(--slate); }
.st-key-js_runner { display:none; }
/* Compact masthead: the only navigation, not a second hero. */
.st-key-appbar {
 padding:22px 0 20px; margin-bottom:26px; border-bottom:1px solid var(--line);
}
.brand { display:flex; align-items:center; gap:12px; white-space:nowrap; }
.brand .logo { width:43px; height:43px; border-radius:11px; background:var(--navy); color:var(--gold-light); display:grid; place-items:center; flex-shrink:0; }
.brand .name { font-size:17px; font-weight:700; color:var(--navy); letter-spacing:-.5px; }
.brand .tag { font-size:9px; color:var(--slate); letter-spacing:2px; text-transform:uppercase; margin-top:4px; }
.st-key-appbar_actions .stButton button, .st-key-appbar_actions .stDownloadButton button { min-height:40px; }
.st-key-module button { border:0 !important; border-radius:0 !important; border-bottom:2px solid transparent !important; background:transparent !important; box-shadow:none !important; padding:12px 15px !important; color:var(--slate) !important; }
.st-key-module button[aria-pressed="true"], .st-key-module [data-testid="stBaseButton-segmented_controlActive"] { border-bottom-color:var(--gold) !important; color:var(--navy) !important; }
/* Equal-height feature pair. Narrow screens revert to natural document flow. */
.st-key-landing_row [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
.st-key-dashboard_pair [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { height:100%; }
.st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stHtml"],
.st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stElementContainer"],
.st-key-landing_row [data-testid="stColumn"]:first-child .stElementContainer { height:100%; }
.st-key-landing_row .ua-landing-hero { height:100%; }
.st-key-dashboard_pair .st-key-card_progress, .st-key-dashboard_pair .st-key-card_outlook { height:100%; }
/* Homepage: an editorial panel paired directly with the working uploader. */
.ua-eyebrow { display:flex; align-items:center; gap:9px; text-transform:uppercase; font-size:10px; font-weight:700; letter-spacing:1.9px; color:var(--teal); margin-bottom:12px; }
.ua-eyebrow::before { content:""; width:22px; height:2px; background:currentColor; flex:none; }
.ua-landing-hero {
 position:relative; overflow:hidden; min-height:546px; box-sizing:border-box;
 padding:45px 43px 32px; border-radius:22px; background:var(--navy); color:white;
 display:flex; flex-direction:column; justify-content:space-between;
}
.ua-landing-hero::after { content:""; position:absolute; width:410px; height:410px;
 border:1px solid rgba(226,198,140,.15); border-radius:50%; right:-290px; top:-125px;
 box-shadow:0 0 0 27px rgba(226,198,140,.035),0 0 0 54px rgba(226,198,140,.035),0 0 0 81px rgba(226,198,140,.025); pointer-events:none;
}
.ua-landing-hero > * { position:relative; z-index:1; }
.ua-landing-hero .ua-eyebrow { color:var(--gold-light); margin-bottom:27px; }
.ua-landing-hero h1 { font-size:clamp(34px,3.6vw,49px); font-weight:500; letter-spacing:-2.1px; line-height:1.15; color:#FFF; margin:0 0 22px; padding:0; }
.ua-landing-hero h1 em { color:var(--gold-light); font-style:normal; }
.ua-landing-hero .ua-lead { max-width:360px; color:#BECAD2; font-size:14px; line-height:1.85; margin:0 0 24px; }
.ua-product-chips { display:flex; gap:9px; flex-wrap:wrap; }
.ua-product-chips span { display:flex; align-items:center; gap:7px; padding:8px 12px; color:#E0E7E9; border:1px solid #3C5061; border-radius:6px; font-size:11px; }
.ua-hero-bottom { margin-top:34px; padding-top:23px; border-top:1px solid #3C5061; display:flex; align-items:center; gap:17px; }
.ua-hero-bottom .ua-emblem { width:41px; height:41px; border:1px solid #5C655E; display:grid; place-items:center; color:var(--gold-light); border-radius:50%; flex:none; }
.ua-hero-bottom b { font-size:12px; font-weight:500; color:#F2F3EB; display:block; margin-bottom:5px; }
.ua-hero-bottom span { font-size:11px; color:#A9B9C4; line-height:1.6; }
[class*="st-key-card_"] { border:1px solid var(--line); background:white; border-radius:var(--r); padding:25px 27px; box-shadow:var(--shadow); }
.st-key-card_upload { padding:31px; min-height:546px; }
.ua-card-top { display:flex; align-items:center; justify-content:space-between; gap:10px; margin-bottom:19px; }
.ua-icon-tile { display:grid; place-items:center; color:var(--teal); width:43px; height:43px; border-radius:12px; background:var(--teal-soft); flex:none; }
.ua-step { font-size:9px; font-weight:700; letter-spacing:1.4px; color:var(--slate); }
.panel-title { font-size:18px; font-weight:600; color:var(--navy); line-height:1.35; letter-spacing:-.4px; }
.panel-sub { font-size:12px; color:var(--slate); line-height:1.75; margin:6px 0 15px; }
.st-key-card_upload .panel-title { font-size:27px; letter-spacing:-.9px; }
.st-key-card_upload .panel-sub { max-width:365px; }
[data-testid="stFileUploaderDropzone"] {
 border:1.5px dashed #C5D3CB; border-radius:12px; background:#F7FAF7;
 min-height:160px; padding:20px !important; display:flex; flex-direction:column;
 align-items:center; justify-content:center; gap:12px; text-align:center;
}
[data-testid="stFileUploaderDropzone"]:hover { background:#F0F6F0; border-color:var(--teal); }
[data-testid="stFileUploaderDropzoneInstructions"] { display:flex; flex-direction:column; align-items:center; gap:9px; }
[data-testid="stFileUploaderDropzoneInstructions"] > div { display:flex; flex-direction:column; align-items:center; }
[data-testid="stFileUploaderDropzoneInstructions"] span { font-size:12px; color:var(--navy); }
[data-testid="stFileUploaderDropzoneInstructions"] small { font-size:10px; color:var(--slate); }
[data-testid="stFileUploaderDropzone"] button { background:var(--navy) !important; color:white !important; border:0 !important; border-radius:7px; min-height:36px; padding:8px 17px; font-weight:500; font-size:12px; }
.ua-formats { font-size:11px; color:var(--slate); line-height:1.65; margin:0; }
.ua-or { display:flex; align-items:center; gap:10px; color:#88928F; font-size:10px; margin:1px 0; }
.ua-or::before,.ua-or::after { content:""; height:1px; background:var(--line); flex:1; }
.ua-private-note { display:flex; align-items:flex-start; gap:8px; color:var(--slate); font-size:10px; line-height:1.7; }
.ua-private-note svg { flex:none; margin-top:1px; }
.ua-file-ok { display:flex; align-items:center; gap:13px; padding:16px; background:var(--teal-soft); border:1px solid #C5DED0; border-radius:11px; color:var(--teal); }
.ua-file-ok b { display:block; color:var(--navy); font-size:13px; overflow-wrap:anywhere; }
.ua-file-ok span { font-size:11px; line-height:1.8; }
.ua-section { display:flex; align-items:baseline; justify-content:space-between; gap:20px; margin:30px 0 18px; }
.ua-section h2 { margin:0; padding:0; color:var(--navy); font-size:23px; font-weight:600; letter-spacing:-.7px; }
.ua-section > span { font-size:10px; color:var(--slate); }
.ua-benefits { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:20px; }
.ua-benefit { padding:22px 24px; border:1px solid var(--line); background:#FFFFFF; border-radius:13px; }
.ua-benefit .ua-benefit-top { display:flex; align-items:center; justify-content:space-between; color:var(--teal); margin-bottom:17px; }
.ua-benefit .ua-benefit-top span { color:#9CA6A0; font-size:10px; letter-spacing:1px; }
.ua-benefit h3 { margin:0 0 9px; padding:0; font-size:14px; font-weight:600; color:var(--navy); }
.ua-benefit p { margin:0; color:var(--slate); font-size:12px; line-height:1.85; }
.ua-guide { display:grid; grid-template-columns:repeat(3,1fr); gap:24px; }
.ua-guide b { display:block; font-size:14px; color:var(--navy); margin-bottom:8px; }
.ua-guide p { font-size:12px; line-height:1.8; color:var(--slate); margin:0; }
/* Dashboard: figures first, with a quiet supporting hierarchy. */
.ua-page-heading { margin:7px 0 8px; }
.ua-page-heading h1 { margin:0 0 10px; padding:0; font-size:34px; line-height:1.2; font-weight:500; color:var(--navy); letter-spacing:-1.2px; }
.ua-page-heading p { font-size:12px; color:var(--slate); margin:0; line-height:1.8; }
.ua-badge { display:inline-flex; align-items:center; gap:5px; border-radius:5px; background:var(--teal-soft); color:var(--teal); padding:5px 8px; font-size:10px; font-weight:600; }
.ua-badge.demo { background:var(--gold-soft); color:#7F683F; }
.ua-badge.closed { background:#EFF1EE; color:var(--slate); }
.ua-statuses { display:flex; gap:7px; margin-top:10px; }
.ua-metrics { display:grid; grid-template-columns:1.25fr 1fr 1fr 1fr; gap:16px; margin:15px 0 7px; }
.ua-metric { border:1px solid var(--line); background:white; padding:22px; border-radius:14px; min-width:0; }
.ua-metric .top { display:flex; justify-content:space-between; align-items:center; color:var(--slate); gap:8px; margin-bottom:18px; }
.ua-metric .label { font-size:10px; line-height:1.4; font-weight:500; }
.ua-metric .value { color:var(--navy); font-size:27px; font-weight:600; letter-spacing:-1.15px; font-variant-numeric:tabular-nums; line-height:1.2; }
.ua-metric .value small { font-size:11px; font-weight:500; color:var(--slate); letter-spacing:0; margin-right:5px; }
.ua-metric .sub { font-size:10px; color:var(--slate); margin-top:12px; line-height:1.5; }
.ua-metric.featured { background:var(--navy); border-color:var(--navy); }
.ua-metric.featured .top { color:#CFD8DB; }
.ua-metric.featured .top svg { color:var(--gold-light); }
.ua-metric.featured .value { color:white; }
.ua-metric.featured .value small { color:#C6D0D4; }
.ua-metric.featured .sub { color:#BAC8CF; }
.ua-metric.date .value { font-size:25px; letter-spacing:-.8px; }
.ua-dl .row { display:flex; justify-content:space-between; gap:18px; padding:12px 0; border-bottom:1px solid #EDF0EB; font-size:12px; }
.ua-dl .row:last-child { border-bottom:0; }
.ua-dl .k { color:var(--slate); }
.ua-dl .v { color:var(--navy); font-weight:600; text-align:right; font-variant-numeric:tabular-nums; overflow-wrap:anywhere; }
.ua-chart-foot { display:flex; align-items:center; gap:8px; background:#F5F8F3; border-radius:7px; padding:9px 12px; font-size:10px; color:var(--teal); line-height:1.6; }
.ua-ring-wrap { display:flex; align-items:center; justify-content:center; padding:6px 0 10px; }
.ua-ring { width:160px; height:160px; border-radius:50%; background:conic-gradient(var(--teal) calc(var(--progress) * 1%),#E9EEEA 0); display:grid; place-items:center; }
.ua-ring .inner { width:130px; height:130px; background:white; border-radius:50%; display:flex; align-items:center; justify-content:center; flex-direction:column; }
.ua-ring strong { font-weight:500; font-size:33px; letter-spacing:-1.1px; color:var(--navy); }
.ua-ring small { font-size:10px; color:var(--slate); margin-top:3px; }
.ua-insights { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }
.ua-insight { padding:22px 23px; border:1px solid var(--line); background:white; border-radius:13px; }
.ua-insight.opportunity { background:var(--gold-soft); border-color:#E8DEC8; }
.ua-insight .top { display:flex; align-items:center; gap:9px; color:var(--teal); margin-bottom:12px; }
.ua-insight.opportunity .top { color:#8A6E37; }
.ua-insight h3 { font-size:11px; font-weight:600; margin:0; padding:0; }
.ua-insight p { font-size:12px; line-height:1.85; color:var(--slate); margin:0; }
.ua-insight strong { font-weight:600; color:var(--navy); }
.ua-insight-note { font-size:10px; line-height:1.7; color:var(--slate); margin:12px 0 0; }
.stTabs [data-baseweb="tab-list"] { gap:22px; background:transparent; border-bottom:1px solid var(--line); }
.stTabs [data-baseweb="tab"] { color:var(--slate); font-size:12px; padding:12px 0; white-space:nowrap; }
.stTabs [aria-selected="true"] { color:var(--navy) !important; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"] { background:var(--gold); height:2px; }
.stTabs [data-baseweb="tab-border"] { display:none; }
[data-testid="stDataFrame"] { border-radius:11px; border:1px solid var(--line); overflow:hidden; }
.st-key-card_context { background:transparent; padding:0; border:0; box-shadow:none; }
.st-key-az_cta { padding:29px; border-radius:15px; background:var(--navy); color:white; }
.st-key-az_cta h3 { color:white; font-size:24px; font-weight:500; letter-spacing:-.6px; padding:0; margin:5px 0 12px; }
.st-key-az_cta p { color:#BFCDD3; font-size:12px; line-height:1.9; }
.st-key-az_cta .ua-eyebrow { color:var(--gold-light); }
.st-key-az_cta [data-testid="stWidgetLabel"] p { color:#D3DCDF; }
.st-key-az_cta [data-testid="stRadio"] label p { color:white; }
.st-key-az_cta [data-testid="stBaseButton-primary"] { background:var(--gold-light) !important; color:var(--navy) !important; border-color:var(--gold-light) !important; }
/* Calculator: one focused product at a time, with an immediate estimate. */
.st-key-calc_product { margin:7px 0 15px; }
.st-key-calc_product button { border-radius:8px !important; min-height:42px; font-size:12px; padding:9px 25px !important; border:1px solid var(--line) !important; background:white !important; color:var(--slate) !important; }
.st-key-calc_product button[aria-pressed="true"], .st-key-calc_product [data-testid="stBaseButton-segmented_controlActive"] { color:white !important; background:var(--navy) !important; border-color:var(--navy) !important; }
.ua-loan-head { display:flex; align-items:center; gap:12px; margin-bottom:15px; }
.ua-loan-head h3 { color:var(--navy); font-size:20px; margin:0 0 4px; padding:0; letter-spacing:-.5px; font-weight:600; }
.ua-loan-head small { font-size:11px; color:var(--slate); }
.ua-slider-range { display:flex; justify-content:space-between; color:var(--slate); font-size:10px; margin-top:-7px; margin-bottom:9px; }
.ua-estimate { background:var(--navy); border-radius:18px; padding:30px 34px; color:white; }
.ua-estimate .ua-eyebrow { color:var(--gold-light); margin-bottom:24px; }
.ua-estimate .ua-emi-label { font-size:12px; color:#CCD6D9; margin-bottom:9px; }
.ua-estimate .ua-emi { font-size:49px; font-weight:500; letter-spacing:-2px; font-variant-numeric:tabular-nums; line-height:1.2; }
.ua-estimate .ua-emi small { font-size:17px; font-weight:400; color:#CDD9DC; letter-spacing:0; margin-right:8px; }
.ua-estimate .ua-emi-note { margin-top:9px; font-size:11px; color:#ADBDC7; }
.ua-estimate .ua-estimate-stats { display:grid; grid-template-columns:repeat(3,1fr); margin-top:30px; padding-top:22px; border-top:1px solid #3B5160; gap:17px; }
.ua-estimate-stats .label { font-size:10px; color:#C2CDD0; }
.ua-estimate-stats strong { display:block; font-size:15px; font-weight:500; margin-top:9px; color:#F0F0E8; font-variant-numeric:tabular-nums; }
.ua-split-bar { display:flex; height:11px; border-radius:6px; overflow:hidden; background:var(--line); margin:20px 0 15px; }
.ua-split-bar i { background:var(--teal); }
.ua-split-bar b { background:var(--gold); flex:1; }
.ua-split-labels { display:flex; justify-content:space-between; gap:14px; color:var(--slate); font-size:11px; }
.ua-split-labels b { color:var(--navy); font-size:13px; display:block; margin-top:8px; font-weight:600; }
.ua-legend-dot { display:inline-block; width:7px; height:7px; border-radius:50%; margin-right:5px; background:var(--teal); }
.ua-legend-dot.gold { background:var(--gold); }
.ua-prefill { border:1px solid #C9DFCF; background:var(--teal-soft); padding:14px 17px; border-radius:10px; font-size:12px; color:var(--teal); line-height:1.8; }
.ua-footer { display:flex; align-items:center; justify-content:space-between; gap:22px; padding:25px 0 7px; margin-top:30px; border-top:1px solid var(--line); }
.ua-footer > div { flex:none; }
.ua-footer b { color:var(--navy); display:block; font-size:11px; font-weight:600; margin-bottom:5px; }
.ua-footer div span { color:var(--slate); font-size:10px; }
.ua-footer p { color:var(--slate); font-size:10px; line-height:1.8; text-align:center; margin:0; max-width:520px; }
.ua-footer-note { color:var(--slate); font-size:10px; white-space:nowrap; }
@media (max-width:1100px) {
 .ua-landing-hero { padding:34px 30px; }
 .st-key-card_upload { padding:26px; }
 .ua-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
 .ua-metric .value { font-size:28px; }
 .ua-landing-hero h1 { font-size:39px; }
 .ua-footer-note { display:none; }
}
@media (max-width:800px) {
 [data-testid="stMainBlockContainer"], .block-container { padding:0 20px 20px !important; }
 .st-key-appbar { margin-bottom:18px; padding-top:17px; }
 .st-key-appbar > [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
 .ua-landing-hero { min-height:430px; }
 .ua-landing-hero h1 { font-size:38px; }
 .ua-hero-bottom { margin-top:24px; }
 .ua-page-heading h1 { font-size:29px; }
 .ua-benefits { gap:12px; }
 .ua-benefit { padding:18px; }
 .ua-insights { grid-template-columns:1fr; }
 .ua-section > span { display:none; }
 .ua-estimate .ua-emi { font-size:39px; }
}
@media (max-width:640px) {
 [data-testid="stMainBlockContainer"], .block-container { padding:0 15px 18px !important; }
 .st-key-appbar [data-testid="stHorizontalBlock"] { flex-wrap:wrap !important; }
 .st-key-appbar [data-testid="stColumn"] { flex:1 1 100% !important; min-width:0 !important; width:100% !important; }
 .st-key-appbar_actions { display:none; }
 .st-key-module button { flex:1; }
 .ua-landing-hero { min-height:430px; padding:31px 27px; border-radius:16px; }
 .st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stHtml"],
 .st-key-landing_row [data-testid="stColumn"]:first-child .stElementContainer,
 .st-key-landing_row .ua-landing-hero { height:auto; }
 .ua-landing-hero h1 { font-size:37px; letter-spacing:-1.5px; }
 .ua-landing-hero .ua-lead { font-size:13px; }
 .ua-metrics { gap:10px; }
 .ua-metric { padding:16px 14px; }
 .ua-metric .value { font-size:23px; letter-spacing:-.8px; }
 .ua-metric.date .value { font-size:22px; }
 .ua-metric .top { margin-bottom:13px; }
 .ua-metric .top svg { width:17px; }
 .ua-metric .label { font-size:9px; }
 .ua-metric .sub { font-size:9px; }
 .ua-benefits, .ua-guide { grid-template-columns:1fr; }
 [class*="st-key-card_"] { padding:22px 21px; }
 .st-key-card_upload { min-height:0; }
 .ua-section h2 { font-size:21px; }
 .ua-estimate { padding:27px; }
 .ua-estimate .ua-emi { font-size:38px; }
 .ua-estimate-stats strong { font-size:13px; }
 .ua-footer { align-items:flex-start; flex-direction:column; gap:12px; }
 .ua-footer p { text-align:left; }
 .st-key-calc_product button { padding:10px 13px !important; }
 .stTabs [data-baseweb="tab-list"] { gap:18px; overflow-x:auto; }
}
@media (prefers-reduced-motion:reduce) { *, *::before, *::after { scroll-behavior:auto !important; animation:none !important; transition:none !important; } }

/* ===== Live-app additions (not needed in the static preview) ===== */
#MainMenu, footer, [data-testid="stDecoration"], [data-testid="stStatusWidget"] { display:none !important; }
.st-key-appbar [data-testid="stHorizontalBlock"] { align-items:center; }
.st-key-module { display:flex; justify-content:center; }
.st-key-module [data-testid="stButtonGroup"] { gap:6px; }
.st-key-appbar_actions [data-testid="stPopover"] button { min-height:40px; width:100%; color:var(--slate); justify-content:flex-start; font-weight:500; }
[data-testid="stPopoverBody"] { width:min(620px, 92vw); padding:22px 24px; border-radius:14px; }
[data-testid="stPopoverBody"] h4 { margin:0 0 14px; padding:0; color:var(--navy); font-size:15px; }
.ua-guide-caption { font-size:11px; color:var(--slate); margin-top:16px; }
/* generic segmented controls (projection view) */
.st-key-az_projection_view button { min-height:32px !important; padding:6px 15px !important; border:1px solid var(--line) !important; border-radius:6px !important; background:white !important; color:var(--slate) !important; font-size:11px !important; }
.st-key-az_projection_view [data-testid="stBaseButton-segmented_controlActive"] { background:var(--teal-soft) !important; color:var(--teal) !important; border-color:#C9DFCF !important; }
/* equal-height panel pair */
.st-key-dashboard_pair [data-testid="stHorizontalBlock"], .st-key-calc_row [data-testid="stHorizontalBlock"] { align-items:stretch; }
.st-key-dashboard_pair [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > * { flex:1 1 auto; }
.st-key-card_outlook, .st-key-card_progress { box-sizing:border-box; }
/* upload card states */
.ua-alert { display:flex; gap:12px; padding:15px 16px; border-radius:11px; border:1px solid; font-size:12px; line-height:1.7; }
.ua-alert b { display:block; font-size:13px; margin-bottom:2px; }
.ua-alert ul { margin:6px 0 0 16px; padding:0; }
.ua-alert.err { background:#FDF3F1; border-color:#F0CFC8; color:#8A2E1E; }
.ua-alert.warn { background:var(--gold-soft); border-color:#E8DEC8; color:#7F683F; }
.st-key-card_upload [data-testid="stFileUploaderFile"] { display:none; }
.st-key-card_upload [data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child { font-size:0 !important; }
.st-key-card_upload [data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child::before { content:"Drag and drop your file here"; font-size:13px; font-weight:600; color:var(--navy); }
.st-key-card_upload [data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child { font-size:0 !important; }
.st-key-card_upload [data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child::before { content:"XLSX, XLS or CSV · up to 10 MB"; font-size:10px; color:var(--slate); }
[data-testid="stFileUploaderDropzoneInstructions"] svg { color:var(--teal); }
[data-testid="stFileUploaderDropzone"].drag-over { border-color:var(--teal); border-style:solid; background:var(--teal-soft); }
/* analysis progress */
.ua-progress { max-width:520px; margin:40px auto; background:white; border:1px solid var(--line); border-radius:var(--r); box-shadow:var(--shadow); padding:30px 32px; }
.ua-progress h4 { margin:0; padding:0; color:var(--navy); font-size:19px; font-weight:600; letter-spacing:-.4px; }
.ua-progress .sub { color:var(--slate); font-size:12px; margin:4px 0 18px; }
.ua-stage { display:flex; align-items:center; gap:11px; padding:8px 0; font-size:13px; color:var(--mist); }
.ua-stage .dot { width:20px; height:20px; border-radius:50%; border:1.5px solid var(--line); display:grid; place-items:center; flex:none; color:white; }
.ua-stage.done { color:var(--ink); } .ua-stage.done .dot { background:var(--teal); border-color:var(--teal); }
.ua-stage.now { color:var(--navy); font-weight:600; } .ua-stage.now .dot { border-color:var(--teal); }
.ua-stage.now .dot::after { content:""; width:8px; height:8px; border-radius:50%; background:var(--teal); animation:uaPulse 1s ease-in-out infinite; }
.ua-pbar { height:4px; background:#EDF0EE; border-radius:2px; overflow:hidden; margin-top:16px; }
.ua-pbar i { display:block; height:100%; background:var(--teal); transition:width .3s; }
@keyframes uaPulse { 0%,100% { opacity:.35; } 50% { opacity:1; } }
/* heading row actions */
.st-key-az_head_actions, .st-key-calc_head_actions { padding-top:22px; }
/* calculator inputs */
.st-key-card_calc_inputs [data-testid="stSlider"] { margin-top:-6px; }
.st-key-card_calc_inputs [data-testid="stNumberInputContainer"] input { font-size:19px; }
.st-key-card_calc_split { margin-top:0; }
.ua-insight { display:block; }
.ua-more-insights { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:16px; }
@media (max-width:800px) { .ua-more-insights { grid-template-columns:1fr; } .st-key-az_head_actions, .st-key-calc_head_actions { padding-top:0; } }
/* Streamlit's markdown sets p { font-size:1rem } - keep the design's small text sizes */
[data-testid="stMarkdownContainer"] p.ua-formats { font-size:11px; line-height:1.65; margin:0; }
[data-testid="stMarkdownContainer"] p.ua-insight-note { font-size:10px; line-height:1.7; margin:12px 0 0; }
[data-testid="stMarkdownContainer"] .ua-private-note, [data-testid="stMarkdownContainer"] p.ua-private-note { font-size:10px; line-height:1.7; margin:0; }
[data-testid="stMarkdownContainer"] .ua-insight p, [data-testid="stMarkdownContainer"] .ua-benefit p,
[data-testid="stMarkdownContainer"] .ua-guide p { font-size:12px; }
[data-testid="stMarkdownContainer"] .ua-page-heading p { font-size:12px; }
[data-testid="stMarkdownContainer"] .ua-landing-hero .ua-lead { font-size:14px; }
[data-testid="stMarkdownContainer"] .st-key-az_cta p, .st-key-az_cta [data-testid="stMarkdownContainer"] p { font-size:12px; }
[data-testid="stCaptionContainer"] { font-size:11px; color:var(--slate); }
[data-testid="stMarkdownContainer"] p.ua-guide-caption { font-size:11px; margin:16px 0 0; }
.ua-guide-title { color:var(--navy); font-size:15px; font-weight:600; margin-bottom:14px; }
/* landing: hero stretches to the upload card's height */
.st-key-landing_row [data-testid="stHorizontalBlock"] { align-items:stretch; }
.st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdown"],
.st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"],
.st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] > div { height:100%; }
/* amount slider mirrors the number input: no duplicate value / tick labels */
[class*="_amt_sl"] [data-testid="stSliderThumbValue"], [class*="_amt_sl"] [data-testid="stSliderTickBar"] { display:none; }
@media (max-width:640px) {
  .st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdown"],
  .st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"],
  .st-key-landing_row [data-testid="stColumn"]:first-child [data-testid="stMarkdownContainer"] > div { height:auto; }
}
</style>
"""

# Runs in the page (st.html with JavaScript) - no deprecated components.html / iframes.
JS_UPLOAD_DRAG = """
<script>
(() => {
  const doc = document;
  if (window.__uaeDragBound) return; window.__uaeDragBound = true;
  const zone = () => doc.querySelector('[data-testid="stFileUploaderDropzone"]');
  let depth = 0;
  doc.addEventListener('dragenter', e => { const z = zone(); if (z && z.contains(e.target)) { depth++; z.classList.add('drag-over'); } }, true);
  doc.addEventListener('dragleave', e => { const z = zone(); if (z && z.contains(e.target)) { depth = Math.max(0, depth - 1); if (!depth) z.classList.remove('drag-over'); } }, true);
  doc.addEventListener('drop', () => { depth = 0; const z = zone(); if (z) z.classList.remove('drag-over'); }, true);
})();
</script>
"""


def js_scroll(target: str) -> str:
    return f"""<script>
(() => {{
  const t = "{target}";
  const go = (smooth) => {{
    const main = document.querySelector('[data-testid="stMain"]');
    const el = t === "top" ? null : (document.getElementById(t) || document.querySelector('.st-key-' + t));
    if (el) el.scrollIntoView({{behavior: smooth ? "smooth" : "auto", block: "start"}});
    else {{ if (main) main.scrollTop = 0; window.scrollTo(0, 0); }}
  }};
  setTimeout(() => go(true), 200);
  if (t === "top") {{ setTimeout(() => go(false), 600); setTimeout(() => go(false), 1200); }}
}})();
</script>"""


JS_COUNTUP = """<script>
setTimeout(() => {
  document.querySelectorAll('.num[data-v]:not([data-done])').forEach(el => {
    el.setAttribute('data-done', '1');
    const end = parseFloat(el.dataset.v), dec = parseInt(el.dataset.d || '0'), suf = el.dataset.s || '';
    const fmt = v => v.toLocaleString('en-US', {minimumFractionDigits: dec, maximumFractionDigits: dec}) + suf;
    const t0 = performance.now(), dur = 900;
    const step = now => { const p = Math.min((now - t0) / dur, 1), e = 1 - Math.pow(1 - p, 3);
      el.textContent = fmt(end * e); if (p < 1) requestAnimationFrame(step); };
    requestAnimationFrame(step);
  });
}, 60);
</script>"""
