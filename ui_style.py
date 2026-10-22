"""Python Mastery Lab: v7 top-navigation design system.

Only frontend CSS and self-contained SVG assets live here. No remote styles,
fonts, scripts, user data or browser state. Used by app.py in both modes.
"""
from __future__ import annotations

import urllib.parse

ICON_PATHS = {
    'home': '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V10Z"/><path d="M9 21v-7h6v7"/>',
    'quiz': '<rect x="3" y="3" width="18" height="18" rx="4"/><path d="m8 12 2.5 2.5L16 9"/>',
    'coding': '<path d="m8 8-4 4 4 4M16 8l4 4-4 4M14 4l-4 16"/>',
    'review': '<path d="M3 12a9 9 0 1 0 2.8-6.5L3 8"/><path d="M3 3v5h5"/><path d="M12 7v5l3 2"/>',
    'progress': '<path d="M3 3v18h18"/><path d="m7 15 4-4 3 3 6-7"/>',
    'packs': '<path d="M4 19V5a2 2 0 0 1 2-2h5a3 3 0 0 1 3 3v15a3 3 0 0 0-3-3H6a2 2 0 0 0-2 2"/><path d="M20 19V5a2 2 0 0 0-2-2h-5a3 3 0 0 0-2 3v15a3 3 0 0 1 3-3h4a2 2 0 0 1 2 2"/>',
    'star': '<path d="m12 2 3.1 6.3 7 1-5 4.9 1.2 6.9-6.3-3.3-6.3 3.3 1.2-6.9-5-4.9 7-1L12 2Z"/>',
    'menu': '<path d="M4 6h16M4 12h16M4 18h16"/>',
    'moon': '<path d="M20.2 15A8.5 8.5 0 0 1 9 3.8 8.5 8.5 0 1 0 20.2 15Z"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.42 1.42m11.3 11.3 1.42 1.42M2 12h2m16 0h2M4.93 19.07l1.42-1.42m11.3-11.3 1.42-1.42"/>',
    'arrow': '<path d="M4 12h16m-6-6 6 6-6 6"/>',
    'check': '<path d="m5 12 5 5L20 7"/>',
    'spark': '<path d="m12 3 1.9 6.1L20 11l-6.1 1.9L12 19l-1.9-6.1L4 11l6.1-1.9L12 3Z"/>',
}


def svg_icon(name: str, size: int = 20, color: str = 'currentColor', class_name: str = '') -> str:
    if name not in ICON_PATHS:
        raise ValueError(name)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" class="{class_name}" aria-hidden="true"'
        f' width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}"'
        f' stroke-width="1.85" stroke-linecap="round" stroke-linejoin="round">'
        f'{ICON_PATHS[name]}</svg>'
    )


def svg_css(name: str, color: str = '#64748b') -> str:
    return 'data:image/svg+xml,' + urllib.parse.quote(svg_icon(name, color=color), safe='')


THEMES = {
    'light': {
        '--bg': '#f4f7fb', '--bg-radial': '#ebf0fb', '--surface': '#ffffff',
        '--surface-2': '#f0f4fa', '--surface-3': '#e5ebf5',
        '--text': '#122037', '--muted': '#4a5d75', '--subtle': '#586d86',
        '--border': '#d6e0ed', '--border-strong': '#b9c9db',
        '--accent': '#2655c8', '--accent-solid': '#2459d6', '--accent-hover': '#1947b6',
        '--accent-soft': '#eaf0ff', '--accent-stroke': '#829fec', '--accent-text': '#244ca9',
        '--success-bg': '#e7f8f0', '--success-text': '#086344', '--success-border': '#82cbae',
        '--wrong-bg': '#fff0f1', '--wrong-text': '#99263a', '--wrong-border': '#eba0ae',
        '--warning-bg': '#fff5dc', '--warning-text': '#78520d', '--warning-border': '#d8b96a',
        '--hero-start': '#ffffff', '--hero-mid': '#ffffff', '--hero-end': '#f4f7ff',
        '--sidebar': '#ffffff', '--side-text': '#182843', '--side-muted': '#4d617c',
        '--side-hover': '#f2f6fc', '--side-border': '#d8e1ee',
        '--sidebar-highlight': '#eef3ff', '--header': '#ffffffed',
        '--shadow': 'rgba(27,52,96,.055)', '--shadow-deep': 'rgba(27,52,96,.12)',
        '--focus': 'rgba(36,89,214,.23)', '--code-bg': '#f3f6fa',
    },
    'dark': {
        '--bg': '#0c1422', '--bg-radial': '#17253d', '--surface': '#172338',
        '--surface-2': '#203149', '--surface-3': '#2a3e59',
        '--text': '#f4f7ff', '--muted': '#c1cde0', '--subtle': '#adbfda',
        '--border': '#364961', '--border-strong': '#5a708e',
        '--accent': '#b4c8ff', '--accent-solid': '#2957d1', '--accent-hover': '#1f46b3',
        '--accent-soft': '#213759', '--accent-stroke': '#7599f5', '--accent-text': '#d7e1ff',
        '--success-bg': '#15382f', '--success-text': '#99edd0', '--success-border': '#418971',
        '--wrong-bg': '#452730', '--wrong-text': '#ffbac5', '--wrong-border': '#b45e73',
        '--warning-bg': '#3f341e', '--warning-text': '#ffe4ac', '--warning-border': '#967944',
        '--hero-start': '#1d2c44', '--hero-mid': '#1a2a42', '--hero-end': '#1b3045',
        '--sidebar': '#111d30', '--side-text': '#f4f7ff', '--side-muted': '#c1cde0',
        '--side-hover': '#263a55', '--side-border': '#31445e',
        '--sidebar-highlight': '#203551', '--header': '#121d30ed',
        '--shadow': 'rgba(0,0,0,.16)', '--shadow-deep': 'rgba(0,0,0,.33)',
        '--focus': 'rgba(129,165,255,.31)', '--code-bg': '#101b2c',
    },
}

CSS = r'''
/* v7 — Compact, sidebar-free study workspace.  All colors use theme tokens. */
:root { __THEME_VARS__ color-scheme: __COLOR_SCHEME__; }
*,*::before,*::after {box-sizing:border-box;}
html {scroll-behavior:smooth;scrollbar-gutter:stable;}
html,body,[data-testid="stApp"],[data-testid="stAppViewContainer"] {
 font-family:Inter,"Segoe UI",system-ui,-apple-system,sans-serif!important;
}
[data-testid="stAppViewContainer"] {background:var(--bg)!important;color:var(--text)!important;}
[data-testid="stMain"],[data-testid="stMainBlockContainer"]{min-width:0!important;color:var(--text);}
[data-testid="stHeader"]{background:var(--bg)!important;height:42px!important;}
[data-testid="stHeader"] button{color:var(--text)!important;}
/* No sidebar, collapsed-sidebar glyph, or left-hand flyout is needed in this app. */
[data-testid="stSidebar"],[data-testid="stSidebarCollapsedControl"],[data-testid="stSidebarHeader"]{display:none!important;}
#MainMenu{visibility:visible;} footer{visibility:hidden;}
.block-container,[data-testid="stMainBlockContainer"]{
 max-width:1140px!important;padding:3.15rem 22px 3.2rem!important;
 margin-left:auto!important;margin-right:auto!important;
}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] p{color:var(--muted);line-height:1.55;}
[data-testid="stMain"] [data-testid="stMarkdownContainer"] strong{color:var(--text);}
[data-testid="stMain"] h1,[data-testid="stMain"] h2,[data-testid="stMain"] h3{
 color:var(--text)!important;letter-spacing:-.035em;line-height:1.28;
}
[data-testid="stMain"] a {color:var(--accent-text)!important;text-underline-offset:3px;}
[data-testid="stMain"] a:hover {text-decoration-thickness:2px;}
[data-testid="stMain"] [data-testid="stCaptionContainer"] p{color:var(--subtle)!important;font-size:.81rem;}
[data-testid="stMain"] hr{margin:1rem 0!important;border-color:var(--border)!important;}
[data-testid="stMain"] [data-testid="stColumn"],
[data-testid="stMain"] [data-testid="stHorizontalBlock"],
[data-testid="stMain"] [data-testid="stElementContainer"]{min-width:0;}

/* Header — brand and user controls in line one, visible tab navigation in line two. */
[class*="st-key-site_header"]{
 background:var(--surface)!important;border:1px solid var(--border)!important;
 border-radius:17px!important;padding:13px 18px 9px!important;
 box-shadow:0 4px 16px var(--shadow)!important;
 margin-bottom:18px!important;
}
[class*="st-key-site_header"] [data-testid="stVerticalBlock"]{gap:0!important;}
.site-brand{display:flex;align-items:center;gap:10px;min-width:0;}
.site-brand-icon{height:38px;width:38px;border-radius:11px;flex:none;
 background:linear-gradient(135deg,#405dd1,#6554e7);display:flex;align-items:center;justify-content:center;}
.site-brand-text{display:flex;flex-direction:column;min-width:0;line-height:1.28;}
.site-brand-text b{font-size:1.03rem;font-weight:800;color:var(--text);letter-spacing:-.035em;white-space:nowrap;}
.site-brand-text small{color:var(--subtle);font-size:.72rem;font-weight:550;letter-spacing:.005em;}
.visitor-note{font-size:.81rem;color:var(--muted);font-weight:600;}
.account-popover-title{font-size:.85rem;color:var(--muted);line-height:1.5;padding:3px 2px 12px;}
.account-popover-title b{color:var(--text);overflow-wrap:anywhere;}
/* Profile trigger: looks like a small utility button, not a featured CTA. */
[class*="st-key-site_header"] [data-testid="stPopover"] button{
 max-width:215px!important;min-height:36px!important;padding:7px 12px!important;
 font-size:.8rem!important;border-radius:10px!important;white-space:nowrap!important;
 overflow:hidden;text-overflow:ellipsis;background:var(--surface-2)!important;
}
/* The icon is a CSS SVG rather than an OS-dependent text symbol. */
[class*="st-key-theme_circle"]{display:flex;justify-content:flex-end;}
[class*="st-key-theme_circle"] button{
 width:42px!important;height:42px!important;min-height:42px!important;
 min-width:42px!important;max-width:42px!important;
 border-radius:50%!important;padding:0!important;position:relative!important;
 display:inline-flex!important;align-items:center!important;justify-content:center!important;
 background:var(--surface-2)!important;border:1px solid var(--border-strong)!important;
 color:var(--text)!important;box-shadow:none!important;
}
[class*="st-key-theme_circle"] button:hover{background:var(--accent-soft)!important;
 border-color:var(--accent-stroke)!important;transform:none!important;}
[class*="st-key-theme_circle"] button::before {
    content: "";
    position: absolute !important;
    top: 50% !important;
    left: 50% !important;
    transform: translate(-50%, -50%) !important;
    width: 21px;
    height: 21px;
    background: var(--theme-icon) center / contain no-repeat;
    pointer-events: none;
}
/* Keep the accessible button name in the DOM but visually conceal it. */
[class*="st-key-theme_circle"] button p{
 position:absolute!important;width:1px!important;height:1px!important;
 padding:0!important;overflow:hidden!important;clip-path:inset(50%)!important;
 white-space:nowrap!important;
}
[class*="st-key-top_navigation"]{margin-top:11px!important;padding-top:10px!important;
 border-top:1px solid var(--border)!important;}
[class*="st-key-top_navigation"] [data-testid="stHorizontalBlock"]{
 display:flex!important;flex-wrap:nowrap!important;justify-content:flex-start!important;
 gap:4px!important;align-items:center!important;
}
[class*="st-key-top_navigation"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
 flex:0 0 auto!important;width:auto!important;min-width:0!important;
}
[class*="st-key-top_navigation"] .stButton button,
[class*="st-key-top_navigation"] [data-testid="stBaseButton-secondary"],
[class*="st-key-top_navigation"] [data-testid="stBaseButton-primary"]{
 min-width:0!important;width:auto!important;height:38px!important;min-height:38px!important;
 padding:8px 14px!important;box-shadow:none!important;
 border:1px solid transparent!important;border-radius:10px!important;
 background:transparent!important;color:var(--muted)!important;transform:none!important;
 font-size:.86rem!important;white-space:nowrap!important;
}
[class*="st-key-top_navigation"] button p,
[class*="st-key-top_navigation"] button span{
 color:inherit!important;-webkit-text-fill-color:currentColor!important;
 font-size:inherit!important;font-weight:680!important;
}
[class*="st-key-top_navigation"] .stButton button:hover{
 background:var(--surface-2)!important;color:var(--text)!important;transform:none!important;
 border-color:var(--border)!important;}
[class*="st-key-top_navigation"] .stButton button[kind="primary"],
[class*="st-key-top_navigation"] [data-testid="stBaseButton-primary"]{
 background:var(--accent-soft)!important;color:var(--accent-text)!important;
 border-color:var(--accent-stroke)!important;box-shadow:none!important;
}
[class*="st-key-top_navigation"] .stButton button[kind="primary"] p,
[class*="st-key-top_navigation"] [data-testid="stBaseButton-primary"] p{
 color:var(--accent-text)!important;-webkit-text-fill-color:var(--accent-text)!important;}

/* Buttons — auto-width actions, accurate text contrast, intentional focus rings. */
[data-testid="stMain"] .stButton button,
[data-testid="stMain"] .stFormSubmitButton button,
[data-testid="stMain"] .stDownloadButton button,
[data-testid="stMain"] [data-testid="stPopover"] button{
 min-height:41px;border-radius:10px!important;padding:9px 15px!important;
 border:1px solid var(--border-strong)!important;background:var(--surface-2)!important;
 color:var(--text)!important;box-shadow:none!important;
 font-size:.875rem!important;font-weight:680!important;line-height:1.25!important;
 width:auto!important;max-width:100%;white-space:normal!important;
 transition:background .16s,border-color .16s,box-shadow .16s!important;
}
[data-testid="stMain"] .stButton button:hover,
[data-testid="stMain"] .stFormSubmitButton button:hover,
[data-testid="stMain"] .stDownloadButton button:hover{
 background:var(--surface-3)!important;border-color:var(--accent-stroke)!important;
 box-shadow:0 2px 9px var(--shadow)!important;transform:none!important;
}
[data-testid="stMain"] .stButton button[kind="primary"],
[data-testid="stMain"] [data-testid="stBaseButton-primary"],
[data-testid="stMain"] .stFormSubmitButton button[kind="primary"]{
 background:var(--accent-solid)!important;border-color:var(--accent-solid)!important;
 color:#ffffff!important;
}
[data-testid="stMain"] .stButton button[kind="primary"]:hover,
[data-testid="stMain"] [data-testid="stBaseButton-primary"]:hover,
[data-testid="stMain"] .stFormSubmitButton button[kind="primary"]:hover{
 background:var(--accent-hover)!important;border-color:var(--accent-hover)!important;color:#ffffff!important;
}
[data-testid="stMain"] [data-testid="stBaseButton-primary"] p,
[data-testid="stMain"] .stButton button[kind="primary"] p,
[data-testid="stMain"] .stFormSubmitButton button[kind="primary"] p,
[data-testid="stMain"] .stButton button[kind="primary"] span{
 color:#fff!important;-webkit-text-fill-color:#fff!important;opacity:1!important;
}
[data-testid="stMain"] .stButton button:disabled,
[data-testid="stMain"] .stFormSubmitButton button:disabled{
 opacity:.48!important;cursor:not-allowed!important;box-shadow:none!important;
}
[data-testid="stMain"] button:focus-visible,[data-testid="stMain"] input:focus-visible,
[data-testid="stMain"] textarea:focus-visible{
 outline:3px solid var(--focus)!important;outline-offset:2px!important;
}
/* Small clusters of buttons must stay side by side; do not stretch across the screen. */
[class*="st-key-quick_actions"] [data-testid="stHorizontalBlock"],
[class*="st-key-code_actions"] [data-testid="stHorizontalBlock"],
[class*="st-key-question_actions"] [data-testid="stHorizontalBlock"]{
 display:flex!important;flex-wrap:wrap!important;gap:10px!important;
 justify-content:flex-start!important;align-items:center!important;
}
[class*="st-key-quick_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-code_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
[class*="st-key-question_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
 flex:0 0 auto!important;width:auto!important;min-width:0!important;
}

/* Other page action pairs use the same closely grouped sizing. */
:is([class*="st-key-completed_actions"],[class*="st-key-grading_actions"],[class*="st-key-export_actions"]) [data-testid="stHorizontalBlock"]{
 display:flex!important;flex-wrap:wrap!important;align-items:center!important;
 justify-content:flex-start!important;gap:10px!important;}
:is([class*="st-key-completed_actions"],[class*="st-key-grading_actions"],[class*="st-key-export_actions"]) [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
 flex:0 1 auto!important;width:auto!important;min-width:0!important;}

/* Secondary surfaces and input controls. */
[data-testid="stWidgetLabel"] p{color:var(--muted)!important;font-size:.82rem!important;font-weight:660!important;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input{
 color:var(--text)!important;background:var(--surface-2)!important;
 border:1px solid var(--border-strong)!important;border-radius:10px!important;min-height:41px!important;
 box-shadow:none!important;}
[data-testid="stTextArea"] textarea{line-height:1.57;min-height:105px!important;}
[data-testid="stTextInput"] input::placeholder,[data-testid="stTextArea"] textarea::placeholder{
 color:var(--subtle)!important;opacity:1!important;}
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stMultiSelect"] [data-baseweb="select"] > div{
 background:var(--surface-2)!important;color:var(--text)!important;
 border:1px solid var(--border-strong)!important;border-radius:10px!important;min-height:41px!important;}
[data-testid="stSelectbox"] [data-baseweb="select"] *,
[data-testid="stMultiSelect"] [data-baseweb="select"] *{color:var(--text)!important;}
[data-testid="stMultiSelect"] [data-baseweb="tag"]{background:var(--accent-soft)!important;border-radius:7px;}
[data-testid="stMultiSelect"] [data-baseweb="tag"] *{color:var(--accent-text)!important;}
[data-testid="stNumberInput"] button{background:var(--surface-3)!important;color:var(--text)!important;}
[data-baseweb="popover"],[data-baseweb="menu"],[data-baseweb="popover"] [role="listbox"],
[data-testid="stPopoverBody"]{background:var(--surface)!important;color:var(--text)!important;}
[data-baseweb="popover"] [role="option"]{color:var(--text)!important;}
[data-baseweb="popover"] [role="option"]:hover,
[data-baseweb="popover"] [aria-selected="true"]{background:var(--accent-soft)!important;color:var(--accent-text)!important;}

/* Readable question selectors and their feedback. */
[data-testid="stForm"]{border:1px solid var(--border)!important;background:var(--surface)!important;
 border-radius:14px!important;padding:17px 18px!important;box-shadow:0 2px 10px var(--shadow);}
[data-testid="stRadio"] div[role="radiogroup"]{gap:8px!important;}
[data-testid="stRadio"] div[role="radiogroup"] label{
 display:flex;gap:10px;align-items:center;border-radius:10px!important;
 background:var(--surface-2)!important;border:1px solid var(--border-strong)!important;
 padding:10px 13px!important;min-height:47px!important;max-width:850px!important;
}
[data-testid="stRadio"] div[role="radiogroup"] label:hover{border-color:var(--accent-stroke)!important;background:var(--accent-soft)!important;}
[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked){border:2px solid var(--accent-stroke)!important;
 background:var(--accent-soft)!important;padding:9px 12px!important;}
[data-testid="stRadio"] div[role="radiogroup"] label p{color:var(--text)!important;font-size:.92rem!important;line-height:1.5!important;}
input[type="radio"],input[type="checkbox"]{accent-color:var(--accent-solid)!important;}
[data-testid="stCheckbox"] p{color:var(--text)!important;}
[data-testid="stExpander"]{background:var(--surface)!important;border:1px solid var(--border)!important;
 border-radius:12px!important;box-shadow:none!important;overflow:hidden;}
[data-testid="stExpander"] summary{color:var(--text)!important;padding:10px 13px!important;}
[data-testid="stExpander"] summary:hover{background:var(--surface-2)!important;}
[data-testid="stExpander"] summary p{color:var(--text)!important;font-weight:670!important;}
[data-testid="stMetric"]{padding:13px 15px!important;background:var(--surface)!important;
 border:1px solid var(--border)!important;border-radius:12px!important;box-shadow:0 2px 9px var(--shadow);}
[data-testid="stMetricLabel"] p{font-size:.78rem!important;color:var(--muted)!important;font-weight:670!important;}
[data-testid="stMetricValue"]{font-size:1.58rem!important;line-height:1.15!important;color:var(--text)!important;font-weight:790!important;}
[data-testid="stVerticalBlockBorderWrapper"]{border:1px solid var(--border)!important;
 background:var(--surface)!important;border-radius:13px!important;box-shadow:none!important;}
[data-testid="stTabs"] [data-baseweb="tab-list"]{overflow-x:auto;gap:6px;border-bottom:1px solid var(--border);}
[data-testid="stTabs"] [data-baseweb="tab"]{font-size:.86rem;color:var(--muted)!important;
 border-radius:8px 8px 0 0;padding:9px 13px!important;}
[data-testid="stTabs"] [aria-selected="true"]{background:var(--accent-soft)!important;color:var(--accent-text)!important;}
[data-testid="stProgress"]{max-width:850px;}
[data-testid="stProgress"] [role="progressbar"] > div{background:var(--accent-solid)!important;}
[data-testid="stCode"] pre{border-radius:11px!important;border:1px solid var(--border)!important;
 background:var(--code-bg)!important;}
[data-testid="stCode"] code{font-size:.87rem!important;}
[data-testid="stAlert"]{border-radius:11px!important;}

/* Page-level hierarchy — purposeful density without large blank slabs. */
.hero{position:relative;overflow:hidden;border:1px solid var(--border);border-radius:15px;
 background:linear-gradient(115deg,var(--hero-start),var(--hero-mid) 70%,var(--hero-end));
 padding:22px 24px;margin:0 0 17px;box-shadow:0 2px 11px var(--shadow);}
.hero::after{content:"";width:130px;height:130px;border-radius:50%;position:absolute;
 right:-60px;top:-70px;border:22px solid var(--accent-soft);pointer-events:none;opacity:.7;}
.hero h1{margin:5px 0 6px!important;color:var(--text)!important;font-size:clamp(1.55rem,2.4vw,2rem)!important;
 line-height:1.2!important;font-weight:800!important;letter-spacing:-.042em!important;}
.hero p{font-size:.9rem!important;max-width:730px;margin:0!important;color:var(--muted)!important;line-height:1.54!important;}
.eyebrow{color:var(--accent-text);font-size:.7rem;font-weight:750;letter-spacing:.07em;text-transform:uppercase;}
[data-testid="stMain"] h2.section-title{font-size:1.06rem!important;color:var(--text);font-weight:780;letter-spacing:-.025em;margin:22px 0 7px;padding:0;}
.section-sub{font-size:.85rem;color:var(--muted);line-height:1.5;margin:0 0 11px;}
.feature-icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;
 background:var(--accent-soft);color:var(--accent-text);border:1px solid var(--accent-stroke);margin:0 0 10px;}
.feature-title{font-size:.98rem;font-weight:770;color:var(--text);margin:0 0 5px;}
.feature-description{color:var(--muted);font-size:.84rem;line-height:1.48;min-height:0;margin-bottom:7px;}
[class*="st-key-feature_"]{padding:12px!important;}
[class*="st-key-feature_"] [data-testid="stVerticalBlock"]{gap:.4rem!important;}
[class*="st-key-feature_"]:hover{border-color:var(--accent-stroke)!important;}
.lead-strip{background:var(--surface);border:1px solid var(--border-strong);
 border-radius:12px;padding:13px 16px;margin:5px 0 11px;display:flex;align-items:center;
 justify-content:space-between;gap:10px;flex-wrap:wrap;}
.lead-strip strong{color:var(--text);font-size:.95rem;}
.lead-strip span{color:var(--muted);font-size:.82rem;}
.num-chip{display:inline-flex;align-items:center;padding:4px 9px;margin:0 5px 7px 0;
 background:var(--accent-soft);border:1px solid var(--accent-stroke);border-radius:30px;
 color:var(--accent-text);font-size:.72rem;font-weight:710;}
.chip-teal{background:var(--success-bg);color:var(--success-text);border-color:var(--success-border);}
.chip-amber{background:var(--warning-bg);color:var(--warning-text);border-color:var(--warning-border);}
.chip-muted{background:var(--surface-2);color:var(--muted);border-color:var(--border);}
.question-label{color:var(--accent-text);font-size:.72rem;font-weight:760;text-transform:uppercase;letter-spacing:.06em;}
.question-topline{font-size:.81rem;color:var(--muted);margin-top:3px;}
.question-heading{font-size:clamp(1.24rem,2.4vw,1.7rem);letter-spacing:-.035em;
 color:var(--text);font-weight:770;line-height:1.38;margin:4px 0 11px;overflow-wrap:anywhere;}
[class*="st-key-question_intro"]{max-width:850px!important;background:var(--surface)!important;
 border-radius:13px!important;padding:12px 15px!important;}
.option-title{color:var(--text);font-size:.83rem;font-weight:730;margin:0 0 9px;}
.option-card{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--border-strong);
 background:var(--surface);color:var(--text);padding:10px 12px;margin:7px 0;border-radius:10px;
 line-height:1.5;max-width:850px;overflow-wrap:anywhere;font-size:.91rem;}
.option-card strong{color:var(--text);font-weight:760;}
.option-letter{flex:none;display:flex;align-items:center;justify-content:center;width:26px;height:26px;
 border-radius:7px;background:var(--surface-3);font-size:.8rem;font-weight:780;}
.option-correct{background:var(--success-bg);border-color:var(--success-border);}
.option-wrong{background:var(--wrong-bg);border-color:var(--wrong-border);}
.feedback{max-width:850px;background:var(--success-bg);border:1px solid var(--success-border);
 border-left:4px solid var(--success-border);border-radius:11px;padding:13px 15px;margin:12px 0;}
.feedback-bad{background:var(--wrong-bg);border-color:var(--wrong-border);}
.feedback strong{color:var(--success-text);font-size:.95rem;}
.feedback-bad strong{color:var(--wrong-text);}
.feedback p{margin:5px 0!important;color:var(--text)!important;font-size:.89rem;line-height:1.55;}
.review-item{border:1px solid var(--border);border-radius:10px;background:var(--surface);
 padding:11px 13px;margin:7px 0;}
.review-item b{color:var(--text);font-size:.9rem;}
.review-item p{color:var(--muted);font-size:.8rem;margin:4px 0 0;}
.topic-pill{display:inline-block;background:var(--accent-soft);color:var(--accent-text);
 border:1px solid var(--accent-stroke);padding:5px 10px;border-radius:99px;
 margin:3px 4px 3px 0;font-size:.76rem;font-weight:670;}
.topic-row{display:grid;grid-template-columns:minmax(120px,1fr) minmax(90px,1.8fr) 45px;
 gap:10px;align-items:center;margin:7px 0;padding:9px 11px;background:var(--surface);
 border:1px solid var(--border);border-radius:10px;}
.topic-label{color:var(--text);font-size:.84rem;font-weight:670;overflow-wrap:anywhere;}
.topic-track{height:9px;background:var(--surface-3);border-radius:99px;overflow:hidden;}
.topic-fill{height:100%;background:var(--accent-solid);border-radius:99px;}
.topic-rate{text-align:right;color:var(--text);font-size:.82rem;font-weight:760;}
.empty{background:var(--surface);border:1px dashed var(--border-strong);border-radius:10px;
 padding:19px;text-align:center;color:var(--muted);font-size:.9rem;}
.table-scroll{overflow-x:auto;max-width:100%;border:1px solid var(--border);
 border-radius:10px;background:var(--surface);margin:8px 0;}
.ui-table{width:100%;border-collapse:collapse;font-size:.83rem;}
.ui-table th{font-weight:730;text-align:left;background:var(--surface-2);color:var(--text);
 border-bottom:1px solid var(--border-strong);padding:10px 12px;white-space:nowrap;}
.ui-table td{padding:10px 12px;border-bottom:1px solid var(--border);color:var(--text);vertical-align:top;}
.ui-table tr:last-child td{border-bottom:0;}
.ui-table pre{margin:0;white-space:pre-wrap;min-width:130px;font-size:.8rem;color:var(--text);}

/* Responsive top navigation: a horizontal, scrollable tab strip instead of stacked sidebar items. */
@media (max-width:900px){
 .block-container,[data-testid="stMainBlockContainer"]{padding-left:16px!important;padding-right:16px!important;}
 [class*="st-key-top_navigation"]{min-width:0!important;overflow-x:auto!important;scrollbar-width:thin;}
 [class*="st-key-top_navigation"] [data-testid="stHorizontalBlock"]{min-width:max-content!important;}
 .feature-description{min-height:0;}
}
@media (max-width:640px){
 .block-container,[data-testid="stMainBlockContainer"]{padding:2.7rem 12px 2.7rem!important;}
 [class*="st-key-site_header"]{padding:11px 12px 8px!important;margin-bottom:13px!important;}
 [class*="st-key-site_header"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"]{
  display:flex!important;flex-wrap:wrap!important;gap:7px!important;align-items:center!important;
 }
 /* Brand + circular toggle on first row, account control underneath. */
 [class*="st-key-site_header"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1){
  order:1!important;flex:1 1 auto!important;width:auto!important;min-width:0!important;
 }
 [class*="st-key-site_header"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2){
  order:3!important;flex:1 1 100%!important;width:100%!important;min-width:0!important;
 }
 [class*="st-key-site_header"] > [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(3){
  order:2!important;flex:0 0 42px!important;width:42px!important;min-width:42px!important;
 }
 .site-brand-text b{font-size:.95rem;}.site-brand-text small{font-size:.68rem;}
 [class*="st-key-top_navigation"]{margin-top:7px!important;padding-top:7px!important;overflow:visible!important;}
 [class*="st-key-top_navigation"] [data-testid="stHorizontalBlock"]{
  display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;
  min-width:0!important;gap:5px!important;
 }
 [class*="st-key-top_navigation"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
  flex:1 1 auto!important;width:100%!important;min-width:0!important;
 }
 [data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button{
  width:100%!important;max-width:100%!important;
  font-size:.8rem!important;padding:7px 5px!important;min-height:36px!important;height:36px!important;
 }
 .hero{padding:18px!important;margin-bottom:14px!important;}
 .hero h1{font-size:1.48rem!important;}.hero p{font-size:.85rem!important;}
 .section-title{font-size:1rem;margin:19px 0 5px;}.section-sub{font-size:.82rem;margin-bottom:10px;}
 [data-testid="stMetric"]{padding:11px 12px!important;}
 [data-testid="stMetricValue"]{font-size:1.3rem!important;}
 [data-testid="stMain"] [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]){
  display:flex!important;flex-wrap:wrap!important;gap:8px!important;
 }
 [data-testid="stMain"] [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) > [data-testid="stColumn"]{
  flex:1 1 calc(50% - 5px)!important;width:calc(50% - 5px)!important;
 }
 [data-testid="stMain"] .stButton button{min-height:40px;}
 [class*="st-key-quick_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
 [class*="st-key-code_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
 [class*="st-key-question_actions"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]{
  flex:0 1 auto!important;width:auto!important;}
 .topic-row{grid-template-columns:minmax(95px,1fr) minmax(65px,1.2fr) 38px;gap:8px;}
}

/* Priority guards: Streamlit's generic blue-button rules must never repaint the
   navigation tabs or the circular theme control. Scoped rules go LAST. */
[data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button,
[data-testid="stMain"] [class*="st-key-top_navigation"] [data-testid="stBaseButton-secondary"]{
 min-height:38px!important;height:38px!important;min-width:0!important;width:auto!important;
 padding:8px 14px!important;background:transparent!important;color:var(--muted)!important;
 border:1px solid transparent!important;box-shadow:none!important;border-radius:10px!important;
 white-space:nowrap!important;}
[data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button p{
 color:var(--muted)!important;-webkit-text-fill-color:var(--muted)!important;}
[data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button:hover{
 background:var(--surface-2)!important;border-color:var(--border)!important;color:var(--text)!important;}
[data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button[kind="primary"],
[data-testid="stMain"] [class*="st-key-top_navigation"] [data-testid="stBaseButton-primary"]{
 background:var(--accent-soft)!important;border-color:var(--accent-stroke)!important;
 color:var(--accent-text)!important;box-shadow:none!important;}
[data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button[kind="primary"] p,
[data-testid="stMain"] [class*="st-key-top_navigation"] [data-testid="stBaseButton-primary"] p{
 color:var(--accent-text)!important;-webkit-text-fill-color:var(--accent-text)!important;}
[data-testid="stMain"] [class*="st-key-theme_circle"] button{
 width:42px!important;min-width:42px!important;max-width:42px!important;
 height:42px!important;min-height:42px!important;border-radius:50%!important;
 background:var(--surface-2)!important;border:1px solid var(--border-strong)!important;
 padding:0!important;box-shadow:none!important;}
[data-testid="stMain"] [class*="st-key-theme_circle"] button:hover{
 background:var(--accent-soft)!important;border-color:var(--accent-stroke)!important;}

/* Keep long questions and code inside their surface, including narrow phones. */
.question-heading,.review-item,.option-card,.lead-strip,.hero{overflow-wrap:anywhere;}
.option-card > span:last-child{min-width:0;white-space:pre-wrap;}
.option-letter{flex-shrink:0;}
[data-testid="stTextArea"] textarea[aria-label="Your Python code"]{
 font-family:Consolas,"Cascadia Code",monospace!important;font-size:.9rem!important;
 tab-size:4;line-height:1.65!important;}
[data-testid="stRadio"] label:has(input:focus-visible),
[data-testid="stMain"] summary:focus-visible,.table-scroll:focus-visible{
 outline:3px solid var(--accent-stroke)!important;outline-offset:3px;}
[data-testid="stMain"] button:focus-visible,[data-testid="stMain"] input:focus-visible,
[data-testid="stMain"] textarea:focus-visible{
 outline-color:var(--accent-stroke)!important;}
[data-baseweb="select"]:focus-within{outline:2px solid var(--accent-stroke);outline-offset:2px;border-radius:10px;}
[data-testid="stMain"] [data-testid="stAlert"] p{color:var(--text)!important;}
[data-testid="stMain"] .stButton button:disabled:hover{
 background:var(--surface-2)!important;border-color:var(--border-strong)!important;}
.hero{border-top:3px solid var(--accent-stroke);}
[class*="st-key-feature_"]{transition:border-color .16s ease,box-shadow .16s ease;}
[class*="st-key-feature_"]:hover{box-shadow:0 5px 18px var(--shadow)!important;}
/* After the navigation guards so mobile hit areas are not overwritten. */
@media (max-width:640px){
 [data-testid="stMain"] [class*="st-key-top_navigation"] .stButton button{
  width:100%!important;min-height:44px!important;height:auto!important;
  padding:9px 5px!important;white-space:normal!important;}
 [data-testid="stMain"] .stButton button,
 [data-testid="stMain"] .stFormSubmitButton button,
 [data-testid="stMain"] .stDownloadButton button{min-height:44px!important;}
 [data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea,
 [data-testid="stNumberInput"] input{font-size:16px!important;}
 [data-testid="stForm"]{padding:14px!important;}
 .site-brand-text b{white-space:normal;}
 .ui-table td{min-width:100px;}
}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important;scroll-behavior:auto!important;}}
'''


def style(theme: str) -> str:
    """Return light/dark tokenized CSS, including a real SVG for the toggle."""
    if theme not in THEMES:
        raise ValueError(f"Unknown theme: {theme}")
    vars_ = dict(THEMES[theme])
    vars_["--theme-icon"] = f'url("{svg_css("sun" if theme == "dark" else "moon", vars_["--text"])}")'
    blob = ';'.join(f'{key}:{value}' for key, value in vars_.items()) + ';'
    return '<style>' + CSS.replace('__THEME_VARS__', blob).replace('__COLOR_SCHEME__', theme) + '</style>'
