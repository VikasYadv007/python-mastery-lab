"""Python Mastery Lab: Python Glass design system.

Only frontend CSS and self-contained SVG assets live here. No remote styles,
fonts, scripts, user data or browser state. Used by app.py in both modes.
"""

from __future__ import annotations

import urllib.parse

ICON_PATHS = {
    "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10Z"/><path d="M9 21v-7h6v7"/>',
    "quiz": '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 2.5 2.5L16 9"/>',
    "coding": '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/>',
    "review": '<path d="M3 12a9 9 0 1 0 2.8-6.5L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
    "progress": '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
    "packs": '<path d="M4 19V5a2 2 0 0 1 2-2h5a3 3 0 0 1 3 3v15a3 3 0 0 0-3-3H6a2 2 0 0 0-2 2"/><path d="M20 19V5a2 2 0 0 0-2-2h-5a3 3 0 0 0-2 3v15a3 3 0 0 1 3-3h4a2 2 0 0 1 2 2"/>',
    "star": '<path d="m12 2 3.1 6.3 7 1-5 4.9 1.2 6.9-6.3-3.3-6.3 3.3 1.2-6.9-5-4.9 7-1L12 2Z"/>',
    "menu": '<path d="M4 6h16M4 12h16M4 18h16"/>',
    "moon": '<path d="M20.2 15A8.5 8.5 0 0 1 9 3.8 8.5 8.5 0 1 0 20.2 15Z"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
    "arrow": '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    "check": '<path d="m5 12 5 5L20 7"/>',
    "spark": '<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/>',
}


def svg_icon(name: str, size: int = 20, color: str = "currentColor", class_name: str = "") -> str:
    if name not in ICON_PATHS:
        raise ValueError(name)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="{class_name}" aria-hidden="true"'
        f' width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}"'
        f' stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">'
        f"{ICON_PATHS[name]}</svg>"
    )


def svg_css(name: str, color: str = "#64748b") -> str:
    return "data:image/svg+xml," + urllib.parse.quote(svg_icon(name, color=color), safe="")


def python_mark(size: int = 40) -> str:
    """Local vector mark using the familiar interlocking blue and gold motif."""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
        'viewBox="0 0 64 64" aria-hidden="true">'
        '<path fill="#3776ab" d="M31 4C18 4 18 9 18 9v10h14v3H12S4 21 4 34s8 13 8 13h6V36s0-8 8-8h15s7 0 7-7V11s1-7-17-7Z"/>'
        '<path fill="#ffd343" d="M33 60c13 0 13-5 13-5V45H32v-3h20s8 1 8-12-8-13-8-13h-6v11s0 8-8 8H23s-7 0-7 7v10s-1 7 17 7Z"/>'
        '<circle cx="25" cy="12" r="2.5" fill="#fff"/>'
        '<circle cx="39" cy="52" r="2.5" fill="#fff"/></svg>'
    )


# Semantic colors, translucent surfaces, and solid accessibility fallbacks.
THEMES = {
    "light": {
        "--surface-2": "#ffffffa6",
        "--surface-3": "#e0ebf3",
        "--bg": "#f0f4f6",
        "--surface": "#f9fbfd",
        "--text": "#172e42",
        "--muted": "#465f72",
        "--subtle": "#536c7e",
        "--border": "#ffffffb8",
        "--border-strong": "#b6cbd9",
        "--accent": "#3776ab",
        "--accent-solid": "#306c9e",
        "--accent-hover": "#24567f",
        "--accent-soft": "#3776ab14",
        "--accent-stroke": "#6498bd",
        "--accent-text": "#265f8b",
        "--success-bg": "#e7f8f0",
        "--success-text": "#086344",
        "--success-border": "#82cbae",
        "--wrong-bg": "#fff0f1",
        "--wrong-text": "#99263a",
        "--wrong-border": "#eba0ae",
        "--shadow": "#193c6310",
        "--shadow-deep": "#193c631c",
        "--code-bg": "#f1f6f9",
        "--gold": "#ffd343",
        "--gold-soft": "#fff4cc",
        "--gold-text": "#795708",
        "--gold-border": "#dbbd60",
        "--glass": "linear-gradient(140deg,#ffffffc9,#ffffff79)",
        "--edge": "#ffffffdc",
        "--blue-glow": "#74afd34a",
        "--gold-glow": "#ffd3433b",
        "--grid": "#3776ab06",
        "--panel-shadow": "0 8px 32px #1c496e0b",
        "--hero-tint": "#d8eaf06b",
        "--editor-bg": "#f7fbfcd9",
        "--input-bg": "#ffffffad",
        "--string": "#397550",
    },
    "dark": {
        "--surface-2": "#243c4e8c",
        "--surface-3": "#2c465a",
        "--bg": "#0b1620",
        "--surface": "#172b3b",
        "--text": "#edf5fa",
        "--muted": "#bccdd9",
        "--subtle": "#a0b7c8",
        "--border": "#9ec7e025",
        "--border-strong": "#4e6c82",
        "--accent": "#74b6e2",
        "--accent-solid": "#326f9e",
        "--accent-hover": "#23567c",
        "--accent-soft": "#74b6e21c",
        "--accent-stroke": "#619ec7",
        "--accent-text": "#a1d5f7",
        "--success-bg": "#15382f",
        "--success-text": "#99edd0",
        "--success-border": "#418971",
        "--wrong-bg": "#452730",
        "--wrong-text": "#ffbac5",
        "--wrong-border": "#b45e73",
        "--shadow": "#00000020",
        "--shadow-deep": "#00000040",
        "--code-bg": "#0c1e2b",
        "--gold": "#ffd343",
        "--gold-soft": "#ffd34318",
        "--gold-text": "#ffe391",
        "--gold-border": "#d2b95d70",
        "--glass": "linear-gradient(140deg,#233c50ba,#152837a6)",
        "--edge": "#c4e8ff14",
        "--blue-glow": "#2e79ab36",
        "--gold-glow": "#b98a1920",
        "--grid": "#b9e0f605",
        "--panel-shadow": "0 10px 34px #00000020",
        "--hero-tint": "#3776ab22",
        "--editor-bg": "#0d1d2bd9",
        "--input-bg": "#102331b8",
        "--string": "#a8d6a9",
    },
}

CSS = r"""
/* Python Glass — a shared visual system for every workspace page. */
:root { __THEME_VARS__ color-scheme: __COLOR_SCHEME__; }
*,*::before,*::after{box-sizing:border-box;}
html{scroll-behavior:smooth;scrollbar-gutter:stable;}
html,body,[data-testid="stApp"]{font-family:"Segoe UI",Inter,system-ui,sans-serif!important;}
[data-testid="stAppViewContainer"]{
 color:var(--text)!important;background-color:var(--bg)!important;
 background-image:radial-gradient(ellipse at 4% 8%,var(--blue-glow),transparent 48%),
 radial-gradient(ellipse at 100% 52%,var(--gold-glow),transparent 48%),
 linear-gradient(var(--grid) 1px,transparent 1px),linear-gradient(90deg,var(--grid) 1px,transparent 1px)!important;
 background-size:auto,auto,48px 48px,48px 48px!important;background-attachment:fixed!important;
}
[data-testid="stMain"],[data-testid="stMainBlockContainer"]{min-width:0;color:var(--text);}
[data-testid="stHeader"]{background:transparent!important;height:38px!important;}
[data-testid="stHeader"] button{color:var(--text)!important;}
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stSidebarHeader"]{display:none!important;}
footer{visibility:hidden;}
.block-container,[data-testid="stMainBlockContainer"]{max-width:1200px!important;padding:3rem 28px 4rem!important;margin-inline:auto!important;}
[data-testid="stMain"] [data-testid="stVerticalBlock"]{gap:1rem;}
[data-testid="stColumn"],[data-testid="stHorizontalBlock"],[data-testid="stElementContainer"]{min-width:0;}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3{color:var(--text)!important;letter-spacing:-.035em;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p{color:var(--muted);line-height:1.7;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] strong{color:var(--text);}
[data-testid="stMain"] a{color:var(--accent-text)!important;text-underline-offset:4px;}
[data-testid="stMain"] a:hover{text-decoration-thickness:2px;}
[data-testid="stCaptionContainer"] p{color:var(--subtle)!important;font-size:.8rem;line-height:1.6;}
[data-testid="stMain"] hr{border-color:var(--border)!important;margin:1rem 0!important;}
/* Glass is applied once per surface; controls stay crisp and inexpensive to draw. */
.st-key-site_header,.hero,[data-testid="stMetric"],[data-testid="stForm"],
[data-testid="stExpander"],[data-testid="stVerticalBlockBorderWrapper"],
[data-testid="stLayoutWrapper"] > [data-testid="stVerticalBlock"][style*="border"],
.review-item,.topic-row,.table-scroll,.empty,.lead-strip{
 background:var(--glass)!important;border:1px solid var(--border)!important;
 box-shadow:var(--panel-shadow),inset 0 1px 0 var(--edge)!important;
 backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
}
.st-key-site_header{border-radius:24px!important;padding:17px 22px 12px!important;margin-bottom:12px;}
.st-key-site_header{gap:0!important;}
/* DOM order and visual order: brand, appearance, account (at the far right). */
.st-key-site_header > [data-testid="stLayoutWrapper"]:first-child > [data-testid="stHorizontalBlock"]{
 display:grid!important;grid-template-columns:minmax(0,1fr) 44px minmax(110px,195px)!important;
 align-items:center!important;gap:12px!important;
}
.st-key-site_header > [data-testid="stLayoutWrapper"]:first-child > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
 width:100%!important;min-width:0!important;}
.site-brand{display:flex;align-items:center;gap:12px;min-width:0;}
.site-brand-icon{width:48px;height:48px;border-radius:15px;display:grid;place-items:center;flex:none;
 background:var(--surface-2);border:1px solid var(--border);box-shadow:inset 0 1px var(--edge);}
.site-brand-text{display:flex;flex-direction:column;gap:3px;min-width:0;}
.site-brand-text b{color:var(--text);font-size:1.12rem;font-weight:800;letter-spacing:-.04em;line-height:1.2;}
.site-brand-text small{color:var(--subtle);font:600 .59rem/1.5 Consolas,monospace;letter-spacing:.16em;}
.visitor-note{color:var(--muted);font-size:.8rem;text-align:right;}
.st-key-site_header [data-testid="stPopover"]{display:flex;justify-content:flex-end;width:100%;}
.st-key-site_header [data-testid="stPopover"] button{
 width:100%!important;min-height:44px!important;border-radius:14px!important;
 background:var(--surface-2)!important;padding:9px 13px!important;
}
.st-key-site_header [data-testid="stPopover"] button p{overflow:hidden;text-overflow:ellipsis;white-space:nowrap!important;}
.st-key-site_header [data-testid="stPopover"] > div,
.st-key-site_header [data-testid="stPopover"] [data-testid="stTooltipIcon"],
.st-key-site_header [data-testid="stPopover"] [data-testid="stTooltipHoverTarget"]{width:100%!important;}
.account-popover-title{font-size:.9rem;color:var(--muted);padding:4px 0 12px;overflow-wrap:anywhere;}
.account-popover-title b{color:var(--text);}
/* Accessible text is retained while the theme control displays a local SVG. */
[data-testid="stMain"] .st-key-theme_circle button{
 width:44px!important;min-width:44px!important;height:44px!important;padding:0!important;
 border-radius:14px!important;position:relative;background:var(--surface-2)!important;
 color:var(--text)!important;box-shadow:none!important;
}
.st-key-theme_circle button::before{content:"";position:absolute;width:20px;height:20px;
 left:50%;top:50%;transform:translate(-50%,-50%);background:var(--theme-icon) center/contain no-repeat;pointer-events:none;}
.st-key-theme_circle button p{position:absolute!important;width:1px!important;height:1px!important;
 padding:0!important;overflow:hidden!important;clip-path:inset(50%)!important;white-space:nowrap!important;}
.st-key-top_navigation{border-top:1px solid var(--border);margin-top:15px;padding-top:11px;}
.st-key-top_navigation [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:nowrap!important;gap:6px!important;}
.st-key-top_navigation [data-testid="stColumn"]{flex:1 1 0!important;width:auto!important;}
[data-testid="stMain"] .st-key-top_navigation .stButton button{
 width:100%!important;min-height:43px!important;border-radius:12px!important;border:1px solid transparent!important;
 background:transparent!important;color:var(--muted)!important;box-shadow:none!important;padding:10px!important;white-space:nowrap!important;
}
[data-testid="stMain"] .st-key-top_navigation .stButton button:hover{background:var(--surface-2)!important;color:var(--text)!important;}
[data-testid="stMain"] .st-key-top_navigation .stButton button[kind="primary"]{
 background:var(--accent-soft)!important;color:var(--accent-text)!important;border-color:var(--accent-stroke)!important;
 box-shadow:inset 0 -2px 0 var(--gold)!important;}
[data-testid="stMain"] .st-key-top_navigation .stButton button p{color:inherit!important;-webkit-text-fill-color:currentColor!important;font-size:.84rem!important;}
/* A Python-inspired editorial hero shared by all six pages and account screens. */
.hero{position:relative;display:grid;grid-template-columns:minmax(0,1fr) 310px;align-items:center;gap:32px;
 overflow:hidden;border-radius:28px;padding:34px 36px;margin-bottom:7px;isolation:isolate;}
.hero::before{content:"";position:absolute;inset:0;background:linear-gradient(115deg,var(--hero-tint),transparent 65%);z-index:-1;}
.hero::after{content:"";position:absolute;top:0;left:36px;right:36px;height:3px;
 background:linear-gradient(90deg,#3776ab 0%,#4d9cd0 45%,#ffd343 100%);border-radius:0 0 4px 4px;}
.eyebrow{display:flex;align-items:center;gap:8px;color:var(--accent-text);font:700 .65rem/1.6 Consolas,monospace;
 letter-spacing:.12em;text-transform:uppercase;}
.eyebrow::before{content:"";width:6px;height:6px;background:var(--gold);border-radius:50%;flex:none;}
.hero h1{font-size:clamp(1.85rem,3.1vw,2.65rem)!important;line-height:1.13!important;font-weight:800!important;
 letter-spacing:-.055em!important;margin:14px 0!important;padding:0!important;max-width:660px;}
.hero p{font-size:.92rem!important;color:var(--muted)!important;line-height:1.7!important;margin:0!important;max-width:600px;}
.hero-signature{display:flex;align-items:center;gap:8px;color:var(--subtle);font-size:.72rem;margin-top:21px;}
.status-dot{width:6px;height:6px;border-radius:50%;background:var(--accent);box-shadow:0 0 0 4px var(--accent-soft);}
.hero-code{border:1px solid var(--border-strong);border-radius:18px;background:var(--editor-bg);box-shadow:0 16px 38px var(--shadow-deep);transform:rotate(-2deg);overflow:hidden;}
.editor-bar{display:flex;align-items:center;gap:5px;padding:13px 14px;border-bottom:1px solid var(--border);}
.editor-bar > span{width:6px;height:6px;border-radius:50%;background:#e99283;}
.editor-bar > span:nth-child(2){background:#e6bd5f;}.editor-bar > span:nth-child(3){background:#7eb6a1;}
.editor-bar small{margin-left:auto;color:var(--subtle);font: .6rem Consolas,monospace;}
.editor-body{padding:16px 14px;color:var(--text);font:.67rem/2.1 Consolas,monospace;white-space:nowrap;}
.editor-body i{font-style:normal;color:var(--subtle);margin-right:14px;opacity:.7;}
.syntax-comment{color:var(--subtle);}.syntax-string{color:var(--string);}.syntax-keyword{color:var(--accent-text);}.syntax-function{color:var(--gold-text);}
.editor-footer{display:flex;align-items:center;gap:7px;border-top:1px solid var(--border);padding:10px 14px;color:var(--subtle);font-size:.6rem;}
[data-testid="stMain"] h2.section-title{font-size:1.17rem!important;letter-spacing:-.035em;margin:24px 0 5px!important;padding:0!important;font-weight:750;}
.section-sub{font-size:.86rem;color:var(--muted);line-height:1.65;margin:0 0 10px;}
/* Native controls, including forms, downloads, account popovers, and uploads. */
[data-testid="stMain"] :is(.stButton,.stFormSubmitButton,.stDownloadButton) button,
[data-testid="stPopover"] button{
 min-height:44px;border:1px solid var(--border-strong)!important;border-radius:12px!important;
 background:var(--surface-2)!important;color:var(--text)!important;padding:10px 17px!important;
 box-shadow:inset 0 1px 0 var(--edge)!important;max-width:100%;width:auto;white-space:normal!important;
 font-size:.85rem!important;font-weight:650!important;line-height:1.4!important;
 transition:background .18s ease,border-color .18s ease,box-shadow .18s ease!important;
}
[data-testid="stMain"] :is(.stButton,.stFormSubmitButton,.stDownloadButton) button:hover{background:var(--surface-3)!important;border-color:var(--accent-stroke)!important;box-shadow:0 4px 14px var(--shadow-deep)!important;}
[data-testid="stMain"] :is(.stButton,.stFormSubmitButton) button[kind="primary"]{
 background:linear-gradient(135deg,var(--accent-solid),var(--accent-hover))!important;
 border-color:var(--accent-solid)!important;color:#fff!important;box-shadow:0 5px 16px var(--blue-glow)!important;}
[data-testid="stMain"] :is(.stButton,.stFormSubmitButton) button[kind="primary"] p{color:inherit!important;-webkit-text-fill-color:currentColor!important;}
[data-testid="stMain"] button:disabled{opacity:.45!important;cursor:not-allowed!important;box-shadow:none!important;}
[data-testid="stMain"] :is(button,input,textarea,summary,a):focus-visible,.table-scroll:focus-visible,
[data-testid="stRadio"] label:has(input:focus-visible){outline:3px solid var(--accent-stroke)!important;outline-offset:3px;}
[data-baseweb="select"]:focus-within{outline:2px solid var(--accent-stroke);outline-offset:2px;border-radius:12px;}
[data-testid="stWidgetLabel"] p{color:var(--muted)!important;font-size:.81rem!important;font-weight:650!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input,
[data-testid="stSelectbox"] [data-baseweb="select"] > div,[data-testid="stMultiSelect"] [data-baseweb="select"] > div{
 background:var(--input-bg)!important;color:var(--text)!important;border:1px solid var(--border-strong)!important;
 border-radius:12px!important;min-height:44px;box-shadow:inset 0 1px 3px var(--shadow)!important;}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{color:var(--subtle)!important;opacity:1;}
[data-testid="stTextArea"] textarea{line-height:1.7;}
[data-testid="stTextArea"] textarea[aria-label="Your Python code"]{font-family:Consolas,"Cascadia Code",monospace!important;font-size:.9rem;tab-size:4;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,[data-testid="stMultiSelect"] [data-baseweb="select"] *{color:var(--text)!important;}
[data-testid="stMultiSelect"] [data-baseweb="tag"]{background:var(--accent-soft)!important;}
[data-baseweb="popover"],[data-baseweb="menu"],[data-testid="stPopoverBody"]{background:var(--surface)!important;color:var(--text)!important;border-color:var(--border)!important;border-radius:16px!important;}
[data-baseweb="popover"] [role="option"]{color:var(--text)!important;}
[data-baseweb="popover"] [role="option"]:hover,[data-baseweb="popover"] [aria-selected="true"]{background:var(--accent-soft)!important;}
[data-testid="stNumberInput"] button{background:var(--surface-2)!important;color:var(--text)!important;}
[data-testid="stForm"]{border-radius:22px!important;padding:22px!important;}
[data-testid="stExpander"]{border-radius:18px!important;overflow:hidden;}
[data-testid="stExpander"] summary{padding:13px 17px!important;color:var(--text)!important;background:transparent!important;}
[data-testid="stExpander"] summary:hover{background:var(--surface-2)!important;}
[data-testid="stExpander"] summary p{color:var(--text)!important;font-size:.87rem;font-weight:650;}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:22px!important;}
[data-testid="stMetric"]{padding:20px!important;border-radius:20px!important;border-top:3px solid var(--accent-stroke)!important;}
[data-testid="stColumn"]:nth-child(even) [data-testid="stMetric"]{border-top-color:var(--gold)!important;}
[data-testid="stMetricLabel"] p{font-size:.76rem!important;color:var(--muted)!important;font-weight:650!important;}
[data-testid="stMetricValue"]{font-size:2.1rem!important;font-weight:750!important;letter-spacing:-.045em;color:var(--text)!important;}
[data-testid="stTabs"] :is([data-baseweb="tab-list"],[role="tablist"]){gap:8px;overflow-x:auto;border-bottom:1px solid var(--border);padding:5px 0 8px;}
[data-testid="stTabs"] :is([data-baseweb="tab"],[role="tab"]){color:var(--muted)!important;border-radius:10px;padding:10px 16px!important;font-size:.85rem;min-height:44px;}
[data-testid="stTabs"] [aria-selected="true"]{color:var(--accent-text)!important;background:var(--accent-soft)!important;}
[data-testid="stTabs"] [data-baseweb="tab-highlight"]{background:var(--gold)!important;}
[data-testid="stCode"] pre{border-radius:16px!important;border:1px solid var(--border)!important;background:var(--code-bg)!important;}
[data-testid="stCode"] code{font-size:.86rem!important;}
[data-testid="stFileUploaderDropzone"]{border-radius:20px!important;background:var(--glass)!important;border:1px dashed var(--accent-stroke)!important;color:var(--text)!important;}
[data-testid="stFileUploaderDropzone"] :is(span,small){color:var(--muted)!important;}
[data-testid="stAlert"]{border-radius:16px!important;}[data-testid="stAlert"] p{color:var(--text)!important;}
[data-testid="stProgress"]{max-width:100%;}[data-testid="stProgress"] [role="progressbar"] > div{background:linear-gradient(90deg,#3776ab,#69a4ca,var(--gold))!important;}
/* Streamlit's React Aria controls (alongside older Base Web selectors above). */
:is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) [data-rac][role="group"]{
 background:var(--input-bg)!important;color:var(--text)!important;border:1px solid var(--border-strong)!important;
 border-radius:12px!important;min-height:44px;box-shadow:inset 0 1px 3px var(--shadow)!important;}
:is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) [data-rac][role="group"]:focus-within{
 outline:2px solid var(--accent-stroke);outline-offset:2px;}
:is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) input[role="combobox"]{
 background:transparent!important;color:var(--text)!important;box-shadow:none!important;}
:is([data-testid="stSelectbox"],[data-testid="stMultiSelect"]) button{background:transparent!important;color:var(--text)!important;}
[data-testid="stSelectboxVirtualDropdown"],[data-testid="stMultiSelectVirtualDropdown"],
[data-rac][role="listbox"]{background:var(--surface)!important;color:var(--text)!important;border-color:var(--border-strong)!important;}
[data-rac][role="option"]{background:transparent!important;color:var(--text)!important;}
[data-rac][role="option"]:is([data-focused="true"],[aria-selected="true"]){background:var(--accent-soft)!important;color:var(--accent-text)!important;}
[data-testid="stNumberInputContainer"]{background:var(--input-bg)!important;border:1px solid var(--border-strong)!important;border-radius:12px!important;overflow:hidden;}
[data-testid="stNumberInputContainer"] input{background:transparent!important;border:0!important;box-shadow:none!important;color:var(--text)!important;}
[data-testid="stNumberInputContainer"] > div{background:transparent!important;}
[data-testid="stNumberInputContainer"] button{background:var(--surface-2)!important;color:var(--text)!important;border:0!important;}
[data-testid="stCode"] :is(pre,code){color:var(--text)!important;}
[data-testid="stCode"] code :is(.token.keyword,.token.operator,.token.boolean){color:var(--accent-text)!important;}
[data-testid="stCode"] code .token.string{color:var(--string)!important;}
[data-testid="stCode"] code :is(.token.number,.token.function){color:var(--gold-text)!important;}
[data-testid="stCode"] code .token.comment{color:var(--subtle)!important;}
[data-testid="stCode"] code .token.punctuation{color:var(--muted)!important;}
[data-testid="stCode"]:focus-visible{outline:3px solid var(--accent-stroke)!important;outline-offset:3px;}
[data-testid="stMarkdownContainer"] :not(pre) > code{background:var(--accent-soft)!important;color:var(--accent-text)!important;}
/* Overview cards and lecture shelves. */
[class*="st-key-feature_"],[class*="st-key-pack_"]{border:1px solid var(--border)!important;border-radius:22px!important;padding:22px!important;background:var(--glass)!important;box-shadow:var(--panel-shadow)!important;}
[class*="st-key-feature_"]{transition:border-color .18s ease,box-shadow .18s ease;}
[class*="st-key-feature_"]:hover{border-color:var(--accent-stroke)!important;box-shadow:0 12px 30px var(--shadow-deep)!important;}
.feature-icon{height:45px;width:45px;display:grid;place-items:center;background:var(--accent-soft);color:var(--accent-text);border:1px solid var(--accent-stroke);border-radius:14px;margin-bottom:16px;}
.st-key-feature_coding .feature-icon{background:var(--gold-soft);color:var(--gold-text);border-color:var(--gold-border);}
.feature-title{color:var(--text);font-size:1.06rem;font-weight:750;letter-spacing:-.025em;margin-bottom:7px;}
.feature-description{color:var(--muted);font-size:.86rem;line-height:1.65;min-height:56px;margin-bottom:10px;}
.lead-strip{border-radius:18px;padding:17px 21px;margin:2px 0 4px;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;}
.lead-strip strong{color:var(--text);font-size:.96rem;}.lead-strip span{color:var(--muted);font-size:.8rem;}
.num-chip,.topic-pill{display:inline-flex;align-items:center;max-width:100%;background:var(--accent-soft);color:var(--accent-text);border:1px solid var(--accent-stroke);border-radius:99px;padding:5px 11px;margin:3px 5px 5px 0;font-size:.71rem;font-weight:600;}
.chip-teal{background:var(--success-bg);color:var(--success-text);border-color:var(--success-border);}
.chip-amber{background:var(--gold-soft);color:var(--gold-text);border-color:var(--gold-border);}
.chip-muted{background:var(--surface-2);color:var(--muted);border-color:var(--border);}
/* Quiz, feedback, revision queues, and analytics share the same surfaces. */
.question-label{color:var(--accent-text);font:700 .72rem/1.6 Consolas,monospace;letter-spacing:.07em;text-transform:uppercase;}
.question-topline{font-size:.8rem;color:var(--muted);margin-top:5px;}
.question-heading{font-size:clamp(1.2rem,2.5vw,1.75rem);line-height:1.45;color:var(--text);font-weight:750;letter-spacing:-.035em;margin:4px 0 12px;}
.st-key-question_intro{background:var(--glass)!important;border:1px solid var(--border)!important;border-radius:22px!important;padding:22px!important;}
.option-title{color:var(--text);font-size:.88rem;font-weight:650;margin-bottom:12px;}
[data-testid="stRadio"] [role="radiogroup"]{gap:10px!important;}
[data-testid="stRadio"] [role="radiogroup"] label{display:flex;align-items:center;gap:10px;border-radius:14px!important;background:var(--surface-2)!important;border:1px solid var(--border-strong)!important;padding:13px 16px!important;min-height:52px!important;transition:border-color .15s,background .15s;}
[data-testid="stRadio"] [role="radiogroup"] label:hover,[data-testid="stRadio"] label:has(input:checked){background:var(--accent-soft)!important;border-color:var(--accent-stroke)!important;}
[data-testid="stRadio"] [role="radiogroup"] label p{color:var(--text)!important;font-size:.93rem;line-height:1.65;}
input[type="radio"],input[type="checkbox"]{accent-color:var(--accent-solid);}
.option-card{display:flex;gap:12px;align-items:flex-start;background:var(--glass);border:1px solid var(--border-strong);border-radius:14px;padding:14px 16px;margin:8px 0;color:var(--text);font-size:.93rem;line-height:1.6;}
.option-card > span:last-child{min-width:0;white-space:pre-wrap;}.option-letter{flex:none;display:grid;place-items:center;width:28px;height:28px;background:var(--surface-3);border-radius:9px;font-size:.8rem;font-weight:700;}
.option-correct{background:var(--success-bg);border-color:var(--success-border);}.option-wrong{background:var(--wrong-bg);border-color:var(--wrong-border);}
.feedback{background:var(--success-bg);border:1px solid var(--success-border);border-left-width:4px;border-radius:16px;padding:17px 20px;margin:14px 0;}
.feedback-bad{background:var(--wrong-bg);border-color:var(--wrong-border);}.feedback strong{color:var(--success-text);}.feedback-bad strong{color:var(--wrong-text);}
.feedback p{color:var(--text)!important;font-size:.89rem;line-height:1.7;margin:6px 0!important;}
.review-item{border-radius:16px;padding:16px 19px;margin:9px 0;}.review-item b{color:var(--text);font-size:.93rem;}.review-item p{color:var(--muted);font-size:.78rem;margin:6px 0 0;}
.topic-row{display:grid;grid-template-columns:minmax(140px,1fr) minmax(80px,1.8fr) 48px;gap:18px;align-items:center;border-radius:13px;padding:13px 16px;margin:8px 0;}
.topic-label{color:var(--text);font-size:.84rem;font-weight:600;}.topic-track{height:8px;background:var(--surface-3);border-radius:99px;overflow:hidden;}.topic-fill{height:100%;background:linear-gradient(90deg,#3776ab,#6daccf);border-radius:99px;}.topic-rate{color:var(--text);text-align:right;font:700 .8rem Consolas,monospace;}
.empty{border-style:dashed!important;border-radius:18px;padding:28px;text-align:center;color:var(--muted);font-size:.9rem;}
.table-scroll{overflow-x:auto;max-width:100%;border-radius:16px;margin:10px 0;}.ui-table{width:100%;border-collapse:collapse;font-size:.84rem;}.ui-table th{background:var(--surface-2);color:var(--text);text-align:left;font-weight:650;padding:13px 16px;white-space:nowrap;}.ui-table td{padding:13px 16px;color:var(--text);border-top:1px solid var(--border);vertical-align:top;}.ui-table pre{white-space:pre-wrap;min-width:130px;margin:0;font-size:.8rem;color:var(--text);}
.hero,.question-heading,.review-item,.option-card,.lead-strip,.topic-label,.num-chip{overflow-wrap:anywhere;}
/* React Aria text editors use a separate surface around the actual input. */
[data-testid="stTextInputRootElement"],[data-testid="stTextAreaRootElement"]{
 background:var(--input-bg)!important;border:1px solid var(--border-strong)!important;
 border-radius:12px!important;box-shadow:inset 0 1px 3px var(--shadow)!important;}
[data-testid="stTextInputRootElement"] > input,[data-testid="stTextAreaRootElement"] > textarea{
 background:transparent!important;border:0!important;box-shadow:none!important;color:var(--text)!important;}
[data-testid="stTextInputRootElement"] > div,[data-testid="stTextInputRootElement"] button{
 background:transparent!important;color:var(--text)!important;}
/* Learning analytics and the revision studio reuse the glass surface tokens. */
[class*="st-key-chart_"],.st-key-progress_filters,.st-key-review_filters,
.st-key-practice_goal,.st-key-mastery_snapshot,.st-key-topic_spotlight,.st-key-review_inspector{
 background:var(--glass)!important;border:1px solid var(--border)!important;border-radius:22px!important;
 padding:22px!important;box-shadow:var(--panel-shadow),inset 0 1px var(--edge)!important;
}
[data-testid="stMain"] h3.chart-title{font-size:1.08rem!important;line-height:1.4!important;
 letter-spacing:-.025em!important;margin:0 0 6px!important;padding:0!important;font-weight:750;}
[data-testid="stMain"] p.chart-caption{color:var(--muted)!important;font-size:.78rem!important;
 line-height:1.6!important;margin:0 0 16px!important;}
[data-testid="stVegaLiteChart"]{border-radius:12px;min-width:0;}
[data-testid="stVegaLiteChart"] :is(canvas,svg){max-width:100%;}
#vg-tooltip-element{background:var(--surface)!important;color:var(--text)!important;
 border:1px solid var(--border-strong)!important;border-radius:12px!important;
 box-shadow:var(--panel-shadow)!important;font-family:"Segoe UI",sans-serif!important;}
#vg-tooltip-element :is(th,td){color:var(--text)!important;}
.st-key-question_actions_review [data-testid="stHorizontalBlock"]{gap:10px!important;}
@media(max-width:640px){
 [class*="st-key-chart_"],.st-key-progress_filters,.st-key-review_filters,
 .st-key-practice_goal,.st-key-mastery_snapshot,.st-key-topic_spotlight,.st-key-review_inspector{padding:16px!important;}
}
/* The overview is its own small observatory; other pages retain their workspace. */
[data-testid="stAppViewContainer"]:has(.st-key-overview_scene){isolation:isolate;}
[data-testid="stAppViewContainer"]:has(.st-key-overview_scene)::before{
 content:"";position:fixed;inset:-5%;pointer-events:none;z-index:0;
 background:radial-gradient(ellipse at 12% 25%,var(--blue-glow),transparent 50%),radial-gradient(ellipse at 88% 70%,var(--gold-glow),transparent 48%);
 opacity:.4;animation:home-aurora 28s ease-in-out infinite alternate;}
[data-testid="stAppViewContainer"]:has(.st-key-overview_scene) [data-testid="stMain"]{position:relative;z-index:1;}
.st-key-overview_scene{margin:1px 0 12px;}
.st-key-home_mission,.st-key-home_resume,.st-key-home_topic_launchpad{
 background:var(--glass)!important;border:1px solid var(--border)!important;border-radius:22px!important;
 padding:24px!important;box-shadow:var(--panel-shadow),inset 0 1px var(--edge)!important;}
.st-key-home_mission .feature-description,.st-key-home_resume .feature-description{min-height:0!important;margin-bottom:0;}
.home-coverage{position:relative;width:145px;height:145px;margin:10px auto;}
.home-coverage svg{width:100%;height:100%;transform:rotate(-90deg);overflow:visible;}
.home-ring-track,.home-ring-fill{fill:none;stroke-width:8;}.home-ring-track{stroke:var(--surface-3);}
.home-ring-fill{stroke:var(--accent);stroke-linecap:round;stroke-dasharray:339.3;stroke-dashoffset:var(--ring-offset);animation:home-ring 1.2s cubic-bezier(.16,1,.3,1) both;}
.home-coverage > div{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:3px;}
.home-coverage strong{font-size:1.9rem;color:var(--text);font-weight:750;letter-spacing:-.06em;}
.home-coverage span{font: .65rem Consolas,monospace;color:var(--subtle);letter-spacing:.04em;}
.home-topic-chips{margin:10px 0 7px;}.home-topic-facts{display:flex;gap:18px;flex-wrap:wrap;color:var(--muted);font-size:.78rem;line-height:1.7;}
.home-topic-facts b{color:var(--text);font-size:.93rem;}
.home-feature-kicker{font:600 .58rem/1.7 Consolas,monospace;letter-spacing:.1em;color:var(--subtle);margin-bottom:18px;}
.st-key-feature_quiz,.st-key-feature_coding,.st-key-feature_review{animation:home-rise .7s ease both;transition:translate .25s ease,border-color .2s,box-shadow .2s;}
.st-key-feature_coding{animation-delay:.1s;}.st-key-feature_review{animation-delay:.2s;}
.st-key-feature_quiz:hover,.st-key-feature_coding:hover,.st-key-feature_review:hover{translate:0 -5px;}
.st-key-feature_quiz .feature-icon,.st-key-feature_coding .feature-icon,.st-key-feature_review .feature-icon{transition:rotate .25s ease,scale .25s ease;}
.st-key-feature_quiz:hover .feature-icon,.st-key-feature_coding:hover .feature-icon,.st-key-feature_review:hover .feature-icon{rotate:-6deg;scale:1.08;}
.st-key-home_topic_actions [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:wrap!important;gap:10px!important;}
.st-key-home_topic_actions [data-testid="stColumn"]{flex:0 1 auto!important;width:auto!important;min-width:0!important;}
@keyframes home-aurora{from{transform:translate3d(-1%,-1%,0) scale(1);}to{transform:translate3d(2%,2%,0) scale(1.04);}}
@keyframes home-rise{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
@keyframes home-ring{from{stroke-dashoffset:339.3;}to{stroke-dashoffset:var(--ring-offset);}}
@media(max-width:640px){.st-key-home_mission,.st-key-home_resume,.st-key-home_topic_launchpad{padding:19px!important;}.home-coverage{width:125px;height:125px;}.home-topic-facts{gap:12px;}}
@media(prefers-reduced-motion:reduce){[data-testid="stAppViewContainer"]:has(.st-key-overview_scene)::before{animation:none!important;}.home-ring-fill{stroke-dashoffset:var(--ring-offset)!important;}.st-key-feature_quiz:hover,.st-key-feature_coding:hover,.st-key-feature_review:hover{translate:none;}}
[data-testid="stAppViewContainer"]:has(#python-observatory.is-still)::before{animation-play-state:paused;}
/* Preserve closely grouped actions without stretched or overlapping buttons. */
:is(.st-key-quick_actions,.st-key-code_actions,.st-key-question_actions,.st-key-completed_actions,.st-key-grading_actions,.st-key-export_actions) [data-testid="stHorizontalBlock"]{display:flex!important;flex-wrap:wrap!important;gap:10px!important;justify-content:flex-start!important;}
:is(.st-key-quick_actions,.st-key-code_actions,.st-key-question_actions,.st-key-completed_actions,.st-key-grading_actions,.st-key-export_actions) [data-testid="stColumn"]{flex:0 1 auto!important;width:auto!important;min-width:0!important;}
@media(max-width:900px){.hero{grid-template-columns:1fr;padding:29px;}.hero-code{display:none;}.hero h1{max-width:700px;}.st-key-site_header{padding:16px;}.block-container,[data-testid="stMainBlockContainer"]{padding-inline:20px!important;}}
@media(max-width:640px){
 .block-container,[data-testid="stMainBlockContainer"]{padding:2.8rem 12px 3rem!important;}
 .st-key-site_header{border-radius:20px!important;padding:13px!important;}
 .st-key-site_header > [data-testid="stLayoutWrapper"]:first-child > [data-testid="stHorizontalBlock"]{grid-template-columns:minmax(0,1fr) 44px minmax(90px,125px)!important;gap:7px!important;}
 .site-brand{gap:7px;}.site-brand-icon{width:34px;height:38px;border-radius:10px;}.site-brand-icon svg{width:29px;height:29px;}.site-brand-text b{font-size:.85rem;}.site-brand-text small{display:none;}
 .st-key-site_header [data-testid="stPopover"] button{padding:8px!important;}.st-key-site_header [data-testid="stPopover"] button p{font-size:.72rem!important;}
 .st-key-top_navigation [data-testid="stHorizontalBlock"]{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:5px!important;}
 [data-testid="stMain"] .st-key-top_navigation .stButton button{font-size:.78rem!important;padding:9px 5px!important;white-space:normal!important;}
 .hero{padding:24px 21px;border-radius:22px;gap:0;}.hero::after{left:21px;right:21px;}.hero h1{font-size:1.9rem!important;}.hero p{font-size:.86rem!important;}.hero-signature{font-size:.65rem;}.eyebrow{font-size:.58rem;}
 [data-testid="stMain"] h2.section-title{font-size:1.08rem!important;}
 [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]){display:flex!important;flex-wrap:wrap!important;gap:10px!important;}
 [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"]{flex:1 1 calc(50% - 5px)!important;width:calc(50% - 5px)!important;}
 [data-testid="stMetric"]{padding:15px!important;border-radius:16px!important;}[data-testid="stMetricValue"]{font-size:1.7rem!important;}
 [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,[data-testid="stNumberInput"] input{font-size:16px!important;}
 [data-testid="stForm"],.st-key-question_intro{padding:16px!important;}
 [class*="st-key-feature_"],[class*="st-key-pack_"]{padding:18px!important;}.feature-description{min-height:0;}
 .topic-row{grid-template-columns:minmax(90px,1fr) minmax(55px,1fr) 38px;gap:9px;padding:12px;}
 .lead-strip{padding:15px;}.visitor-note{font-size:.65rem;}
}
@supports not (backdrop-filter:blur(1px)){
 .hero,.st-key-site_header,[data-testid="stForm"],[data-testid="stMetric"],.review-item,.topic-row{background:var(--surface)!important;}
}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important;}.hero-code{transform:none;}}
@media(prefers-reduced-transparency:reduce){.hero,.st-key-site_header,[data-testid="stForm"],[data-testid="stMetric"],.review-item,.topic-row,.lead-strip{background:var(--surface)!important;backdrop-filter:none!important;}}
"""


def style(theme: str) -> str:
    """Return light/dark tokenized CSS, including a real SVG for the toggle."""
    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")
    vars_ = dict(THEMES[theme])
    vars_["--theme-icon"] = (
        f'url("{svg_css("sun" if theme == "dark" else "moon", vars_["--text"])}")'
    )
    blob = ";".join(f"{key}:{value}" for key, value in vars_.items()) + ";"
    return (
        "<style>"
        + CSS.replace("__THEME_VARS__", blob).replace("__COLOR_SCHEME__", theme)
        + "</style>"
    )
