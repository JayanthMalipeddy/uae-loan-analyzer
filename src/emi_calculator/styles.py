"""Design system + page CSS.

Tokens (shared by both modules):
  Navy   #0B1F3A  primary / headings / primary buttons
  Teal   #0E7C66  positive / secondary accent / active state
  Gold   #A8823F  financial highlights (used sparingly)
  Ink    #0F172A  text   ·  Slate #64748B  secondary text  ·  Mist #94A3B8  labels   (calculator palette)
  Line   #E2E8F0  borders · Surface #FFFFFF cards · Warm #FAF8F4 subtle panels
  Radius 6px (controls) / 14px (inner cards) / 18px (cards) / 22px (hero)
  The EMI Calculator's background, cards, hero and section titles are the source of truth;
  the Loan Analyzer reuses those same rules (shared selectors), it does not restyle them.
  Type: Inter, tabular numerals; labels 11px uppercase .08em tracking
"""

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
:root {
  --navy: #0B1F3A; --navy-2: #13294B; --teal: #0E7C66; --teal-soft: #E7F3F0; --gold: #A8823F; --gold-soft: #F6F0E4;
  --ink: #0F172A; --slate: #64748B; --mist: #94A3B8; --line: #E2E8F0; --line-2: #EEF2F7;
  --canvas: #F6F7F9; --surface: #FFFFFF; --warm: #FAF8F4; --danger: #B42318; --danger-soft: #FEF3F2;
  --r-sm: 6px; --r-md: 14px; --r-lg: 18px;
  --shadow: 0 6px 18px -12px rgba(15,23,42,.25);           /* calculator .summary-row card */
  --shadow-card: 0 10px 30px -15px rgba(15,23,42,.25);     /* calculator loan cards */
  --shadow-card-hover: 0 18px 38px -16px rgba(15,23,42,.32);
  --ease: cubic-bezier(.2,.7,.2,1);
}
html, body, [class*="css"], .stApp, button, input, textarea { font-family: 'Inter', system-ui, sans-serif; }
/* App background - the EMI Calculator's background, now shared by both modules */
.stApp {
  color: var(--ink);
  background:
    radial-gradient(circle at 10% 0%, rgba(14,124,102,.10) 0, transparent 40%),
    radial-gradient(circle at 95% 10%, rgba(168,130,63,.10) 0, transparent 35%),
    radial-gradient(rgba(11,31,58,.05) 1px, transparent 1px),
    linear-gradient(180deg, #F8FAFC 0%, #EEF3F9 100%);
  background-size: auto, auto, 22px 22px, auto; background-attachment: fixed;
}
.num, .metric .v, .hero-metric .v { font-variant-numeric: tabular-nums; }
header[data-testid="stHeader"] { background: transparent; height: 0; pointer-events: none; }
header[data-testid="stHeader"] * { pointer-events: auto; }
[data-testid="stToolbar"] { top: .35rem; right: .5rem; }
.block-container { padding-top: 0 !important; max-width: 1280px; }
.st-key-js_runner { display: none; }

/* ---------- buttons (shared) ---------- */
.stButton > button, .stDownloadButton > button {
  border-radius: var(--r-sm); font-weight: 600; font-size: .9rem; min-height: 2.6rem;
  border: 1px solid var(--line); color: var(--ink); background: var(--surface);
  transition: background .15s var(--ease), border-color .15s var(--ease), color .15s var(--ease), box-shadow .15s var(--ease);
}
.stButton > button:hover, .stDownloadButton > button:hover { border-color: var(--navy); color: var(--navy); background: #FBFCFD; }
[data-testid="stBaseButton-primary"] { background: var(--navy) !important; border-color: var(--navy) !important; color: #fff !important; }
[data-testid="stBaseButton-primary"]:hover { background: var(--navy-2) !important; box-shadow: 0 6px 16px -8px rgba(11,31,58,.55); }
[data-testid="stBaseButton-tertiary"] { color: var(--slate) !important; font-weight: 600; }
[data-testid="stBaseButton-tertiary"]:hover { color: var(--navy) !important; }
.stButton > button:focus-visible { outline: 2px solid var(--teal); outline-offset: 2px; }

/* ---------- inputs (shared) ---------- */
[data-baseweb="select"] > div, [data-testid="stNumberInputContainer"], .stTextInput input {
  border-radius: var(--r-sm) !important; border-color: var(--line) !important; background: var(--surface) !important; }
[data-testid="stWidgetLabel"] p { font-size: .8rem; font-weight: 600; color: var(--slate); }

/* ---------- app bar / navigation ---------- */
.st-key-appbar {
  background: var(--surface); padding: .75rem 0; margin-bottom: 1.6rem; position: relative;
  box-shadow: 0 0 0 100vmax var(--surface), 0 1px 0 100vmax var(--line); clip-path: inset(-100vmax -100vmax -1px -100vmax);
}
.brand { display: flex; align-items: center; gap: .7rem; }
.brand .logo { width: 38px; height: 38px; border-radius: 8px; display: grid; place-items: center;
  background: var(--navy); color: #E9D7AE; font-weight: 700; font-size: .78rem; letter-spacing: .06em; }
.brand .name { font-weight: 700; font-size: 1rem; color: var(--navy); letter-spacing: -.005em; line-height: 1.15; }
.brand .tag { font-size: .72rem; color: var(--mist); letter-spacing: .02em; }
.st-key-module [data-testid="stButtonGroup"] { gap: 0; }
.st-key-module button {
  background: transparent !important; border: none !important; border-radius: 0 !important; box-shadow: none !important;
  color: var(--slate) !important; font-weight: 600 !important; padding: .55rem 1rem !important;
  border-bottom: 2px solid transparent !important; min-height: 2.6rem;
}
.st-key-module button:hover { color: var(--navy) !important; }
.st-key-module [data-testid="stBaseButton-segmented_controlActive"] {
  color: var(--navy) !important; border-bottom-color: var(--teal) !important; }
.st-key-appbar_actions [data-testid="stHorizontalBlock"] { justify-content: flex-end; }
.st-key-appbar button { white-space: nowrap; }
.st-key-appbar button p { white-space: nowrap; }

/* ---------- generic surfaces ---------- */
.eyebrow { font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--teal); }
/* panel headings = calculator .loan-head h3 / small, in the primary navy */
.panel-title { font-size: 1.2rem; font-weight: 700; color: var(--navy); margin: 0 0 .15rem; letter-spacing: -.01em; }
.panel-sub { font-size: .8rem; color: var(--slate); margin-bottom: .5rem; }
.muted { color: var(--slate); font-size: .85rem; }

.st-key-page_az [class*="st-key-card_"] { padding: 1.25rem 1.35rem 1.1rem; }

/* ---------- hero (Analyzer) ---------- */
.st-key-hero_btns { max-width: 380px; }
.st-key-hero_btns button p { white-space: nowrap; }
.hero-copy h1 { color: #fff; font-size: 2.3rem; font-weight: 700; letter-spacing: -.02em; line-height: 1.12; margin: .7rem 0 .5rem; padding: 0; }
.hero-copy p { color: rgba(255,255,255,.85); font-size: 1rem; line-height: 1.55; max-width: 560px; margin: 0; }
.trust { display: grid; gap: .8rem; padding-left: 1.4rem; border-left: 1px solid rgba(255,255,255,.14); }
.trust .t { display: flex; gap: .7rem; align-items: flex-start; color: rgba(255,255,255,.85); font-size: .84rem; line-height: 1.4; }
.trust .t b { color: #fff; font-weight: 600; display: block; font-size: .86rem; }
.trust svg { flex: none; margin-top: .1rem; }
.st-key-az_hero [data-testid="stBaseButton-primary"] { background: #fff !important; color: var(--navy) !important; border-color: #fff !important; }
.st-key-az_hero [data-testid="stBaseButton-primary"]:hover { background: #F1F4F8 !important; }
.st-key-az_hero [data-testid="stBaseButton-secondary"] { background: transparent; color: #fff; border-color: rgba(255,255,255,.35); }
.st-key-az_hero [data-testid="stBaseButton-secondary"]:hover { border-color: #fff; color: #fff; background: rgba(255,255,255,.06); }

/* ---------- upload ---------- */
.upload-head { display: flex; align-items: center; gap: .8rem; margin-bottom: .8rem; }
.upload-head .doc { width: 40px; height: 40px; border-radius: 8px; background: var(--teal-soft); display: grid; place-items: center; flex: none; }
[data-testid="stFileUploaderDropzone"] {
  background: #FBFCFD; border: 1.5px dashed #C9D2DD; border-radius: var(--r-md);
  height: auto !important; min-height: 190px; padding: 1.5rem 1.2rem !important;
  display: flex; flex-direction: column; align-items: center; justify-content: center; gap: .9rem; text-align: center;
  transition: border-color .15s var(--ease), background .15s var(--ease), box-shadow .15s var(--ease);
}
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--teal); background: #F6FBFA; }
[data-testid="stFileUploaderDropzone"].drag-over { border-color: var(--teal); border-style: solid; background: var(--teal-soft);
  box-shadow: 0 0 0 4px rgba(14,124,102,.10); }
[data-testid="stFileUploaderDropzoneInstructions"] { display: flex; flex-direction: column; align-items: center; gap: .55rem; margin: 0 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > span svg { color: var(--teal); width: 2.1rem; height: 2.1rem; }
[data-testid="stFileUploaderDropzoneInstructions"] > div { align-items: center; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child { font-size: 0 !important; line-height: 1.3; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:first-child::before {
  content: "Drag & drop your Excel file here"; font-size: 1rem; font-weight: 600; color: var(--navy); }
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child { font-size: 0 !important; }
[data-testid="stFileUploaderDropzoneInstructions"] > div > span:last-child::before {
  content: "or browse from your device  ·  .xlsx  ·  .xls  ·  .csv"; font-size: .8rem; color: var(--mist); }
[data-testid="stFileUploaderDropzone"] button { border-radius: var(--r-sm); border: 1px solid var(--navy) !important;
  color: var(--navy) !important; font-weight: 600; padding: .45rem 1.3rem; }
[data-testid="stFileUploaderDropzone"] button:hover { background: var(--navy) !important; color: #fff !important; }
[data-testid="stFileUploaderFile"] { display: none; }   /* replaced by our file summary */
.formats { display: flex; gap: .4rem; align-items: center; margin-top: .7rem; font-size: .76rem; color: var(--mist); flex-wrap: wrap; }
.formats code { background: var(--line-2); color: var(--slate); border-radius: 4px; padding: .08rem .38rem; font-size: .74rem; }

.file-ok { display: flex; gap: .9rem; align-items: center; padding: .95rem 1.05rem; border: 1px solid #BFE3DA;
  background: #F4FAF8; border-radius: var(--r-md); animation: rise .35s var(--ease) both; }
.file-ok .ic { width: 38px; height: 38px; border-radius: 8px; background: #fff; border: 1px solid #BFE3DA; display: grid; place-items: center; flex: none; }
.file-ok .fn { font-weight: 700; color: var(--navy); font-size: .95rem; word-break: break-all; }
.file-ok .meta { font-size: .8rem; color: var(--slate); display: flex; gap: .9rem; flex-wrap: wrap; margin-top: .15rem; }
.file-ok .meta .okc { color: var(--teal); font-weight: 600; }
.alert { display: flex; gap: .85rem; padding: .95rem 1.05rem; border-radius: var(--r-md); border: 1px solid; animation: rise .3s var(--ease) both; }
.alert .t { font-weight: 700; font-size: .93rem; margin-bottom: .15rem; }
.alert .d { font-size: .84rem; line-height: 1.5; }
.alert.err { background: var(--danger-soft); border-color: #F5C2BC; color: #7A271A; }
.alert.warn { background: #FFFAEB; border-color: #F3DFA2; color: #7A4D0B; }
.alert ul { margin: .35rem 0 0 1rem; padding: 0; }

/* ---------- slideshow ---------- */
.howto-top { display: flex; justify-content: space-between; align-items: center; margin-bottom: .9rem; }
.howto-top .lbl { font-size: .7rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--mist); }
.bars { display: grid; grid-template-columns: repeat(4, 1fr); gap: .35rem; margin-bottom: 1.05rem; }
.bars i { height: 3px; border-radius: 2px; background: var(--line); transition: background .3s var(--ease); }
.bars i.on { background: var(--teal); }
.bars i.done { background: #9CCFC3; }
.slide { display: grid; grid-template-columns: 56px 1fr; gap: 1rem; align-items: start; min-height: 112px; animation: fadeIn .35s var(--ease) both; }
.slide .ico { width: 56px; height: 56px; border-radius: 10px; background: var(--warm); border: 1px solid var(--line); display: grid; place-items: center; }
.slide .no { font-size: .74rem; font-weight: 700; color: var(--gold); letter-spacing: .08em; }
.slide .st { font-size: 1.02rem; font-weight: 700; color: var(--navy); margin: .2rem 0 .3rem; }
.slide .sx { font-size: .86rem; color: var(--slate); line-height: 1.5; }

/* ---------- analysis progress ---------- */
.progress-card { max-width: 560px; margin: 2rem auto; background: var(--surface); border: 1px solid var(--line);
  border-radius: var(--r-md); box-shadow: var(--shadow); padding: 1.6rem 1.8rem; }
.progress-card h4 { margin: 0; padding: 0; color: var(--navy); font-size: 1.1rem; }
.progress-card .sub { color: var(--slate); font-size: .86rem; margin: .2rem 0 1.1rem; }
.stage { display: flex; align-items: center; gap: .75rem; padding: .5rem 0; font-size: .9rem; color: var(--mist); }
.stage .dot { width: 20px; height: 20px; border-radius: 50%; border: 1.5px solid var(--line); display: grid; place-items: center; flex: none; }
.stage.done { color: var(--ink); }
.stage.done .dot { background: var(--teal); border-color: var(--teal); }
.stage.now { color: var(--navy); font-weight: 600; }
.stage.now .dot { border-color: var(--teal); }
.stage.now .dot::after { content: ""; width: 8px; height: 8px; border-radius: 50%; background: var(--teal); animation: pulse 1s ease-in-out infinite; }
.pbar { height: 4px; background: var(--line-2); border-radius: 2px; overflow: hidden; margin-top: 1rem; }
.pbar i { display: block; height: 100%; background: linear-gradient(90deg, var(--teal), #3AA58C); transition: width .3s var(--ease); }

/* ---------- context bar (after analysis) ---------- */
.ctx { display: flex; align-items: center; gap: .8rem; flex-wrap: wrap; font-size: .84rem; color: var(--slate); }
.ctx .file { display: inline-flex; align-items: center; gap: .45rem; font-weight: 600; color: var(--navy); }
.ctx .sep { width: 1px; height: 14px; background: var(--line); }
.badge { display: inline-block; padding: .14rem .5rem; border-radius: 4px; font-size: .7rem; font-weight: 700; letter-spacing: .04em; text-transform: uppercase; }
.badge.ok { background: var(--teal-soft); color: var(--teal); }
.badge.muted { background: var(--line-2); color: var(--slate); }
.badge.gold { background: var(--gold-soft); color: #7D5F27; }

/* ---------- overview / metrics ---------- */
.st-key-card_overview { padding: 1.5rem 1.6rem 1.3rem !important; }
.ov-head { display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.1rem; }

.hero-metrics { display: grid; grid-template-columns: 1fr 1.15fr 1fr; border: 1px solid var(--line); border-radius: var(--r-md); overflow: hidden; }
.hero-metric { padding: 1.1rem 1.3rem; border-right: 1px solid var(--line); background: var(--surface); }
.hero-metric:last-child { border-right: none; }
.hero-metric.key { background: var(--warm); box-shadow: inset 0 3px 0 var(--gold); }
.hero-metric .l { font-size: .7rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; color: var(--mist); }
.hero-metric .v { font-size: 1.95rem; font-weight: 700; color: var(--navy); letter-spacing: -.02em; margin: .35rem 0 .2rem; line-height: 1.1; }
.hero-metric .v .cur { font-size: .95rem; font-weight: 600; color: var(--slate); margin-right: .3rem; letter-spacing: 0; }
.hero-metric .s { font-size: .8rem; color: var(--slate); }
.sec-metrics { display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 1rem; }
.metric { padding: .2rem 1.1rem; border-left: 1px solid var(--line); }
.metric:first-child { border-left: none; padding-left: .2rem; }
.metric .l { font-size: .7rem; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--mist); }
.metric .v { font-size: 1.12rem; font-weight: 700; color: var(--ink); margin-top: .25rem; }
.metric .s { font-size: .76rem; color: var(--slate); margin-top: .1rem; }
.progress-line { margin-top: 1.2rem; }
.progress-line .top { display: flex; justify-content: space-between; font-size: .78rem; color: var(--slate); margin-bottom: .4rem; }
.progress-line .top b { color: var(--navy); }
.progress-line .track { height: 6px; background: var(--line-2); border-radius: 3px; overflow: hidden; }
.progress-line .fill { height: 100%; background: linear-gradient(90deg, var(--teal), #2F9E85); border-radius: 3px; animation: grow .9s var(--ease) both; transform-origin: left; }

/* equal-size panel pairs (Repayment Progress | Loan Details, Interest vs Principal | Outstanding Balance) */
.st-key-pair_top > div > [data-testid="stHorizontalBlock"], .st-key-pair_charts > div > [data-testid="stHorizontalBlock"],
.st-key-pair_top [data-testid="stHorizontalBlock"], .st-key-pair_charts [data-testid="stHorizontalBlock"] { align-items: stretch; }
.st-key-pair_top [data-testid="stColumn"] > [data-testid="stVerticalBlock"],
.st-key-pair_charts [data-testid="stColumn"] > [data-testid="stVerticalBlock"] { height: 100%; }
.st-key-pair_top [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > *,
.st-key-pair_charts [data-testid="stColumn"] > [data-testid="stVerticalBlock"] > * { flex: 1 1 auto; }
.st-key-card_progress, .st-key-card_details, .st-key-card_flows, .st-key-card_outlook { height: 100%; box-sizing: border-box; }

/* details list */
.dl { display: grid; }
.dl .row { display: flex; justify-content: space-between; gap: 1rem; padding: .62rem 0; border-bottom: 1px solid var(--line-2); font-size: .86rem; }
.dl .row:last-child { border-bottom: none; }
.dl .k { color: var(--slate); }
.dl .v { color: var(--ink); font-weight: 600; text-align: right; font-variant-numeric: tabular-nums; }

/* insights */
.insights-grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); grid-auto-rows: 1fr; gap: .9rem; }
.insight { background: #fff; border: 1px solid var(--line); border-radius: var(--r-md); padding: 1rem 1.15rem;
  box-shadow: var(--shadow); min-height: 128px; height: 100%; box-sizing: border-box; }
.insight .t { font-size: .72rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; color: var(--navy); margin-bottom: .45rem; }
.insight.teal .t { color: var(--teal); } .insight.gold .t { color: var(--gold); } .insight.warn .t { color: var(--danger); }
.insight .x { font-size: .9rem; color: var(--ink); line-height: 1.55; }
.insight .x b { color: var(--navy); font-weight: 700; }

/* CTA band */
.st-key-az_cta .eyebrow { color: #E9C46A; }
.st-key-az_cta h3 { color: #fff; margin: .35rem 0 .3rem; padding: 0; font-size: 1.3rem; font-weight: 700; letter-spacing: -.01em; }
.st-key-az_cta .cta-copy p { color: rgba(255,255,255,.75); margin: 0; font-size: .9rem; line-height: 1.5; }
.st-key-az_cta [data-testid="stBaseButton-primary"] { background: #fff !important; color: var(--navy) !important; border-color: #fff !important; }
.st-key-az_cta [data-testid="stBaseButton-primary"] p, .st-key-az_hero [data-testid="stBaseButton-primary"] p { color: var(--navy) !important; }
.st-key-az_cta [data-testid="stBaseButton-primary"]:hover { background: #F1F4F8 !important; }
.st-key-az_cta [data-testid="stBaseButton-secondary"] { background: transparent; color: #fff; border-color: rgba(255,255,255,.35); }
.st-key-az_cta [data-testid="stBaseButton-secondary"]:hover { color: #fff; border-color: #fff; background: rgba(255,255,255,.06); }
.st-key-az_cta [data-testid="stWidgetLabel"] p { color: rgba(255,255,255,.7); }
.st-key-az_cta [data-testid="stRadio"] label p { color: #fff; }

/* charts & tables */
.st-key-page_az .stPlotlyChart { animation: fadeIn .5s var(--ease) both; }
.st-key-page_az [data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: var(--r-md); overflow: hidden; }
@media (max-width: 640px) {
  [class*="st-key-scroll_"] { overflow-x: auto; }
  [class*="st-key-scroll_"] .stPlotlyChart { min-width: 520px; }
}
.foot { text-align: center; color: var(--mist); font-size: .76rem; margin: 2.4rem 0 1.2rem; line-height: 1.6; }

/* prefill banner (calculator) */
.prefill-banner { background: var(--teal-soft); border: 1px solid #BFE3DA; color: #0B4F42; border-radius: var(--r-md);
  padding: .75rem 1rem; margin-bottom: .6rem; font-size: .9rem; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes rise { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }
@keyframes grow { from { transform: scaleX(0); } to { transform: scaleX(1); } }
@keyframes pulse { 0%,100% { opacity: .35; } 50% { opacity: 1; } }
@media (prefers-reduced-motion: reduce) { * { animation: none !important; transition: none !important; } }

/* =================== EMI CALCULATOR components (source of truth, reused by the Analyzer) =================== */
/* Hero surface - calculator hero; also used by the Analyzer hero and the Analyzer CTA band */
.hero, .st-key-az_hero, .st-key-az_cta {
  position: relative; overflow: hidden; text-align: center;
  padding: 2.6rem 1.5rem 2.2rem; margin-bottom: 1.8rem; border-radius: 22px;
  background: linear-gradient(120deg, #0B1F3A 0%, #0F2747 40%, #0E5F55 75%, #0E7C66 100%);
  box-shadow: 0 18px 40px -18px rgba(11,31,58,.55); color: #fff;
}
.hero::before, .hero::after, .st-key-az_hero::before, .st-key-az_hero::after {
  content: ""; position: absolute; border-radius: 50%; background: rgba(255,255,255,.06); pointer-events: none; }
.hero::before, .st-key-az_hero::before { width: 320px; height: 320px; top: -140px; left: -80px; }
.hero::after, .st-key-az_hero::after { width: 420px; height: 420px; bottom: -260px; right: -120px; background: rgba(233,215,174,.10); }
.hero .badge, .hero-copy .badge { display: inline-block; padding: .3rem .9rem; border-radius: 999px; background: rgba(255,255,255,.14);
  border: 1px solid rgba(255,255,255,.25); font-size: .78rem; letter-spacing: .08em; text-transform: uppercase; font-weight: 600; color: #fff; }
.hero h1 { color: #fff; font-size: 2.9rem; font-weight: 700; margin: .7rem 0 .4rem; letter-spacing: -.02em; line-height: 1.1; padding: 0; }
.hero h1 span, .hero-copy h1 span { color: #E9C46A; }
.hero p { color: rgba(255,255,255,.85); font-size: 1.05rem; margin: 0 auto; max-width: 760px; }
.st-key-az_hero, .st-key-az_cta { text-align: left; }
.st-key-az_hero { padding: 2.1rem 2.3rem 1.9rem; margin-bottom: 0; }
.st-key-az_cta { padding: 1.6rem 1.9rem; margin: 2.2rem 0 0; }
.hero .chips { margin-top: 1.1rem; display: flex; gap: .6rem; justify-content: center; flex-wrap: wrap; }
.hero .chip { background: rgba(255,255,255,.12); border-radius: 10px; padding: .45rem .8rem; font-size: .85rem; border: 1px solid rgba(255,255,255,.18); }

/* Card - shared by calculator cards and every Analyzer panel */
.st-key-page_calc div[data-testid="stVerticalBlockBorderWrapper"],
.st-key-page_az [class*="st-key-card_"] {
  background: rgba(255,255,255,.94); border-radius: var(--r-lg) !important; border: 1px solid var(--line) !important;
  box-shadow: var(--shadow-card); transition: transform .2s ease, box-shadow .2s ease;
}
.st-key-page_calc div[data-testid="stVerticalBlockBorderWrapper"]:hover,
.st-key-page_az [class*="st-key-card_"]:hover { transform: translateY(-3px); box-shadow: var(--shadow-card-hover); }
.loan-head { display: flex; align-items: center; gap: .7rem; margin-bottom: .4rem; }
.loan-head .ico { width: 44px; height: 44px; border-radius: 12px; display: grid; place-items: center; font-size: 1.4rem; }
.loan-head h3 { margin: 0; padding: 0; font-size: 1.2rem; font-weight: 700; color: #0F172A; }
.loan-head small { color: #64748B; font-size: .78rem; }
.emi-box { border-radius: 14px; padding: 1rem 1.1rem; margin: .6rem 0 .8rem; color: #fff; }
.emi-box .lbl { font-size: .78rem; opacity: .85; text-transform: uppercase; letter-spacing: .06em; }
.emi-box .val { font-size: 1.9rem; font-weight: 800; letter-spacing: -.01em; font-variant-numeric: tabular-nums; }
.stats { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: .5rem; margin-bottom: 1rem; }
.stat { background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 10px; padding: .55rem .6rem; }
.stat .lbl { font-size: .68rem; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.stat .val { font-size: .9rem; font-weight: 700; color: #0F172A; }
.section-title { display: flex; align-items: center; gap: .6rem; margin: 2rem 0 .8rem; }
.section-title h2 { margin: 0; padding: 0; font-size: 1.5rem; font-weight: 800; color: #0F172A; }
.section-title .bar { width: 6px; height: 28px; border-radius: 4px; background: linear-gradient(#0E7C66, #A8823F); }
.section-title .note { margin-left: auto; font-size: .8rem; color: var(--mist); }
.ov-head .section-title { margin: 0; }
.st-key-page_calc .stTabs [data-baseweb="tab-list"] { gap: .4rem; background: #fff; padding: .35rem; border-radius: 14px;
  border: 1px solid #E2E8F0; width: fit-content; max-width: 100%; overflow-x: auto; }
.st-key-page_calc .stTabs [data-baseweb="tab"] { border-radius: 10px; padding: .45rem 1.1rem; font-weight: 600; }
.st-key-page_calc .stTabs [aria-selected="true"] { background: #0B1F3A !important; color: #fff !important; }
.st-key-page_calc .stTabs [data-baseweb="tab-highlight"], .st-key-page_calc .stTabs [data-baseweb="tab-border"] { display: none; }
.summary-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: .8rem; margin: 1rem 0; }
.summary-row .card { background: #fff; border: 1px solid #E2E8F0; border-radius: 14px; padding: .9rem 1rem; box-shadow: 0 6px 18px -12px rgba(15,23,42,.25); }
.summary-row .lbl { font-size: .72rem; color: #64748B; text-transform: uppercase; letter-spacing: .05em; }
.summary-row .val { font-size: 1.25rem; font-weight: 800; color: #0F172A; font-variant-numeric: tabular-nums; }
.st-key-page_calc [data-testid="stDataFrame"] { border-radius: 14px; overflow: hidden; border: 1px solid #E2E8F0; }
.footer { text-align: center; color: #94A3B8; font-size: .8rem; margin: 2.5rem 0 1rem; }

/* =================== responsive =================== */
@media (max-width: 1024px) {
  .insights-grid { grid-template-columns: 1fr 1fr; }
  .hero h1 { font-size: 2.3rem; }
  .summary-row { grid-template-columns: repeat(2, 1fr); }
  .hero-metric .v { font-size: 1.6rem; }
}
@media (max-width: 760px) {
  .block-container { padding-left: .9rem; padding-right: .9rem; }
  .st-key-appbar_actions [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; gap: .5rem; }
  .st-key-appbar_actions [data-testid="stColumn"] { width: auto !important; flex: 1 1 0 !important; min-width: 0 !important; }
  .st-key-appbar button { min-height: 2.2rem; font-size: .82rem; }
  .st-key-appbar { margin-bottom: 1rem; }
  .st-key-module [data-testid="stButtonGroup"] { width: 100%; }
  .st-key-module button { flex: 1; padding: .5rem .4rem !important; font-size: .86rem; }
  .hero-copy h1 { font-size: 1.6rem; }
  .st-key-az_hero, .st-key-az_cta { padding: 1.4rem 1.2rem; border-radius: 16px; }
  .section-title .note { display: none; }
  .hero-copy p { font-size: .9rem; }
  .trust { border-left: none; padding-left: 0; border-top: 1px solid rgba(255,255,255,.14); padding-top: .9rem; }
  .hero-metrics { grid-template-columns: 1fr; }
  .hero-metric { border-right: none; border-bottom: 1px solid var(--line); padding: .9rem 1rem; }
  .hero-metric:last-child { border-bottom: none; }
  .hero-metric .v { font-size: 1.5rem; }
  .sec-metrics { grid-template-columns: 1fr 1fr; row-gap: .9rem; }
  .metric { padding: .1rem .7rem; }
  .metric:nth-child(3) { border-left: none; padding-left: .2rem; }
  .insights-grid { grid-template-columns: 1fr; }
  .st-key-card_overview { padding: 1.1rem 1rem 1rem !important; }
  .slide { grid-template-columns: 44px 1fr; }
  .slide .ico { width: 44px; height: 44px; }
  .hero { padding: 1.6rem 1rem 1.4rem; border-radius: 16px; }
  .hero h1 { font-size: 1.75rem; }
  .hero p { font-size: .92rem; }
  .summary-row { grid-template-columns: 1fr 1fr; }
  .summary-row .val { font-size: 1.02rem; }
  .emi-box .val { font-size: 1.5rem; }
  .st-key-page_calc div[data-testid="stVerticalBlockBorderWrapper"]:hover,
  .st-key-page_az [class*="st-key-card_"]:hover { transform: none; }
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
