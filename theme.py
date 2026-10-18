"""Visual theme: tinted canvas, floating white cards, dark slicer rail.

Modelled on the Power BI dashboards the team referenced - a soft blue page with
white cards sitting on it, a dark navy rail for the slicers, and dense packing.
"""
from __future__ import annotations

NAVY = "#12315c"
NAVY_DEEP = "#0d2546"
BLUE = "#1668d6"
BLUE_LT = "#5aa0f0"
CANVAS = "#dceaf9"
CARD = "#ffffff"
INK = "#13233d"
MUTED = "#6a7a92"

CSS = f"""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{
  background: {CANVAS} !important; }}
[data-testid="stAppViewContainer"], [data-testid="stMain"], .stApp {{
  min-height: 100vh !important; }}
[data-testid="stSidebarContent"], [data-testid="stSidebarUserContent"] {{
  min-height: 100vh !important; background: {NAVY} !important; }}
.stApp {{ background: linear-gradient(180deg, {CANVAS} 0%, #eaf2fc 45%, #d3e3f7 100%)
  !important; background-attachment: fixed !important; }}
[data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
[data-testid="stMainBlockContainer"] {{ background: rgba(0,0,0,0) !important; }}
.block-container {{ padding: 1.4rem 1.6rem 1rem 1.6rem; max-width: 100%; }}

/* ---- dark slicer rail ---- */
section[data-testid="stSidebar"] {{ background: {NAVY}; border-right: none; }}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] h3 {{ color: #e8eefb !important; }}
section[data-testid="stSidebar"] h3 {{ color: #ffffff !important; font-size: 1.02rem;
  letter-spacing: .04em; text-transform: uppercase; }}
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {{
  color: #a9bdda !important; font-size: .76rem; text-transform: uppercase;
  letter-spacing: .04em; margin-bottom: 2px; }}
/* Streamlit 1.66 renders selects as react-aria ComboBox, not baseweb */
section[data-testid="stSidebar"] .react-aria-ComboBox [role="group"],
section[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"] {{
  border: 1px solid #2b4a79 !important; border-radius: 7px !important; }}
section[data-testid="stSidebar"] [role="combobox"] {{
  color: {INK} !important; -webkit-text-fill-color: {INK} !important;
  font-weight: 600; }}
section[data-testid="stSidebar"] [role="combobox"]::placeholder {{
  color: #7f97bb !important; -webkit-text-fill-color: #7f97bb !important; }}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {{ fill: #9fc0ea !important; }}
section[data-testid="stSidebar"] [data-testid="stCheckbox"] p {{ font-size: .8rem; }}
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {{
  color: #8fa9cc !important; }}
/* the dropdown menu renders in a portal on a light surface - keep it readable */
[role="listbox"], [role="listbox"] [role="option"] {{ color: {INK} !important; }}
section[data-testid="stSidebar"] hr {{ border-color: #2b4a79; margin: .7rem 0; }}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] strong {{
  color: #7fb0ee !important; font-size: .8rem; letter-spacing: .05em; }}

/* ---- title block ---- */
h1 {{ font-size: 1.95rem !important; font-weight: 700; color: {INK}; margin: 0 0 .1rem 0; }}

/* ---- KPI tiles ---- */
div[data-testid="stMetric"] {{ background: {CARD}; border: 1px solid #ccdcf0;
  border-radius: 12px; padding: 13px 16px 9px 16px;
  box-shadow: 0 1px 3px rgba(18,49,92,.10); }}
div[data-testid="stMetricLabel"] p {{ font-size: .74rem !important; color: {MUTED};
  text-transform: uppercase; letter-spacing: .055em; font-weight: 600; }}
div[data-testid="stMetricValue"] {{ font-size: 1.6rem !important; font-weight: 700;
  color: {INK}; line-height: 1.15; white-space: nowrap; }}

/* ---- chart cards ---- */
div[data-testid="stVerticalBlockBorderWrapper"] {{ background: {CARD};
  border: 1px solid #ccdcf0 !important; border-radius: 12px;
  box-shadow: 0 1px 3px rgba(18,49,92,.10); padding: .35rem .2rem; }}
div[data-testid="stVerticalBlockBorderWrapper"] [data-testid="stMarkdownContainer"] strong {{
  font-size: .95rem; color: {INK}; }}

/* ---- category bar ---- */
div[data-testid="stElementContainer"] div[role="radiogroup"] {{ gap: .2rem; }}
button[kind="segmented_control"], button[data-testid="stBaseButton-segmented_control"] {{
  border-radius: 8px !important; font-weight: 600 !important; }}

/* ---- misc tightening ---- */
div[data-testid="stExpander"] details {{ border: none; background: #f6f9fe;
  border-radius: 8px; }}
div[data-testid="stAlert"] {{ border-radius: 10px; }}
hr {{ margin: .6rem 0; }}
</style>
"""
