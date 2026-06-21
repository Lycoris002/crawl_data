import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import requests

st.set_page_config(page_title="NEU Courses Explorer", page_icon="🎓", layout="wide")

# ══════════════════════════════════════════════════════════════
#  Session State – Theme
# ══════════════════════════════════════════════════════════════
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # mặc định dark

# Ẩn hidden toggle button bằng CSS (trước khi render)
st.markdown("""
<style>
    /* Ẩn đúng button toggle theme */
    #theme-toggle-anchor + div button,
    div[data-testid="stButton"] button[kind="secondary"] {
        position: fixed !important;
        top: -9999px !important;
        left: -9999px !important;
        width: 1px !important;
        height: 1px !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }
</style>
<div id="theme-toggle-anchor"></div>
""", unsafe_allow_html=True)

# Hidden toggle button (triggered by JS keyboard shortcut)
toggle_clicked = st.button("__toggle_theme__", key="theme_toggle_btn")
if toggle_clicked:
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()

IS_DARK = st.session_state.dark_mode

# ══════════════════════════════════════════════════════════════
#  JS: Lắng nghe phím "D" → click hidden button
#  Dùng components.html() thay st.markdown() vì Streamlit strip <script>
# ══════════════════════════════════════════════════════════════
components.html("""
<script>
(function() {
    var doc = window.parent.document;

    // ── Keyboard shortcut: D → toggle theme ──
    doc.addEventListener('keydown', function(e) {
        var tag = (e.target.tagName || '').toLowerCase();
        if (tag === 'input' || tag === 'textarea' || e.target.isContentEditable) return;
        if (e.key === 'd' || e.key === 'D') {
            var btns = doc.querySelectorAll('button');
            for (var i = 0; i < btns.length; i++) {
                if (btns[i].innerText.trim() === '__toggle_theme__') {
                    btns[i].click();
                    break;
                }
            }
        }
    }, true);

    // ── Fix sidebar toggle button position to vertical center ──
    function fixTogglePosition() {
        var btn = doc.querySelector('[data-testid="collapsedControl"]');
        if (btn) {
            btn.style.setProperty('position', 'fixed', 'important');
            btn.style.setProperty('top', '50vh', 'important');
            btn.style.setProperty('transform', 'translateY(-50%)', 'important');
            btn.style.setProperty('z-index', '9999', 'important');
        }
    }

    // Chạy ngay và giữ bằng MutationObserver
    fixTogglePosition();
    var observer = new MutationObserver(function() { fixTogglePosition(); });
    observer.observe(doc.body, { childList: true, subtree: true, attributes: true });

    // Backup: chạy lại sau khi trang load hoàn toàn
    setTimeout(fixTogglePosition, 500);
    setTimeout(fixTogglePosition, 1500);
})();
</script>
""", height=0)

# ══════════════════════════════════════════════════════════════
#  THEME TOKENS
# ══════════════════════════════════════════════════════════════
if IS_DARK:
    BG_APP        = "linear-gradient(135deg, #0a0e1a 0%, #0d1526 40%, #0f1f3d 100%)"
    BG_SIDEBAR    = "linear-gradient(180deg, #0d1526 0%, #111827 100%)"
    SIDEBAR_BORDER = "rgba(99,179,237,0.15)"
    SIDEBAR_SHADOW = "4px 0 30px rgba(0,0,0,0.5)"
    TEXT_PRIMARY  = "#f0f9ff"
    TEXT_SECONDARY= "#94a3b8"
    TEXT_ACCENT   = "#60a5fa"
    TEXT_ACCENT2  = "#93c5fd"
    HEADER_GRAD   = "linear-gradient(90deg,#60a5fa,#a78bfa,#60a5fa)"
    CARD_BG       = "rgba(255,255,255,0.04)"
    CARD_BORDER   = "rgba(255,255,255,0.08)"
    CARD_SHADOW   = "0 8px 32px rgba(0,0,0,0.4),inset 0 1px 0 rgba(255,255,255,0.07)"
    CARD_HOVER_SH = "0 20px 50px rgba(59,130,246,0.2),inset 0 1px 0 rgba(255,255,255,0.1)"
    SELECT_BG     = "rgba(255,255,255,0.05)"
    SELECT_BORDER = "rgba(99,179,237,0.25)"
    SELECT_TEXT   = "#e2e8f0"
    EXP_BG        = "rgba(255,255,255,0.04)"
    EXP_BORDER    = "rgba(99,179,237,0.12)"
    EXP_TEXT      = "#93c5fd"
    EXP_HOVER_BG  = "rgba(59,130,246,0.08)"
    EXP_HOVER_BD  = "rgba(99,179,237,0.3)"
    METRIC_BG     = "rgba(59,130,246,0.08)"
    METRIC_BORDER = "rgba(59,130,246,0.2)"
    METRIC_LABEL  = "#93c5fd"
    METRIC_VALUE  = "#f0f9ff"
    H_COLOR       = "#e2e8f0"
    TAB_COLOR     = "#94a3b8"
    TAB_ACTIVE    = "#60a5fa"
    TAB_ACTIVE_BD = "#3b82f6"
    SBAR_INFO_BG  = "rgba(59,130,246,0.08)"
    SBAR_INFO_BD  = "rgba(59,130,246,0.2)"
    SBAR_INFO_TXT = "#94a3b8"
    BTN_GRAD      = "linear-gradient(135deg,#1d4ed8,#4f46e5)"
    BTN_HOVER     = "linear-gradient(135deg,#2563eb,#6366f1)"
    BTN_SHADOW    = "0 4px 20px rgba(79,70,229,0.45)"
    BTN_HOVER_SH  = "0 6px 28px rgba(99,102,241,0.7)"
    CHART_BG      = "rgba(255,255,255,0.03)"
    CHART_BORDER  = "rgba(255,255,255,0.06)"
    DIVIDER_GRAD  = "linear-gradient(90deg,#3b82f6,#a78bfa)"
    DIVIDER_GLOW  = "rgba(99,102,241,0.4)"
    TOGGLE_ICON   = "☀️"
    TOGGLE_LABEL  = "Light Mode"
    ARROW_BG      = "linear-gradient(135deg,#1e40af,#3b82f6)"
    ARROW_GLOW    = "rgba(59,130,246,0.5)"
    ARROW_H_GLOW  = "rgba(59,130,246,0.8)"
    SUB_H_COLOR   = "#94a3b8"
    SIDEBAR_STAR  = "#93c5fd"
    MAJOR_H_COLOR = "#f0f9ff"
    MAJOR_P_COLOR = "#60a5fa"
    MAJOR_CODE_C  = "#93c5fd"
else:
    BG_APP        = "linear-gradient(135deg, #f0f6ff 0%, #e8f0fe 40%, #f5f0ff 100%)"
    BG_SIDEBAR    = "linear-gradient(180deg, #ffffff 0%, #f8faff 100%)"
    SIDEBAR_BORDER = "rgba(59,130,246,0.12)"
    SIDEBAR_SHADOW = "4px 0 20px rgba(59,130,246,0.08)"
    TEXT_PRIMARY  = "#0f172a"
    TEXT_SECONDARY= "#475569"
    TEXT_ACCENT   = "#1d4ed8"
    TEXT_ACCENT2  = "#2563eb"
    HEADER_GRAD   = "linear-gradient(90deg,#1d4ed8,#7c3aed,#1d4ed8)"
    CARD_BG       = "rgba(255,255,255,0.85)"
    CARD_BORDER   = "rgba(59,130,246,0.12)"
    CARD_SHADOW   = "0 4px 24px rgba(59,130,246,0.1),inset 0 1px 0 rgba(255,255,255,0.9)"
    CARD_HOVER_SH = "0 12px 40px rgba(59,130,246,0.18),inset 0 1px 0 rgba(255,255,255,1)"
    SELECT_BG     = "rgba(255,255,255,0.95)"
    SELECT_BORDER = "rgba(59,130,246,0.25)"
    SELECT_TEXT   = "#0f172a"
    EXP_BG        = "rgba(59,130,246,0.04)"
    EXP_BORDER    = "rgba(59,130,246,0.15)"
    EXP_TEXT      = "#1d4ed8"
    EXP_HOVER_BG  = "rgba(59,130,246,0.08)"
    EXP_HOVER_BD  = "rgba(59,130,246,0.3)"
    METRIC_BG     = "rgba(59,130,246,0.06)"
    METRIC_BORDER = "rgba(59,130,246,0.18)"
    METRIC_LABEL  = "#2563eb"
    METRIC_VALUE  = "#0f172a"
    H_COLOR       = "#0f172a"
    TAB_COLOR     = "#64748b"
    TAB_ACTIVE    = "#1d4ed8"
    TAB_ACTIVE_BD = "#2563eb"
    SBAR_INFO_BG  = "rgba(59,130,246,0.05)"
    SBAR_INFO_BD  = "rgba(59,130,246,0.15)"
    SBAR_INFO_TXT = "#475569"
    BTN_GRAD      = "linear-gradient(135deg,#1d4ed8,#4f46e5)"
    BTN_HOVER     = "linear-gradient(135deg,#2563eb,#6366f1)"
    BTN_SHADOW    = "0 4px 16px rgba(29,78,216,0.3)"
    BTN_HOVER_SH  = "0 6px 24px rgba(99,102,241,0.5)"
    CHART_BG      = "rgba(255,255,255,0.7)"
    CHART_BORDER  = "rgba(59,130,246,0.1)"
    DIVIDER_GRAD  = "linear-gradient(90deg,#3b82f6,#7c3aed)"
    DIVIDER_GLOW  = "rgba(99,102,241,0.25)"
    TOGGLE_ICON   = "🌙"
    TOGGLE_LABEL  = "Dark Mode"
    ARROW_BG      = "linear-gradient(135deg,#1d4ed8,#3b82f6)"
    ARROW_GLOW    = "rgba(29,78,216,0.35)"
    ARROW_H_GLOW  = "rgba(29,78,216,0.6)"
    SUB_H_COLOR   = "#475569"
    SIDEBAR_STAR  = "#1d4ed8"
    MAJOR_H_COLOR = "#0f172a"
    MAJOR_P_COLOR = "#1d4ed8"
    MAJOR_CODE_C  = "#2563eb"

# ══════════════════════════════════════════════════════════════
#  INJECT CSS
# ══════════════════════════════════════════════════════════════
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Outfit:wght@400;600;800&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        transition: background 0.4s ease, color 0.4s ease;
    }}

    /* ─── Global Background ─── */
    .stApp {{
        background: {BG_APP};
        min-height: 100vh;
        transition: background 0.4s ease;
    }}

    /* ─── Hide the physical hidden toggle button ─── */
    button[kind="secondary"]:has(> div > p:contains("__toggle_theme__")) {{
        display: none !important;
    }}
    /* Fallback for older Streamlit – hide by text */
    [data-testid="baseButton-secondary"] {{
        /* only hides if it's truly empty-label style */
    }}

    /* ─── Sidebar – smooth slide animation ─── */
    section[data-testid="stSidebar"] {{
        background: {BG_SIDEBAR} !important;
        border-right: 1px solid {SIDEBAR_BORDER};
        box-shadow: {SIDEBAR_SHADOW};
        /* Animation mượt khi toggle */
        transition:
            width 0.45s cubic-bezier(0.4, 0, 0.2, 1),
            min-width 0.45s cubic-bezier(0.4, 0, 0.2, 1),
            max-width 0.45s cubic-bezier(0.4, 0, 0.2, 1),
            transform 0.45s cubic-bezier(0.4, 0, 0.2, 1),
            opacity 0.4s ease,
            background 0.4s ease !important;
        will-change: width, transform, opacity;
        overflow: hidden;
    }}
    /* Khi sidebar đang collapsed (ẩn) – trượt sang trái */
    section[data-testid="stSidebar"][aria-expanded="false"] {{
        opacity: 0;
        transform: translateX(-20px);
    }}
    /* Khi sidebar mở – trượt vào từ trái */
    section[data-testid="stSidebar"][aria-expanded="true"] {{
        opacity: 1;
        transform: translateX(0);
    }}

    /* Nội dung bên trong sidebar fade-in sau khi sidebar mở */
    section[data-testid="stSidebar"] > div {{
        transition: opacity 0.35s ease 0.1s;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] > div {{
        opacity: 0;
    }}
    section[data-testid="stSidebar"][aria-expanded="true"] > div {{
        opacity: 1;
    }}

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li,
    section[data-testid="stSidebar"] code {{
        color: {TEXT_SECONDARY} !important;
    }}
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] strong {{
        color: {SIDEBAR_STAR} !important;
    }}

    /* ─── Sidebar Toggle Arrow – cố định giữa trang theo chiều dọc ─── */
    [data-testid="collapsedControl"] {{
        position: fixed !important;
        top: 50vh !important;
        transform: translateY(-50%) !important;
        background: {ARROW_BG} !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 0 20px {ARROW_GLOW}, 0 4px 16px rgba(0,0,0,0.3) !important;
        border: 1px solid rgba(255,255,255,0.25) !important;
        transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1) !important;
        z-index: 999 !important;
    }}
    [data-testid="collapsedControl"]:hover {{
        box-shadow: 0 0 32px {ARROW_H_GLOW}, 0 6px 24px rgba(0,0,0,0.4) !important;
        transform: translateY(-50%) scale(1.14) !important;
    }}
    [data-testid="collapsedControl"] svg {{
        fill: white !important;
        transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }}

    /* ─── Header ─── */
    .main-header {{
        text-align: center;
        padding: 2.2rem 0 0.4rem;
        background: {HEADER_GRAD};
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-family: 'Outfit', sans-serif;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1px;
        animation: shine 4s linear infinite;
    }}

    @keyframes shine {{
        to {{ background-position: 200% center; }}
    }}

    .sub-header {{
        text-align: center;
        color: {SUB_H_COLOR};
        font-size: 1.05rem;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.3px;
    }}

    /* ─── Divider ─── */
    .fancy-divider {{
        width: 80px;
        height: 3px;
        background: {DIVIDER_GRAD};
        border-radius: 999px;
        margin: 0 auto 2.5rem;
        box-shadow: 0 0 12px {DIVIDER_GLOW};
    }}

    /* ─── Theme toggle badge ─── */
    .theme-badge {{
        text-align: center;
        font-size: 0.78rem;
        color: {TEXT_SECONDARY};
        margin-top: -1.8rem;
        margin-bottom: 2rem;
        opacity: 0.75;
    }}

    /* ─── Glass Card ─── */
    .glass-card {{
        background: {CARD_BG};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 28px 32px;
        box-shadow: {CARD_SHADOW};
        transition: transform 0.35s cubic-bezier(0.22,1,0.36,1), box-shadow 0.35s ease, background 0.4s ease;
        margin-bottom: 24px;
    }}
    .glass-card:hover {{
        transform: translateY(-6px);
        box-shadow: {CARD_HOVER_SH};
    }}

    /* ─── School Tag ─── */
    .school-tag {{
        background: linear-gradient(90deg, #3b82f6, #6366f1);
        color: white !important;
        padding: 4px 14px;
        border-radius: 99px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-left: 12px;
        display: inline-block;
        vertical-align: middle;
        box-shadow: 0 4px 12px rgba(99,102,241,0.35);
        letter-spacing: 0.5px;
    }}

    /* ─── Selectbox ─── */
    div[data-baseweb="select"] > div {{
        border-radius: 14px !important;
        border: 1.5px solid {SELECT_BORDER} !important;
        background: {SELECT_BG} !important;
        color: {SELECT_TEXT} !important;
        font-size: 1rem;
        transition: all 0.25s ease;
    }}
    div[data-baseweb="select"] > div:hover {{
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59,130,246,0.15) !important;
    }}
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] [data-testid="stSelectbox"] span {{
        color: {SELECT_TEXT} !important;
    }}
    /* Dropdown list items */
    ul[data-testid="stSelectboxVirtualDropdown"] li,
    [data-baseweb="menu"] li {{
        color: {TEXT_PRIMARY} !important;
        background: {SELECT_BG} !important;
    }}

    /* ─── Fetch Button ─── */
    .fetch-btn-wrap {{
        margin-top: 1rem;
    }}
    .fetch-btn-wrap button {{
        width: 100% !important;
        background: {BTN_GRAD} !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 14px 20px !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.3px !important;
        cursor: pointer;
        transition: all 0.3s ease !important;
        box-shadow: {BTN_SHADOW} !important;
    }}
    .fetch-btn-wrap button:hover {{
        background: {BTN_HOVER} !important;
        box-shadow: {BTN_HOVER_SH} !important;
        transform: translateY(-2px) !important;
    }}
    .fetch-btn-wrap button:active {{
        transform: translateY(0px) !important;
    }}

    /* ─── Tabs ─── */
    button[data-baseweb="tab"] {{
        color: {TAB_COLOR} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        padding: 10px 20px !important;
        border-radius: 10px 10px 0 0 !important;
        transition: all 0.25s ease !important;
    }}
    button[data-baseweb="tab"]:hover {{
        color: {TAB_ACTIVE} !important;
        background: rgba(59,130,246,0.07) !important;
    }}
    button[aria-selected="true"][data-baseweb="tab"] {{
        color: {TAB_ACTIVE} !important;
        border-bottom: 3px solid {TAB_ACTIVE_BD} !important;
        background: rgba(59,130,246,0.08) !important;
    }}

    /* ─── Expander ─── */
    .streamlit-expanderHeader {{
        background: {EXP_BG} !important;
        border-radius: 12px !important;
        border: 1px solid {EXP_BORDER} !important;
        color: {EXP_TEXT} !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 12px 16px !important;
        transition: all 0.2s ease !important;
    }}
    .streamlit-expanderHeader:hover {{
        background: {EXP_HOVER_BG} !important;
        border-color: {EXP_HOVER_BD} !important;
    }}

    /* ─── Metric ─── */
    div[data-testid="metric-container"] {{
        background: {METRIC_BG} !important;
        border: 1px solid {METRIC_BORDER} !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: background 0.4s ease;
    }}
    div[data-testid="metric-container"] label {{
        color: {METRIC_LABEL} !important;
        font-weight: 500 !important;
    }}
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {{
        color: {METRIC_VALUE} !important;
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }}
    div[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
        color: #22c55e !important;
    }}

    /* ─── Chart area ─── */
    .stVegaLiteChart, .element-container [data-testid="stArrowVegaLiteChart"] {{
        background: {CHART_BG} !important;
        border-radius: 14px !important;
        padding: 12px !important;
        border: 1px solid {CHART_BORDER} !important;
    }}

    /* ─── Headings ─── */
    h1, h2, h3 {{
        color: {H_COLOR} !important;
        transition: color 0.3s ease;
    }}

    /* ─── Sidebar info badge ─── */
    .sidebar-info {{
        background: {SBAR_INFO_BG};
        border: 1px solid {SBAR_INFO_BD};
        border-radius: 10px;
        padding: 12px;
        margin-top: 16px;
        font-size: 0.85rem;
        color: {SBAR_INFO_TXT};
        line-height: 1.7;
        transition: all 0.4s ease;
    }}

    /* ─── Dataframe ─── */
    .stDataFrame {{
        border-radius: 12px !important;
        overflow: hidden;
        border: 1px solid {CARD_BORDER} !important;
    }}

    /* ─── Alerts ─── */
    .stAlert {{
        border-radius: 12px !important;
    }}

    /* ─── Warning ─── */
    div[data-testid="stNotification"] {{
        border-radius: 12px !important;
    }}

    /* ─── Smooth page transition ─── */
    .main .block-container {{
        transition: opacity 0.3s ease;
        animation: fadeIn 0.4s ease;
    }}
    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(8px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  Config
# ══════════════════════════════════════════════════════════════
API_BASE = "http://localhost:8000/api"

@st.cache_data(ttl=60)
def fetch_search_options():
    try:
        response = requests.get(f"{API_BASE}/search")
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
    return []

# ══════════════════════════════════════════════════════════════
#  SIDEBAR – Admin Panel
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"## 🛠️ Quản trị Data")
    st.markdown(f"<hr style='border:1px solid {SIDEBAR_BORDER}; margin:8px 0 16px'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div style="font-size:0.88rem; color:{TEXT_SECONDARY}; margin-bottom:16px; line-height:1.75;">
        Nhấn nút bên dưới để crawler thu thập toàn bộ dữ liệu chương trình đào tạo từ
        <strong style="color:{TEXT_ACCENT};">NEU</strong> và lưu vào cơ sở dữ liệu.
    </div>
    """, unsafe_allow_html=True)

    # ── Nút Fetch ──
    st.markdown('<div class="fetch-btn-wrap">', unsafe_allow_html=True)
    clicked = st.button("🚀  Cập nhật dữ liệu mới nhất", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if clicked:
        with st.spinner("⏳ Đang kết nối crawler..."):
            try:
                res = requests.post(f"{API_BASE}/sync")
                if res.status_code == 200:
                    st.success("✅ " + res.json().get("message", "Đồng bộ thành công!"))
                    fetch_search_options.clear()
                else:
                    st.error("❌ Lỗi khi đồng bộ dữ liệu!")
            except Exception as e:
                st.error(f"⚠️ Lỗi kết nối: {e}")

    st.markdown(f"""
    <div class="sidebar-info">
        📡 <strong>API Backend:</strong><br>
        <code style="color:{TEXT_ACCENT}; font-size:0.8rem;">localhost:8000</code><br><br>
        🗄️ <strong>Database:</strong> SQLite local<br>
        🔄 <strong>Cache TTL:</strong> 60 giây
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="margin-top:24px; padding:10px; border-radius:8px; background:{SBAR_INFO_BG};
                border:1px solid {SBAR_INFO_BD}; text-align:center; font-size:0.8rem; color:{TEXT_SECONDARY};">
        {TOGGLE_ICON} <strong>Phím tắt:</strong> Nhấn <kbd style="
            background:rgba(59,130,246,0.15); border:1px solid rgba(59,130,246,0.3);
            border-radius:4px; padding:1px 6px; font-family:monospace;
            color:{TEXT_ACCENT};">D</kbd> để đổi giao diện
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  MAIN CONTENT
# ══════════════════════════════════════════════════════════════
search_options = fetch_search_options()

st.markdown('<div class="main-header">🎓 NEU Course Explorer</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-header">Tra cứu điểm chuẩn &amp; lộ trình đào tạo · Đại học Kinh tế Quốc dân</div>',
            unsafe_allow_html=True)
st.markdown(f'<div class="theme-badge">{TOGGLE_ICON} Đang dùng {"Dark" if IS_DARK else "Light"} Mode · Nhấn <kbd style="font-family:monospace;font-size:0.75rem;">D</kbd> để đổi</div>',
            unsafe_allow_html=True)
st.markdown('<div class="fancy-divider"></div>', unsafe_allow_html=True)

if not search_options:
    st.warning("⚠️ Chưa có dữ liệu. Vui lòng mở **Sidebar → Cập nhật dữ liệu mới nhất** để bắt đầu thu thập.")
    st.stop()

# ── Search Bar ──
col1, col2, col3 = st.columns([1, 2.5, 1])
with col2:
    options_dict = {item["display_name"]: item["id"] for item in search_options}
    selected_display_name = st.selectbox(
        "Tìm ngành",
        options=["🔍  Chọn mã xét tuyển hoặc tên ngành..."] + list(options_dict.keys()),
        index=0,
        label_visibility="collapsed"
    )

st.markdown("<br>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  DETAIL VIEW
# ══════════════════════════════════════════════════════════════
if selected_display_name and selected_display_name != "🔍  Chọn mã xét tuyển hoặc tên ngành...":
    major_id = options_dict[selected_display_name]

    with st.spinner("✨ Đang tải dữ liệu..."):
        try:
            res = requests.get(f"{API_BASE}/curriculum/{major_id}")
            if res.status_code == 200:
                item = res.json()

                # ── Major Header Card ──
                st.markdown(f"""
                <div class="glass-card">
                    <h2 style="margin:0; color:{MAJOR_H_COLOR}; font-weight:700; font-size:1.6rem; font-family:'Outfit',sans-serif;">
                        {item.get('major_name', 'Chưa có tên')}
                        <span class="school-tag">{item.get('school', 'NEU')}</span>
                    </h2>
                    <p style="color:{MAJOR_P_COLOR}; font-weight:600; margin-top:10px; font-size:1.05rem; letter-spacing:0.3px;">
                        🏷️ Mã xét tuyển: <strong style="color:{MAJOR_CODE_C};">{item.get('major_code', 'N/A')}</strong>
                    </p>
                </div>
                """, unsafe_allow_html=True)

                tab1, tab2 = st.tabs(["📈  Điểm chuẩn (Dự kiến)", "📚  Lộ trình học (Dự kiến)"])

                # ── Tab 1: Scores ──
                with tab1:
                    st.markdown(f"### 📊 Lịch sử Điểm chuẩn")
                    scores = item.get('scores', {})
                    if not scores:
                        st.info("ℹ️ Nhà trường chưa công bố hoặc chưa cập nhật dữ liệu điểm chuẩn cho ngành này.")
                    else:
                        df_scores = pd.DataFrame(
                            list(scores.items()), columns=['Năm', 'Điểm chuẩn']
                        ).set_index('Năm')
                        col_chart, col_metric = st.columns([2, 1])
                        with col_chart:
                            st.line_chart(df_scores, use_container_width=True)
                        with col_metric:
                            latest_year  = list(scores.keys())[-1]
                            latest_score = scores[latest_year]
                            st.metric(
                                label=f"🏆 Điểm chuẩn {latest_year}",
                                value=latest_score,
                                delta="Cập nhật mới nhất"
                            )

                # ── Tab 2: Curriculum ──
                with tab2:
                    st.markdown("### 🗺️ Chương trình đào tạo")
                    curriculum = item.get('curriculum', [])
                    if not curriculum:
                        st.info("ℹ️ Hệ thống đang thu thập chi tiết môn học cho ngành này. Vui lòng quay lại sau!")
                    else:
                        for sem_data in curriculum:
                            sem_num = sem_data.get('semester', sem_data.get('year', '?'))
                            with st.expander(f"📌  Học kỳ {sem_num} – Danh sách môn học", expanded=(sem_num == 1)):
                                subjects = sem_data.get('subjects', [])
                                if not subjects:
                                    st.write("Chưa có môn học nào.")
                                else:
                                    df_subjects = pd.DataFrame(subjects)
                                    col_map = {"code": "Mã môn", "name": "Tên môn", "credits": "Số tín chỉ"}
                                    df_subjects.rename(columns=col_map, inplace=True)
                                    display_cols = [c for c in ["Mã môn", "Tên môn", "Số tín chỉ"]
                                                    if c in df_subjects.columns]
                                    df_subjects = df_subjects[display_cols]
                                    df_subjects.index = df_subjects.index + 1
                                    st.dataframe(
                                        df_subjects,
                                        use_container_width=True,
                                        column_config={
                                            "Mã môn":    st.column_config.TextColumn("Mã môn",   width="medium"),
                                            "Tên môn":   st.column_config.TextColumn("Tên môn học", width="large"),
                                            "Số tín chỉ": st.column_config.NumberColumn("Tín chỉ", width="small")
                                        }
                                    )
            else:
                st.error("❌ Không tìm thấy thông tin chi tiết cho ngành này.")
        except Exception as e:
            st.error(f"❌ Lỗi kết nối hệ thống Backend: {e}")
