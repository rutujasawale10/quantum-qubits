import streamlit as st

def apply_claymorphism_theme():
    """Inject Dark Navy / Indigo Cyber Command Center Theme matching the visual reference image."""
    st.markdown("""
    <style>
    :root {
        --bg-page: #0B0E17;
        --bg-card: #121526;
        --bg-card-elevated: #16192E;
        --bg-input: #1A1D33;
        
        --border-purple: rgba(139, 92, 246, 0.25);
        --border-purple-bright: rgba(168, 85, 247, 0.45);
        
        --text-primary: #F3F4F6;
        --text-secondary: #9CA3AF;
        --text-muted: #6B7280;
        
        --accent-purple: #8B5CF6;
        --accent-violet: #A855F7;
        --accent-magenta: #EC4899;
        --accent-cyan: #06B6D4;
        
        --success-emerald: #10B981;
        --danger-red: #EF4444;
        --warning-amber: #F59E0B;
        --warning-orange: #F97316;
    }

    /* Base Page Setup */
    .stApp {
        background-color: var(--bg-page) !important;
        color: var(--text-primary) !important;
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
        max-width: 1560px !important;
        padding-top: 0.2rem !important;
        padding-bottom: 2.0rem !important;
        margin-top: 0 !important;
        position: relative !important;
        z-index: 1 !important;
    }

    /* Sidebar Styling - Dark Navy / Indigo Panel */
    [data-testid="stSidebar"] {
        min-width: 270px !important;
        max-width: 285px !important;
        width: 275px !important;
        background-color: #121526 !important;
        background: linear-gradient(180deg, #14172B 0%, #0E101D 100%) !important;
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
        padding-top: 1.0rem !important;
    }

    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    [data-testid="stSidebar"] .stCaption {
        color: var(--text-secondary) !important;
    }

    /* Inputs in Sidebar */
    [data-testid="stSidebar"] [data-testid="stTextInput"] input,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] > div {
        background-color: #1A1D33 !important;
        background: #1A1D33 !important;
        border: 1px solid rgba(139, 92, 246, 0.3) !important;
        border-radius: 10px !important;
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
    }

    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] span,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] p,
    [data-testid="stSidebar"] [data-testid="stSelectbox"] [data-baseweb="select"] div[role="button"] {
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
    }

    /* Dropdown Popover Menu */
    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"],
    div[role="listbox"] {
        background-color: #16192E !important;
        border: 1px solid rgba(168, 85, 247, 0.4) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5) !important;
    }

    li[role="option"] {
        background-color: #16192E !important;
        color: #F3F4F6 !important;
        -webkit-text-fill-color: #F3F4F6 !important;
    }

    li[role="option"]:hover,
    li[role="option"][aria-selected="true"] {
        background-color: #261D45 !important;
        color: #A855F7 !important;
        -webkit-text-fill-color: #A855F7 !important;
    }

    /* Buttons in Sidebar */
    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A855F7 100%) !important;
        border: none !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        min-height: 44px !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4) !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(168, 85, 247, 0.6) !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"],
    [data-testid="stSidebar"] [data-testid="stButton"] button:not([kind="primary"]) {
        background-color: #1A1D33 !important;
        border: 1px solid rgba(139, 92, 246, 0.35) !important;
        border-radius: 12px !important;
        color: #F3F4F6 !important;
        min-height: 42px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button[kind="secondary"]:hover {
        border-color: #A855F7 !important;
        background-color: #242845 !important;
    }

    /* Custom Cards System */
    .cmd-card {
        background-color: #121526;
        background: linear-gradient(145deg, #15182B 0%, #101221 100%);
        border: 1px solid rgba(139, 92, 246, 0.22);
        border-radius: 16px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.35);
    }

    /* Top Hero Header Panel */
    .cmd-hero {
        background: linear-gradient(135deg, #1D153B 0%, #121526 70%, #0F1221 100%);
        border: 1px solid rgba(168, 85, 247, 0.35);
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 10px 30px rgba(124, 58, 237, 0.2);
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
        background: rgba(26, 29, 51, 0.8);
        border: 1px solid rgba(139, 92, 246, 0.3);
    }

    .tag-violet { border-color: #8B5CF6; color: #C4B5FD; }
    .tag-blue { border-color: #3B82F6; color: #93C5FD; }
    .tag-emerald { border-color: #10B981; color: #A7F3D0; }
    .tag-amber { border-color: #F59E0B; color: #FDE68A; }
    .tag-magenta { border-color: #EC4899; color: #FBCFE8; }

    /* Security Verification Result Card */
    .cmd-panel-valid {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, #121526 100%);
        border: 1px solid rgba(16, 185, 129, 0.35);
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
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.12) 0%, #121526 100%);
        border: 1px solid rgba(239, 68, 68, 0.35);
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
        background: linear-gradient(135deg, rgba(245, 158, 11, 0.12) 0%, #121526 100%);
        border: 1px solid rgba(245, 158, 11, 0.35);
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
    .cmd-tile-status {
        background-color: #16192E;
        background: linear-gradient(145deg, #181C33 0%, #121424 100%);
        border: 1px solid rgba(139, 92, 246, 0.22);
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
        gap: 8px;
        flex-wrap: wrap;
    }

    .cmd-flow-box {
        background-color: #16192E;
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-radius: 12px;
        padding: 12px 14px;
        flex: 1;
        min-width: 110px;
    }

    .cmd-flow-arrow {
        color: #A855F7;
        font-weight: 800;
        font-size: 16px;
    }

    .cmd-terminal-box {
        background-color: #0D0E19;
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 8px;
        padding: 6px 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: #C4B5FD;
    }

    /* Attack Scenario Cards Grid */
    .cmd-scenario-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(110px, 1fr));
        gap: 10px;
    }

    .cmd-scenario-tile {
        border-radius: 12px;
        padding: 12px;
        background: #16192E;
        border: 1px solid rgba(139, 92, 246, 0.2);
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
        gap: 10px;
    }

    .cmd-readout-box {
        background-color: #1A1D33;
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 10px;
        padding: 12px 10px;
        text-align: center;
    }

    .cmd-readout-lbl {
        font-size: 9px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #9CA3AF;
        margin-bottom: 4px;
    }

    .cmd-readout-val {
        font-size: 18px;
        font-weight: 800;
        color: #F3F4F6;
    }

    .val-emerald { color: #10B981 !important; }
    .val-red { color: #EF4444 !important; }
    .val-cyan { color: #06B6D4 !important; }
    .val-amber { color: #F59E0B !important; }
    .val-violet { color: #A855F7 !important; }
    </style>
    """, unsafe_allow_html=True)
