"""Custom Streamlit CSS for a polished Power BI-style dashboard."""

CSS = """
<style>
:root {
    --navy-950: #081421;
    --navy-900: #0C2235;
    --navy-800: #15314A;
    --ink-900: #122033;
    --ink-700: #32445E;
    --ink-500: #667A94;
    --paper-100: #F4F7FB;
    --paper-200: #E8EEF6;
    --card: #FFFFFF;
    --line: #D8E2EE;
    --line-strong: #C4D2E2;
    --red: #D94C45;
    --orange: #E69A1C;
    --green: #0F8B5F;
    --green-bright: #8DE0B8;
    --green-soft: #E7F8F0;
    --emerald: #16A34A;
    --blue: #2F6DE1;
    --purple: #7C5CDB;
    --teal: #118A8A;
    --radius-lg: 18px;
    --radius-md: 14px;
    --radius-sm: 10px;
    --shadow-soft: 0 12px 32px rgba(11, 28, 48, .08);
    --shadow-medium: 0 20px 44px rgba(11, 28, 48, .12);
}

#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility: hidden; }
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarUserContent"] > div:first-child:has([data-testid="stSidebarNav"]) {
    display: none !important;
}
.stApp {
    background:
        radial-gradient(circle at 0% 0%, rgba(15, 139, 95, .10), transparent 28%),
        radial-gradient(circle at 100% 0%, rgba(47, 109, 225, .10), transparent 24%),
        linear-gradient(180deg, rgba(255,255,255,.88) 0%, rgba(245,248,252,.96) 40%, rgba(236,243,249,1) 100%),
        repeating-linear-gradient(135deg, rgba(11,35,64,.028) 0, rgba(11,35,64,.028) 1px, transparent 1px, transparent 20px);
    color: var(--ink-900);
}
.block-container {
    padding: 1rem 1.18rem 1.7rem 1.18rem;
    max-width: 100%;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--ink-900);
    letter-spacing: 0;
}
h1 { font-size: 1.9rem; margin: 0; line-height: 1.04; font-weight: 900; }
h2 { font-size: 1.15rem; font-weight: 850; }
h3 { font-size: .98rem; text-transform: uppercase; font-weight: 900; }

section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 12% 0%, rgba(255,255,255,.82), transparent 34%),
        radial-gradient(circle at 100% 16%, rgba(134,239,172,.44), transparent 34%),
        linear-gradient(180deg, #E8FFF0 0%, #CFFADB 42%, #A7F3C4 100%);
    border-right: 1px solid rgba(34,197,94,.32);
    box-shadow: 14px 0 42px rgba(16, 105, 60, .16);
}
section[data-testid="stSidebar"] .block-container,
section[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
    gap: .62rem;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: #075333 !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    font-size: .74rem !important;
    letter-spacing: .06em;
}
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stCaptionContainer {
    color: #123B2B !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
section[data-testid="stSidebar"] div[data-baseweb="select"] input,
section[data-testid="stSidebar"] div[data-baseweb="select"] span,
section[data-testid="stSidebar"] .stTextInput input,
section[data-testid="stSidebar"] .stMultiSelect input {
    color: #0B2E21 !important;
    font-weight: 760 !important;
}
section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
    border-radius: 12px;
    border: 1px solid rgba(22,163,74,.36);
    background: linear-gradient(180deg, #FFFFFF 0%, #F1FFF6 100%) !important;
    box-shadow: 0 10px 22px rgba(16,105,60,.11), inset 0 1px 0 rgba(255,255,255,.9);
}
section[data-testid="stSidebar"] div[data-baseweb="select"] svg {
    color: #0F5132 !important;
    fill: #0F5132 !important;
}
div[data-baseweb="popover"] div[role="listbox"],
div[data-baseweb="popover"] ul {
    background: #F7FCF8 !important;
    border: 1px solid rgba(34,197,94,.22) !important;
    box-shadow: 0 18px 40px rgba(5,34,25,.18) !important;
}
div[data-baseweb="popover"] div[role="option"],
div[data-baseweb="popover"] li,
div[data-baseweb="popover"] span {
    color: #052219 !important;
    font-weight: 760 !important;
}
div[data-baseweb="popover"] div[aria-selected="true"] {
    background: #DCFCE7 !important;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] {
    padding-top: .18rem;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stTickBar"] {
    display: none;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] div[role="slider"] {
    background: #FFFFFF !important;
    border: 4px solid #22C55E !important;
    box-shadow: 0 0 0 5px rgba(34,197,94,.18), 0 8px 18px rgba(16,105,60,.22) !important;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] [data-baseweb="slider"] > div {
    color: #22C55E !important;
}
section[data-testid="stSidebar"] [data-testid="stSlider"] p {
    color: #064E3B !important;
    font-weight: 900 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] {
    display: flex;
    flex-direction: column;
    align-items: stretch;
    background: rgba(255,255,255,.48);
    border: 1px solid rgba(22,163,74,.25);
    border-radius: 14px;
    padding: .48rem;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label {
    display: flex;
    align-items: center;
    align-self: stretch;
    flex: 1 1 0% !important;
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;
    box-sizing: border-box;
    height: 66px;
    border-radius: 14px;
    padding: .56rem .72rem;
    margin: 0 0 .3rem 0;
    color: #123B2B !important;
    background: rgba(255,255,255,.58);
    border: 1px solid rgba(22,163,74,.15);
    transition: background .15s ease, color .15s ease;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:last-child {
    margin-bottom: 0;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label span {
    color: #123B2B !important;
    font-size: .9rem !important;
    font-weight: 760 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label p {
    margin: 0 !important;
    line-height: 1.15 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label > div:last-child {
    flex: 1 1 auto;
    min-width: 0;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked),
section[data-testid="stSidebar"] [role="radiogroup"] > label:has([aria-checked="true"]) {
    background: linear-gradient(135deg, #D8FBE5 0%, #BDF7D1 100%) !important;
    color: #0B2E21 !important;
    border-color: rgba(22,163,74,.55);
    box-shadow: 0 14px 28px rgba(16,105,60,.14);
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) span,
section[data-testid="stSidebar"] [role="radiogroup"] > label:has([aria-checked="true"]) span {
    color: #0B2E21 !important;
    font-weight: 860 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] > label:has(input:checked) input,
section[data-testid="stSidebar"] [role="radiogroup"] > label:has([aria-checked="true"]) input {
    accent-color: #22C55E;
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(22,163,74,.22);
    margin: .6rem 0 .85rem;
}

.dashboard-brand {
    display: flex;
    align-items: center;
    gap: .72rem;
    padding: .35rem 0 .88rem;
}
.brand-mark {
    width: 48px;
    height: 48px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    font-weight: 900;
    letter-spacing: -.02em;
    color: #0B2E21;
    background: linear-gradient(145deg, #D9F99D 0%, #86EFAC 55%, #22C55E 100%);
    box-shadow: 0 16px 32px rgba(22,163,74,.24);
}
.brand-title {
    color: #052E1F !important;
    font-weight: 900;
    line-height: 1.03;
    font-size: 1.08rem;
}
.brand-subtitle {
    color: #166534 !important;
    font-size: .72rem;
    font-weight: 750;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-top: .15rem;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
    min-height: 56px;
    width: 100%;
    justify-content: flex-start;
    border-radius: 14px;
    border: 1px solid rgba(22,163,74,.24);
    background: rgba(255,255,255,.56);
    color: #0B3D2D !important;
    font-weight: 880;
    letter-spacing: 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.08), 0 10px 18px rgba(4, 24, 18, .12);
    transition: background .16s ease, border-color .16s ease, transform .16s ease;
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
    background: rgba(220,252,231,.9);
    border-color: rgba(22,163,74,.56);
    color: #052E1F !important;
    transform: translateY(-1px);
}
section[data-testid="stSidebar"] div[data-testid="stButton"] > button p {
    color: inherit !important;
    font-weight: 880 !important;
}
.sidebar-rule {
    height: 1px;
    background: linear-gradient(90deg, rgba(22,163,74,.34), rgba(22,163,74,0));
    margin: .8rem 0;
}
.sidebar-caption,
.sidebar-note {
    color: #164E35 !important;
    font-size: .78rem;
    line-height: 1.45;
}
.sidebar-note {
    border: 1px solid rgba(22,163,74,.24);
    background: rgba(255,255,255,.42);
    border-radius: 14px;
    padding: .72rem .78rem;
    margin-top: .4rem;
}

.page-hero {
    position: relative;
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    align-items: stretch;
    border: 1px solid rgba(200,213,232,.9);
    background:
        linear-gradient(135deg, rgba(255,255,255,.99) 0%, rgba(248,250,254,.97) 58%, rgba(236,242,250,.99) 100%);
    border-radius: 18px;
    padding: 1rem 1.08rem;
    box-shadow: var(--shadow-soft);
    overflow: hidden;
    margin-bottom: .82rem;
}
.page-hero:before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: var(--hero-accent, var(--red));
}
.page-eyebrow {
    color: var(--hero-accent, var(--red));
    font-size: .72rem;
    font-weight: 900;
    letter-spacing: .09em;
    text-transform: uppercase;
    margin-bottom: .16rem;
}
.page-question {
    color: var(--ink-700);
    font-weight: 760;
    margin-top: .3rem;
    font-size: .98rem;
}
.hero-meta {
    display: flex;
    align-items: center;
    gap: .48rem;
    flex-wrap: wrap;
    justify-content: flex-end;
    min-width: 260px;
}
.hero-pill {
    border: 1px solid var(--line);
    background: #FFFFFF;
    color: var(--ink-700);
    border-radius: 999px;
    padding: .5rem .7rem;
    font-size: .78rem;
    font-weight: 850;
    box-shadow: 0 10px 22px rgba(31,45,77,.06);
}
.filter-strip {
    display: flex;
    gap: .45rem;
    flex-wrap: wrap;
    align-items: center;
    margin: .24rem 0 .78rem;
}
.filter-chip {
    display: inline-flex;
    gap: .4rem;
    align-items: center;
    border: 1px solid var(--line);
    background: rgba(255,255,255,.82);
    border-radius: 999px;
    padding: .42rem .68rem;
    font-size: .78rem;
    box-shadow: 0 10px 22px rgba(31,45,77,.05);
}
.filter-key {
    color: var(--ink-500);
    font-weight: 800;
}
.filter-value {
    color: var(--ink-900);
    font-weight: 900;
}

.section-heading {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 1rem;
    margin: .86rem 0 .42rem;
}
.section-kicker {
    color: #0F8B5F;
    text-transform: uppercase;
    letter-spacing: .09em;
    font-size: .68rem;
    font-weight: 900;
}
.section-title {
    color: var(--ink-900);
    font-size: 1rem;
    font-weight: 900;
    margin-top: .04rem;
}
.section-subtitle {
    color: var(--ink-500);
    font-size: .82rem;
    font-weight: 650;
}

.kpi-card {
    min-height: 106px;
    position: relative;
    display: flex;
    gap: .74rem;
    align-items: center;
    background:
        linear-gradient(140deg, #FFFFFF 0%, #FBFEFC 64%, rgba(246,252,248,.96) 100%);
    border: 1px solid var(--line);
    border-top: 4px solid var(--accent, var(--red));
    border-radius: 18px;
    padding: .92rem .95rem;
    box-shadow: var(--shadow-soft);
    overflow: hidden;
}
.kpi-card:after {
    content: "";
    position: absolute;
    right: -32px;
    bottom: -38px;
    width: 112px;
    height: 112px;
    border: 18px solid var(--accent-soft, rgba(214,59,50,.09));
    border-radius: 50%;
}
.kpi-icon {
    position: relative;
    z-index: 1;
    width: 46px;
    height: 46px;
    border-radius: 14px;
    display: grid;
    place-items: center;
    flex: 0 0 auto;
    color: var(--accent, var(--red));
    background: var(--accent-soft, rgba(214,59,50,.09));
    border: 1px solid rgba(255,255,255,.74);
    font-size: .72rem;
    font-weight: 950;
    letter-spacing: .04em;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.72);
}
.kpi-body { position: relative; z-index: 1; min-width: 0; }
.kpi-title {
    font-size: .68rem;
    text-transform: uppercase;
    color: var(--ink-500);
    font-weight: 900;
    letter-spacing: .06em;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.kpi-value {
    font-size: clamp(1.05rem, 1.22vw, 1.55rem);
    color: var(--ink-900);
    font-weight: 950;
    line-height: 1.08;
    margin-top: .14rem;
    overflow-wrap: anywhere;
}
.kpi-subtitle {
    color: var(--ink-500);
    font-size: .78rem;
    font-weight: 750;
    margin-top: .18rem;
}

div[data-testid="stPlotlyChart"] {
    background:
        linear-gradient(180deg, #FFFFFF 0%, #FCFDFF 100%);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 10px 10px 8px;
    box-shadow: var(--shadow-soft);
}
.insight-panel {
    border: 1px solid var(--line);
    border-radius: 18px;
    background:
        linear-gradient(180deg, #FFFFFF 0%, #F8FBFF 100%);
    padding: 1rem;
    box-shadow: var(--shadow-soft);
}
.insight-title {
    display: flex;
    align-items: center;
    gap: .5rem;
    color: var(--ink-900);
    font-weight: 950;
    text-transform: uppercase;
    letter-spacing: .05em;
    font-size: .82rem;
    margin-bottom: .58rem;
}
.insight-mark {
    width: 28px;
    height: 28px;
    border-radius: 10px;
    display: grid;
    place-items: center;
    background: rgba(34,197,94,.12);
    color: #15803D;
    font-weight: 950;
}
.insight {
    position: relative;
    background: #FFFFFF;
    border: 1px solid #DDE8FA;
    border-left: 4px solid #22C55E;
    border-radius: 14px;
    padding: .7rem .78rem .7rem .86rem;
    margin: .42rem 0;
    color: #26365E;
    font-weight: 720;
    line-height: 1.36;
    box-shadow: 0 10px 20px rgba(31,45,77,.05);
}
.single-insight {
    border-color: #DDE8FA;
    background: linear-gradient(90deg, rgba(46,98,212,.07), rgba(255,255,255,.92));
    color: #2D4477;
    margin: .45rem 0 .75rem;
}

.stTabs [data-baseweb="tab-list"] {
    gap: .35rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 12px;
    border: 1px solid var(--line);
    background: white;
    padding: .45rem .78rem;
}
button[kind="secondary"],
button[kind="primary"] {
    border-radius: 12px;
    font-weight: 850;
}

div[data-testid="stAlert"] {
    border-radius: 14px;
    border: 1px solid var(--line);
    box-shadow: var(--shadow-soft);
}

div[data-baseweb="select"] > div,
.stTextInput input,
.stTextArea textarea {
    border-radius: 12px !important;
}

hr {
    border-color: rgba(200,213,232,.6);
}

@media (max-width: 980px) {
    .page-hero { flex-direction: column; }
    .hero-meta { justify-content: flex-start; min-width: 0; }
    .kpi-card { min-height: 96px; }
    .section-heading { flex-direction: column; align-items: flex-start; }
}
</style>
"""
