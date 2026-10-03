import streamlit as st

def apply_claymorphism_theme():
    """Inject Dark Navy / Indigo Cyber Command Center Theme matching the reference screenshot."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    :root {
        --bg-page: #070B18;
        --bg-card: #11182E;
        --bg-card-elevated: #151D38;
        --bg-input: #18213D;
        
        --border-purple: rgba(139, 92, 246, 0.25);
        --border-purple-bright: rgba(168, 85, 247, 0.45);
        
        --text-primary: #FFFFFF;
        --text-secondary: #E5E7EB;
        --text-muted: #9CA3AF;
        
        --accent-purple: #8B5CF6;
        --accent-violet: #A855F7;
        --accent-magenta: #EC4899;
        --accent-cyan: #06B6D4;
        
        --success-emerald: #10B981;
        --danger-red: #EF4444;
        --warning-amber: #F59E0B;
        --warning-orange: #F97316;
    }

    /* Force Deep Dark Background on All Page Containers */
    html, body, .stApp, 
    [data-testid="stAppViewContainer"], 
    [data-testid="stHeader"], 
    [data-testid="stSidebarContent"], 
    .main, section.main, 
    [data-testid="stMain"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        background-color: #070B18 !important;
        background: #070B18 !important;
        color: var(--text-secondary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    /* Suppress Streamlit Default Header, Toolbar, Footer, & Chrome */
    header[data-testid="stHeader"],
    [data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stToolbar"],
    #MainMenu,
    footer,
    .stApp > header {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    /* Main Container Padding & Width */
    .block-container {
        max-width: 1600px !important;
        padding-top: 0.2rem !important;
        padding-bottom: 2.0rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
        margin-top: 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Ensure text colors are bright and visible */
    p, span, label, div, h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] span {
        color: var(--text-secondary);
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }

    /* Sidebar Styling - Dark Navy / Indigo Panel */
    [data-testid="stSidebar"] {
        min-width: 270px !important;
        max-width: 290px !important;
        width: 280px !important;
        background-color: #0F1428 !important;
        background: linear-gradient(180deg, #11162B 0%, #080B18 100%) !important;
        border-right: 1px solid var(--border-purple) !important;
        padding-top: 0 !important;
        margin-top: 0 !important;
        z-index: 2 !important;
    }

    [data-testid="stSidebarHeader"] {
        display: none !important;
        height: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebarUserContent"] {
        padding-top: 1.2rem !important;
        padding-left: 1.0rem !important;
        padding-right: 1.0rem !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-secondary) !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        color: #E5E7EB !important;
        font-weight: 600 !important;
        font-size: 13px !important;
    }

    /* Sidebar Controls (Inputs & Selectboxes) */
    [data-testid="stSidebar"] [data-testid="stTextInput"] input {
        background-color: #151D38 !important;
        background: #151D38 !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        font-size: 13px !important;
    }

    /* ULTRA SPECIFIC SIDEBAR SELECTBOX RULES */
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] label * {
        background-color: transparent !important;
        background: transparent !important;
        color: #E5E7EB !important;
        -webkit-text-fill-color: #E5E7EB !important;
    }

    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] *,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] input,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] button,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [role="combobox"],
    html body section[data-testid="stSidebar"] [data-baseweb="select"],
    html body section[data-testid="stSidebar"] [data-baseweb="select"] *,
    html body section[data-testid="stSidebar"] .st-emotion-cache-zfrvrb,
    html body section[data-testid="stSidebar"] .e1fp86qc1,
    html body section[data-testid="stSidebar"] .e1fp86qc2,
    html body section[data-testid="stSidebar"] .e1fp86qc0 {
        background-color: #11182E !important;
        background: #11182E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    html body section[data-testid="stSidebar"] div[data-baseweb="select"] {
        border-radius: 10px !important;
    }

    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] div[role="combobox"],
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] .st-emotion-cache-zfrvrb,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] .e1fp86qc1 {
        border: 1px solid rgba(139, 92, 246, 0.45) !important;
        border-radius: 10px !important;
        background-color: #11182E !important;
        background: #11182E !important;
    }

    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] svg,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] path,
    html body section[data-testid="stSidebar"] div[data-testid="stSelectbox"] [data-baseweb="icon"] {
        fill: #C4B5FD !important;
        color: #C4B5FD !important;
        background-color: transparent !important;
        background: transparent !important;
    }

    /* Selectbox Hover & Focus States */
    html body section[data-testid="stSidebar"] [data-baseweb="select"]:hover > div,
    html body section[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {
        border-color: #A855F7 !important;
        background-color: #151D38 !important;
        background: #151D38 !important;
    }

    html body section[data-testid="stSidebar"] [data-baseweb="select"]:focus-within > div {
        border-color: #A855F7 !important;
        box-shadow: 0 0 0 2px rgba(168, 85, 247, 0.3) !important;
    }

    /* Radio Controls in Sidebar */
    html body section[data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label span {
        color: #F3F4F6 !important;
    }

    /* Dropdown Popover Menu & Option List */
    html body div[data-baseweb="popover"],
    html body div[data-baseweb="menu"],
    html body ul[data-baseweb="menu"],
    html body div[role="listbox"],
    html body ul[role="listbox"],
    html body [data-testid="stSidebar"] [data-baseweb="popover"] {
        background-color: #11182E !important;
        background: #11182E !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        border-radius: 10px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.6) !important;
    }

    html body div[data-baseweb="popover"] *,
    html body div[data-baseweb="menu"] *,
    html body ul[data-baseweb="menu"] *,
    html body div[role="listbox"] *,
    html body ul[role="listbox"] * {
        background-color: #11182E !important;
        background: #11182E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    html body li[role="option"],
    html body div[role="option"] {
        background-color: #11182E !important;
        background: #11182E !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        padding: 10px 14px !important;
    }

    html body li[role="option"]:hover,
    html body li[role="option"][aria-selected="true"],
    html body div[role="option"]:hover,
    html body div[role="option"][aria-selected="true"] {
        background-color: #25204A !important;
        background: #25204A !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
    }

    /* Sidebar Buttons */
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"],
    [data-testid="stSidebar"] [data-testid="stButton"] button[type="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        min-height: 44px !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover,
    [data-testid="stSidebar"] [data-testid="stButton"] button[type="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
    [data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) {
        background-color: #151D38 !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        border-radius: 12px !important;
        color: #F3F4F6 !important;
        font-size: 13px !important;
        min-height: 42px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #A855F7 !important;
        background-color: #202A4A !important;
    }

    /* Slider track & thumb styling */
    [data-testid="stSidebar"] [data-baseweb="slider"] div {
        color: #A855F7 !important;
    }

    /* Custom Section Cards System */
    .cmd-card {
        background-color: #11182E;
        background: linear-gradient(145deg, #151D38 0%, #0F1629 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }

    /* Top Hero Header Panel */
    .cmd-hero {
        background: linear-gradient(135deg, #1A1438 0%, #11182E 70%, #0F1428 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.22);
        display: flex;
        align-items: center;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
    }

    .hero-badge-tag {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-right: 6px;
        margin-bottom: 4px;
        background: rgba(24, 33, 61, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    .tag-violet { border-color: #8B5CF6; color: #C4B5FD; }
    .tag-blue { border-color: #3B82F6; color: #93C5FD; }
    .tag-emerald { border-color: #10B981; color: #A7F3D0; }
    .tag-amber { border-color: #F59E0B; color: #FDE68A; }
    .tag-magenta { border-color: #EC4899; color: #FBCFE8; }

    /* Security Verification Result Banners */
    .cmd-panel-valid {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.15) 0%, #11182E 100%);
        border: 1px solid rgba(16, 185, 129, 0.4);
        border-left: 5px solid #10B981;
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.15);
    }

    .cmd-panel-threat {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.15) 0%, #11182E 100%);
        border: 1px solid rgba(239, 68, 68, 0.4);
        border-left: 5px solid #EF4444;
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 6px 20px rgba(239, 68, 68, 0.15);
    }

    .cmd-panel-invisible {
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.15) 0%, #11182E 100%);
        border: 1px solid rgba(245, 158, 11, 0.4);
        border-left: 5px solid #F59E0B;
        border-radius: 14px;
        padding: 16px 22px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 6px 20px rgba(245, 158, 11, 0.15);
    }

    /* Summary Tiles Grid */
    .cmd-tile-grid {
        display: grid;
        grid-template-columns: repeat(6, 1fr);
        gap: 10px;
    }

    .cmd-tile-status {
        background-color: #151D38;
        background: linear-gradient(145deg, #182242 0%, #11172D 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px;
        padding: 12px 14px;
        min-height: 76px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .cmd-tile-lbl {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #9CA3AF;
        margin-bottom: 4px;
        font-weight: 600;
    }

    .cmd-tile-val {
        font-size: 13px;
        font-weight: 700;
        line-height: 1.2;
        white-space: normal;
        word-break: break-word;
    }

    /* Flow Step Row */
    .cmd-flow-row {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: nowrap;
    }

    .cmd-flow-box {
        background-color: #151D38;
        background: linear-gradient(145deg, #17203F 0%, #11172D 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px;
        padding: 12px 14px;
        flex: 1;
        min-width: 110px;
    }

    .cmd-flow-arrow {
        color: #A855F7;
        font-weight: 800;
        font-size: 18px;
        padding: 0 4px;
    }

    .cmd-terminal-box {
        background-color: #0B0F1F;
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 8px;
        padding: 6px 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #C4B5FD;
    }

    /* Attack Scenario Cards Grid */
    .cmd-scenario-grid {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 12px;
    }

    .cmd-scenario-tile {
        border-radius: 12px;
        padding: 14px 16px;
        background: #151D38;
        background: linear-gradient(145deg, #182242 0%, #11172D 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
    }

    .tile-genuine { border-left: 4px solid #10B981; }
    .tile-forgery { border-left: 4px solid #EF4444; }
    .tile-impersonation { border-left: 4px solid #F59E0B; }
    .tile-replay { border-left: 4px solid #F97316; }
    .tile-channel { border-left: 4px solid #8B5CF6; }

    /* 2x2 Readout Grid (Right Column Cards) */
    .cmd-readout-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }

    .cmd-readout-box {
        background-color: #151D38;
        background: linear-gradient(145deg, #182242 0%, #11172D 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 10px;
        padding: 14px 12px;
        text-align: center;
    }

    .cmd-readout-lbl {
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #9CA3AF;
        margin-bottom: 6px;
        font-weight: 600;
    }

    .cmd-readout-val {
        font-size: 18px;
        font-weight: 800;
        color: #FFFFFF;
    }

    .val-emerald { color: #10B981 !important; }
    .val-red { color: #EF4444 !important; }
    .val-cyan { color: #06B6D4 !important; }
    .val-amber { color: #F59E0B !important; }
    .val-violet { color: #A855F7 !important; }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #070B18;
    }
    ::-webkit-scrollbar-thumb {
        background: #1D264A;
        border-radius: 4px;
        border: 1px solid rgba(139, 92, 246, 0.3);
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #A855F7;
    }
    </style>
    """, unsafe_allow_html=True)

    import streamlit.components.v1 as components
    st.html("""
    <script>
    (function() {
        const applyDarkSelectboxStyles = () => {
            try {
                const doc = window.parent ? window.parent.document : document;
                if (!doc) return;
                const selectboxes = doc.querySelectorAll('[data-testid="stSidebar"] [data-testid="stSelectbox"]');
                selectboxes.forEach(sb => {
                    const nodes = sb.querySelectorAll('div, input, button, span, [data-baseweb="select"]');
                    nodes.forEach(node => {
                        const tag = node.tagName.toLowerCase();
                        if (tag === 'label' || node.closest('label') === node) return;
                        if (tag === 'svg' || tag === 'path') {
                            node.style.setProperty('fill', '#C4B5FD', 'important');
                            node.style.setProperty('color', '#C4B5FD', 'important');
                            return;
                        }
                        node.style.setProperty('background-color', '#11182E', 'important');
                        node.style.setProperty('background', '#11182E', 'important');
                        node.style.setProperty('color', '#FFFFFF', 'important');
                        node.style.setProperty('-webkit-text-fill-color', '#FFFFFF', 'important');
                    });
                    const outer = sb.querySelector('[data-baseweb="select"] > div') || sb.querySelector('[data-baseweb="select"]');
                    if (outer) {
                        outer.style.setProperty('border', '1px solid rgba(139, 92, 246, 0.45)', 'important');
                        outer.style.setProperty('border-radius', '10px', 'important');
                    }
                });
            } catch(e) {}
        };
        setInterval(applyDarkSelectboxStyles, 150);
        applyDarkSelectboxStyles();
    })();
    </script>
    """)
