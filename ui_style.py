from __future__ import annotations
import urllib.parse

ICON_PATHS = {
 'home':'<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10Z"/><path d="M9 21v-7h6v7"/>',
 'quiz':'<rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 2.5 2.5L16 9"/>',
 'coding':'<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/>',
 'review':'<path d="M3 12a9 9 0 1 0 2.8-6.5L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
 'progress':'<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
 'packs':'<path d="M4 19V5a2 2 0 0 1 2-2h5a3 3 0 0 1 3 3v15a3 3 0 0 0-3-3H6a2 2 0 0 0-2 2"/><path d="M20 19V5a2 2 0 0 0-2-2h-5a3 3 0 0 0-2 3v15a3 3 0 0 1 3-3h4a2 2 0 0 1 2 2"/>',
 'star':'<path d="m12 2 3.1 6.3 7 1-5 4.9 1.2 6.9-6.3-3.3-6.3 3.3 1.2-6.9-5-4.9 7-1L12 2Z"/>',
 'menu':'<path d="M4 6h16M4 12h16M4 18h16"/>',
 'moon':'<path d="M20.2 15A8.5 8.5 0 0 1 9 3.8 8.5 8.5 0 1 0 20.2 15Z"/>',
 'sun':'<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
 'arrow':'<path d="M4 12h16m-6-6 6 6-6 6"/>',
 'check':'<path d="m5 12 5 5L20 7"/>',
 'spark':'<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/>',
}

def svg_icon(name:str, size:int=20, color:str='currentColor', class_name:str='') -> str:
    if name not in ICON_PATHS:
        raise ValueError(name)
    # Only use constant locally-authored SVG path contents, no external assets/fonts.
    return f'<svg xmlns="http://www.w3.org/2000/svg" class="{class_name}" aria-hidden="true" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">{ICON_PATHS[name]}</svg>'

def svg_css(name:str, color:str='#64748b') -> str:
    svg=svg_icon(name, color=color)
    return 'data:image/svg+xml,'+urllib.parse.quote(svg, safe='')

THEMES = {
 'light': {
 '--bg':'#f6f8fd','--bg-radial':'#e6e9ff','--surface':'#ffffff','--surface-2':'#f2f5fc',
 '--text':'#16243e','--muted':'#60718a','--subtle':'#8291a9','--border':'#dde5f0','--border-strong':'#c8d4e5',
 '--accent':'#5c4de3','--accent-deep':'#4735ce','--accent-soft':'#f0edff','--accent-stroke':'#afa4ff',
 '--success-bg':'#e9faf2','--success-text':'#08764e','--success-border':'#a1e2c5',
 '--wrong-bg':'#fff0ee','--wrong-text':'#b33e3e','--wrong-border':'#f9b8b4',
 '--hero-start':'#ebefff','--hero-mid':'#f5f5ff','--hero-end':'#e3f8f5',
 '--sidebar':'#ffffff','--side-text':'#30415c','--side-muted':'#70819b','--side-hover':'#f2f2ff',
 '--side-border':'#e0e6f2','--sidebar-highlight':'#f5f4ff','--header':'#f6f8fdea',
 '--shadow':'#2c3c650c','--shadow-deep':'#29365b13',
 },
 'dark': {
 '--bg':'#0c1221','--bg-radial':'#25204c','--surface':'#161e31','--surface-2':'#202b42',
 '--text':'#ebf0ff','--muted':'#a3b3cd','--subtle':'#91a0b9','--border':'#2d3951','--border-strong':'#43516d',
 '--accent':'#a397ff','--accent-deep':'#7567ef','--accent-soft':'#252442','--accent-stroke':'#8f80f4',
 '--success-bg':'#16352f','--success-text':'#8de0b9','--success-border':'#2c755a',
 '--wrong-bg':'#38242a','--wrong-text':'#ffc4be','--wrong-border':'#85434d',
 '--hero-start':'#222447','--hero-mid':'#1d2641','--hero-end':'#15363d',
 '--sidebar':'#101829','--side-text':'#e2eafb','--side-muted':'#9fb1cd','--side-hover':'#222c44',
 '--side-border':'#29344c','--sidebar-highlight':'#262346','--header':'#0c1221ed',
 '--shadow':'#00000020','--shadow-deep':'#00000032',
 }
}

CSS = r'''
/* Python Mastery Lab v3 — locally bundled SVGs, no icon font required */
:root { __THEME_VARS__ }
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"] {font-family:Inter,"Segoe UI",system-ui,sans-serif;}
[data-testid="stAppViewContainer"] {color:var(--text);background:radial-gradient(ellipse 65% 35% at 85% -11%,var(--bg-radial),transparent 87%),var(--bg);}
[data-testid="stHeader"] {background:var(--header)!important; backdrop-filter:blur(16px);border-bottom:1px solid var(--border);}
/* Critical: Do NOT hide Streamlit toolbar/header controls. This preserves its collapse/expand sidebar buttons. */
[data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarHeader"] {visibility:visible!important; opacity:1!important;}
[data-testid="stSidebarCollapsedControl"] button,[data-testid="stHeader"] button {color:var(--text)!important;}
[data-testid="stSidebarHeader"] button {color:var(--side-text)!important;}
#MainMenu {visibility:visible;}
footer {visibility:hidden;}
.block-container {max-width:1260px; padding-top:5.1rem!important; padding-bottom:4rem!important;}
.block-container h1,.block-container h2,.block-container h3,.block-container h4 {color:var(--text);letter-spacing:-.035em;}
.block-container h1 {font-size:clamp(1.85rem,3.4vw,2.65rem);line-height:1.16;}
.block-container h2 {font-size:1.43rem;}
[data-testid="stMarkdownContainer"] p {line-height:1.62;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p, [data-testid="stMain"] label p,
[data-testid="stMain"] [data-testid="stCaptionContainer"] p {color:var(--muted);}
[data-testid="stMain"] hr {border-color:var(--border);}
/* Sidebar is intentionally different per mode; native collapse and expand controls remain available. */
[data-testid="stSidebar"] {background:var(--sidebar)!important; border-right:1px solid var(--side-border)!important;}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {padding-top:3.2rem;}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"],[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,[data-testid="stSidebar"] span {color:var(--side-text);}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {color:var(--side-muted);font-weight:700;}
[data-testid="stSidebar"] input {background:var(--surface)!important;color:var(--text)!important;border:1px solid var(--side-border)!important;border-radius:12px!important;}
[data-testid="stSidebar"] .stButton button {display:flex!important;align-items:center!important;gap:12px!important;
 justify-content:flex-start!important;text-align:left!important; width:100%;font-weight:650;
 min-height:48px;border-radius:12px!important;background:transparent;color:var(--side-text)!important;
 border:1px solid transparent!important;box-shadow:none!important;padding:10px 13px!important;transform:none!important;}
[data-testid="stSidebar"] .stButton button:hover {background:var(--side-hover)!important;border-color:var(--side-border)!important;}
[data-testid="stSidebar"] .stButton button[kind="primary"] {background:linear-gradient(105deg,#6355ed,#4c40c9)!important;
 color:#fff!important;border-color:#7a6fff!important;box-shadow:0 6px 17px #5344db2b!important;}
[data-testid="stSidebar"] .stButton button:focus-visible {outline:3px solid var(--accent-stroke)!important;outline-offset:2px!important;}
[data-testid="stSidebar"] hr {border-color:var(--side-border);}
.sidebar-brand {display:flex;align-items:center;gap:12px;padding:5px 0 14px;}
.brand-symbol {width:44px;height:44px;border-radius:14px;flex:none;display:flex;align-items:center;justify-content:center;
 background:linear-gradient(135deg,#6555e8,#22b6b4);box-shadow:0 7px 18px #413d9f26;color:#fff;}
.brand-name {font-size:1.12rem;font-weight:820;color:var(--side-text)!important;letter-spacing:-.045em;}
.brand-caption {font-size:.7rem;color:var(--side-muted)!important;letter-spacing:1.45px;font-weight:800;margin:0 0 8px;}
.side-stats {border:1px solid var(--side-border);border-radius:16px;padding:15px 16px;background:var(--sidebar-highlight);margin-top:10px;}
.side-stats strong {color:var(--side-text);}.side-stats span {color:var(--side-muted);font-size:.82rem;}
.sidebar-small {font-size:.81rem;line-height:1.6;color:var(--side-muted);}
/* Locally encoded SVG icons on nav buttons: renders identically on Windows/macOS/mobile. */
[data-testid="stSidebar"] .stButton button::before {content:"";flex:none;width:19px;height:19px;display:inline-block;
 background:var(--nav-icon) center/contain no-repeat;}
__NAV_ICON_RULES__
[data-testid="stSidebar"] .stButton button[kind="primary"]::before {filter:brightness(0) invert(1);}
/* Header controls: an always-visible navigation popup even when the sidebar is collapsed. */
.topbar {display:flex;flex-direction:column;gap:1px;min-width:0;}
.topbar-overline {text-transform:uppercase;letter-spacing:1.7px;font-size:.69rem;font-weight:820;color:var(--subtle);}
.topbar-title {font-weight:850;line-height:1.35;font-size:1rem;color:var(--text);white-space:normal;}
[data-testid="stMain"] [data-testid="stPopover"] button {background:var(--surface);color:var(--text);border:1px solid var(--border)!important;}
/* Shared interactive control styles */
.stButton button,.stDownloadButton button,.stFormSubmitButton button,
[data-testid="stPopover"] button {min-height:44px;border-radius:12px!important;
 background:var(--surface);color:var(--text);border:1px solid var(--border)!important;
 box-shadow:0 3px 12px var(--shadow);font-weight:670;
 transition:background .17s,border-color .17s,box-shadow .17s,transform .17s;}
.stButton button:hover,.stDownloadButton button:hover,.stFormSubmitButton button:hover,
[data-testid="stPopover"] button:hover {background:var(--surface-2);color:var(--text);
 border-color:var(--accent-stroke)!important;box-shadow:0 6px 18px var(--shadow-deep);transform:translateY(-1px);}
.stButton button[kind="primary"],.stFormSubmitButton button[kind="primary"] {
 background:linear-gradient(105deg,#6255ed,#4639c9)!important;color:#fff!important;border-color:#6b5fea!important;
 box-shadow:0 6px 18px #5541d32d;}
.stButton button[kind="primary"]:hover,.stFormSubmitButton button[kind="primary"]:hover {background:#4f42cf!important;color:#fff!important;}
.stButton button:disabled,.stFormSubmitButton button:disabled {opacity:.5;box-shadow:none;transform:none;cursor:not-allowed;}
.stButton button:focus-visible,.stDownloadButton button:focus-visible,.stFormSubmitButton button:focus-visible,
[data-testid="stPopover"] button:focus-visible {outline:3px solid var(--accent-stroke)!important;outline-offset:2px;}
/* Forms, select menus, checkboxes, radio cards */
[data-testid="stForm"] {background:var(--surface)!important;border:1px solid var(--border)!important;
 border-radius:18px!important;padding:20px!important;box-shadow:0 7px 22px var(--shadow);}
[data-testid="stWidgetLabel"] p {color:var(--muted)!important;font-weight:700;font-size:.87rem;}
[data-testid="stRadio"] div[role="radiogroup"] {gap:9px;}
[data-testid="stRadio"] div[role="radiogroup"] label {background:var(--surface)!important;border:1px solid var(--border)!important;
 min-height:49px;width:100%;border-radius:13px;padding:12px 15px;align-items:center;transition:.18s;}
[data-testid="stRadio"] div[role="radiogroup"] label:hover {background:var(--accent-soft)!important;border-color:var(--accent-stroke)!important;}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {background:var(--accent-soft)!important;
 border-color:var(--accent)!important;box-shadow:inset 0 0 0 1px var(--accent);}
[data-testid="stRadio"] div[role="radiogroup"] label p {color:var(--text)!important;font-size:.97rem;overflow-wrap:anywhere;}
input[type="radio"],input[type="checkbox"] {accent-color:var(--accent-deep)!important;}
[data-testid="stCheckbox"] label {padding:5px 0;}
[data-testid="stCheckbox"] p,[data-testid="stToggle"] p {color:var(--text)!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input {
 border-radius:12px!important;background:var(--surface)!important;color:var(--text)!important;
 border-color:var(--border)!important;}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder {color:var(--subtle);}
[data-testid="stSelectbox"] [data-baseweb="select"] >div,[data-testid="stMultiSelect"] [data-baseweb="select"] >div {
 border-radius:12px!important;background:var(--surface)!important;border-color:var(--border)!important;color:var(--text)!important;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,[data-testid="stMultiSelect"] [data-baseweb="select"] * {color:var(--text);}
[data-testid="stPopoverBody"],[data-baseweb="popover"] {background:var(--surface)!important;color:var(--text)!important;border-color:var(--border)!important;}
[data-baseweb="popover"] [role="listbox"],[data-baseweb="menu"],[data-baseweb="popover"] ul {
 background:var(--surface)!important;color:var(--text)!important;}
[data-baseweb="popover"] [role="option"] {color:var(--text)!important;}
[data-baseweb="popover"] [role="option"]:hover {background:var(--accent-soft)!important;}
[data-testid="stExpander"] {background:var(--surface)!important;border:1px solid var(--border)!important;
 border-radius:15px!important;overflow:hidden;box-shadow:0 3px 12px var(--shadow);}
[data-testid="stExpander"] summary {padding:6px 8px;font-weight:700;color:var(--text)!important;}
[data-testid="stExpander"] summary p {color:var(--text)!important;}
[data-testid="stMetric"] {background:var(--surface)!important;border:1px solid var(--border);
 border-radius:16px;padding:16px 19px;box-shadow:0 7px 24px var(--shadow);}
[data-testid="stMetricLabel"] p {color:var(--muted)!important;}
[data-testid="stMetricValue"] {color:var(--text)!important;letter-spacing:-.045em;}
[data-testid="stProgress"] {margin:.5rem 0 1.2rem;}
[data-testid="stProgress"] [data-testid="stProgressBar"] {border-radius:99px;overflow:hidden;}
[data-testid="stCode"] {border:1px solid var(--border);border-radius:14px;overflow:hidden;}
[data-testid="stAlert"] {border-radius:13px;background:var(--surface-2)!important;color:var(--text)!important;border:1px solid var(--border)!important;}
[data-testid="stAlert"] p {color:var(--text)!important;}
[data-testid="stFileUploaderDropzone"] {background:var(--surface-2)!important;border:1px dashed var(--border-strong)!important;border-radius:14px!important;}
[data-testid="stFileUploaderDropzone"] * {color:var(--text)!important;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] :is(strong,em,li,h4,h5,h6) {color:var(--text);}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] a {color:var(--accent)!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:4px;overflow-x:auto;flex-wrap:nowrap;}
[data-testid="stTabs"] [data-baseweb="tab"] {font-weight:700;color:var(--muted);white-space:nowrap;}
[data-testid="stTabs"] [aria-selected="true"] {color:var(--accent)!important;}
/* Full-theme custom table replaces light-only Streamlit dataframe Canvas */
.table-scroll {max-width:100%;overflow-x:auto;border:1px solid var(--border);border-radius:15px;background:var(--surface);}
.ui-table {width:100%;border-collapse:collapse;min-width:440px;font-size:.88rem;}
.ui-table th {text-align:left;color:var(--muted);font-size:.77rem;letter-spacing:.04em;text-transform:uppercase;
 background:var(--surface-2);padding:13px 14px;border-bottom:1px solid var(--border);}
.ui-table td {padding:12px 14px;border-bottom:1px solid var(--border);color:var(--text);vertical-align:top;overflow-wrap:anywhere;}
.ui-table tr:last-child td {border-bottom:0;}.ui-table code,.ui-table pre {font-family:Consolas,monospace;font-size:.84rem;white-space:pre-wrap;margin:0;color:var(--text);}
/* Visual hierarchy and brand blocks */
.eyebrow {text-transform:uppercase;letter-spacing:1.7px;font-weight:820;font-size:.7rem;color:var(--accent);}
.hero {position:relative;overflow:hidden;border:1px solid var(--border);border-radius:22px;
 background:linear-gradient(105deg,var(--hero-start),var(--hero-mid) 55%,var(--hero-end));
 padding:28px 32px;margin:8px 0 23px;box-shadow:0 13px 32px var(--shadow);}
.hero::before {content:"";pointer-events:none;position:absolute;right:-48px;top:-137px;width:230px;height:230px;
 border:33px solid var(--accent-soft);opacity:.58;border-radius:50%;z-index:0;}
.hero h1,.hero p,.hero .eyebrow {position:relative;z-index:1;}
.hero h1 {margin:7px 0 9px!important;font-size:clamp(1.75rem,3.0vw,2.48rem)!important;line-height:1.19;font-weight:850;color:var(--text)!important;}
.hero p {max-width:760px;font-size:.97rem;margin:0;color:var(--muted)!important;}
.section-title {font-size:1.15rem;font-weight:820;color:var(--text);letter-spacing:-.025em;margin:26px 0 11px;}
.section-sub {color:var(--muted);font-size:.91rem;margin:-6px 0 18px;}
.feature-icon {display:flex;width:44px;height:44px;border-radius:13px;background:var(--accent-soft);
 align-items:center;justify-content:center;color:var(--accent);margin:2px 0 14px;}
.feature-title {color:var(--text);font-size:1.12rem;font-weight:790;margin:3px 0 7px;}
.feature-description {color:var(--muted);line-height:1.65;min-height:66px;font-size:.9rem;}
.lead-strip {background:var(--surface);border:1px solid var(--border);border-radius:18px;
 color:var(--text);padding:20px 24px;display:flex;align-items:center;justify-content:space-between;
 gap:14px;margin-bottom:21px;box-shadow:0 8px 21px var(--shadow);flex-wrap:wrap;}
.lead-strip strong {color:var(--text);font-size:1.08rem;}.lead-strip span {font-size:.85rem;color:var(--muted);}
.num-chip {display:inline-flex;padding:5px 10px;background:var(--accent-soft);color:var(--accent);border-radius:99px;
 margin:0 6px 7px 0;font-size:.74rem;font-weight:760;letter-spacing:.1px;}
.chip-teal {background:var(--success-bg);color:var(--success-text);}.chip-amber {background:var(--surface-2);color:var(--text);}
.chip-muted {background:var(--surface-2);color:var(--muted);}
.question-heading {font-size:clamp(1.5rem,2.65vw,2.15rem);font-weight:820;letter-spacing:-.035em;
 line-height:1.35;color:var(--text);margin:9px 0 15px;overflow-wrap:anywhere;}
.question-label {font-size:.76rem;color:var(--accent);letter-spacing:1.3px;font-weight:800;text-transform:uppercase;}
.question-topline {color:var(--muted);font-size:.89rem;}
.option-card {display:flex;gap:12px;align-items:flex-start;padding:14px 16px;border:1px solid var(--border);
 background:var(--surface);border-radius:13px;margin:8px 0;color:var(--text);line-height:1.6;overflow-wrap:anywhere;}
.option-letter {display:inline-flex;flex-shrink:0;width:29px;height:29px;border-radius:9px;
 background:var(--surface-2);justify-content:center;align-items:center;color:var(--muted);font-size:.85rem;font-weight:800;}
.option-correct {border-color:var(--success-border);background:var(--success-bg);}
.option-correct .option-letter {background:var(--success-border);color:#103c2f;}
.option-wrong {border-color:var(--wrong-border);background:var(--wrong-bg);}
.option-wrong .option-letter {background:var(--wrong-border);color:#361b25;}
.feedback {padding:16px 19px;border:1px solid var(--success-border);border-radius:14px;margin:18px 0;background:var(--success-bg);}
.feedback strong {color:var(--success-text);font-size:1rem;}.feedback p {color:var(--text)!important;line-height:1.7;margin:7px 0 0;}
.feedback-bad {background:var(--wrong-bg);border-color:var(--wrong-border);}
.feedback-bad strong {color:var(--wrong-text);}
.review-item {padding:13px 17px;background:var(--surface);border:1px solid var(--border);border-radius:13px;margin:9px 0;}
.review-item b {color:var(--text);font-size:.94rem;}.review-item p {margin:4px 0 0;font-size:.84rem;color:var(--muted);}
.topic-pill {display:inline-block;background:var(--accent-soft);color:var(--accent);border:1px solid var(--border);
 padding:5px 10px;border-radius:30px;font-size:.78rem;margin:3px 5px 3px 0;font-weight:670;}
.empty {padding:27px;background:var(--surface);text-align:center;border:1px dashed var(--border-strong);
 border-radius:16px;color:var(--muted);}
.small-note {color:var(--subtle);font-size:.84rem;line-height:1.5;}
.topic-row {display:grid;grid-template-columns:minmax(125px,1fr) minmax(160px,2fr) 55px;
 gap:15px;align-items:center;margin:10px 0;padding:12px 15px;background:var(--surface);
 border:1px solid var(--border);border-radius:12px;}
.topic-row .topic-label {font-weight:680;color:var(--text);font-size:.88rem;overflow-wrap:anywhere;}
.topic-track {height:9px;border-radius:99px;background:var(--surface-2);overflow:hidden;}
.topic-fill {height:100%;border-radius:99px;background:linear-gradient(90deg,#6c60f0,#20b6a6);}
.topic-row .topic-rate {text-align:right;font-weight:750;color:var(--text);font-size:.87rem;}
/* Streamlit default container cards, custom color in both modes */
[data-testid="stVerticalBlockBorderWrapper"]:has(> div > [data-testid="stVerticalBlock"]) {border-radius:17px;}
[class*="st-key-feature_"],[class*="st-key-pack_"] {background:var(--surface)!important;border-color:var(--border)!important;border-radius:17px!important;}
@media(max-width:850px) {
 .block-container {padding-left:1.45rem!important;padding-right:1.45rem!important;}
 .hero {padding:23px 24px;}
 .feature-description {min-height:0;}
}
@media(max-width:640px) {
 .block-container {padding-top:4.35rem!important;padding-left:.85rem!important;padding-right:.85rem!important;padding-bottom:2.5rem!important;}
 .hero {padding:22px 19px;border-radius:17px;margin-top:6px;}
 .hero h1 {font-size:1.85rem!important;}
 .lead-strip {padding:16px 18px;}
 .question-heading {font-size:1.52rem;}
 .question-label {font-size:.72rem;}
 [data-testid="stForm"] {padding:14px!important;}
 [data-testid="stMetric"] {padding:12px 14px;}
 [data-testid="stTabs"] [data-baseweb="tab"] {font-size:.86rem;padding:12px 9px;}
 .topic-row {grid-template-columns:minmax(95px,1fr) minmax(100px,1.5fr) 45px;gap:9px;padding:11px;}
 .topbar-title {font-size:.88rem;}
}
@media(prefers-reduced-motion:reduce) {
 .stButton button,.stFormSubmitButton button,[data-testid="stRadio"] label {transition:none!important;transform:none!important;}
}
'''

def style(theme: str) -> str:
    values=THEMES[theme]
    var_blob=';'.join(f'{k}:{v}' for k,v in values.items())+';'
    nav_rules='\n'.join(f'[data-testid="stSidebar"] [class*="st-key-nav_{key}"] button {{--nav-icon:url("{svg_css(key, "#8393b2")}");}}' for key in ('home','quiz','coding','review','progress','packs'))
    return '<style>'+CSS.replace('__THEME_VARS__',var_blob).replace('__NAV_ICON_RULES__',nav_rules)+'</style>'
