import streamlit as st
import html

def inject_css():
    """Injects custom CSS for a clean, light, professional UI matching the reference design."""
    st.markdown("""
    <style>
        /* --- 1. CORE THEME (Light, Clean, Professional) --- */
        .stApp {
            background-color: #F4F6F8;
            color: #2C3E50;
            font-family: 'Segoe UI', 'Inter', 'Helvetica Neue', sans-serif;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {background-color: transparent;}

        /* --- 2. TYPOGRAPHY & COLORS --- */
        h1, h2, h3 { color: #008080; font-weight: 600; letter-spacing: -0.5px; }
        h4 { color: #008080; font-weight: 500; }
        p, li { line-height: 1.7; color: #4A5568; }

        /* --- 3. CARDS & CONTAINERS --- */
        .mr-card {
            background-color: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        .mr-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 12px rgba(0, 0, 0, 0.08);
        }

        .mr-qcard {
            background: #FFFFFF;
            border-left: 5px solid #008080;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }
        .mr-domain {
            color: #008080;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            font-weight: 600;
            margin-bottom: 8px;
        }
        .mr-qtext {
            font-size: 1.1rem;
            color: #2D3748;
            font-weight: 500;
        }

        .mr-letter {
            background: #FFFFFF;
            border: 1px solid #CBD5E0;
            border-left: 4px solid #008080;
            border-radius: 8px;
            padding: 24px;
            font-family: 'Georgia', 'Times New Roman', serif;
            font-size: 1.05rem;
            line-height: 1.8;
            color: #2D3748;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }
        .sig {
            text-align: right;
            color: #008080;
            font-style: italic;
            margin-top: 15px;
            font-weight: 600;
        }

        .mr-crisis {
            background: #FFF5F5;
            border: 1px solid #FED7D7;
            border-left: 4px solid #E53E3E;
            border-radius: 8px;
            padding: 16px;
            color: #C53030;
            margin-bottom: 20px;
        }

        .stButton > button {
            background-color: #008080;
            color: #FFFFFF;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            background-color: #006666;
            transform: translateY(-2px);
        }
        .stButton > button[disabled] {
            background-color: #E2E8F0;
            color: #A0AEC0;
            cursor: not-allowed;
        }

        .stTabs [data-baseweb="tab-list"] { gap: 12px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #EDF2F7;
            border-radius: 8px;
            color: #4A5568;
        }
        .stTabs [aria-selected="true"] {
            background-color: #008080;
            color: #FFFFFF;
            font-weight: 600;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 12px;
        }
        div[data-testid="stMetricValue"] { font-size: 1.5rem; color: #008080; }
        
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E2E8F0;
        }
        .sidebar .stMarkdown { color: #4A5568; }
    </style>
    """, unsafe_allow_html=True)

def hero_header(title, subtitle, chips):
    safe_title = html.escape(title)
    safe_subtitle = html.escape(subtitle)
    chips_html = "".join([
        f'<div style="background:#FFFFFF; padding: 6px 16px; border-radius: 20px; '
        f'font-size: 0.8rem; color: #008080; border: 1px solid #008080; '
        f'box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: inline-block; margin: 4px;">'
        f'{html.escape(chip)}</div>' 
        for chip in chips
    ])

    st.markdown(f"""
        <div style='text-align: center; margin-bottom: 3rem; padding: 2rem 1rem;'>
            <h1 style='color: #008080; font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem;'>
                {safe_title}
            </h1>
            <p style='font-size: 1.2rem; color: #4A5568; max-width: 700px; margin: 0 auto 2rem auto;'>
                {safe_subtitle}
            </p>
            <div style='margin-top: 2rem; display: flex; justify-content: center; flex-wrap: wrap; gap: 10px;'>
                {chips_html}
            </div>
        </div>
    """, unsafe_allow_html=True)

def render_crisis_banner(helplines):
    st.markdown("""
    <div class="mr-crisis">
        <h4 style="margin-top:0;">🚨 In Immediate Crisis?</h4>
        <p style="margin-bottom:15px;">You do not need to complete a check-in to get help. Support is confidential and 24/7.</p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    for i, h in enumerate(helplines):
        col = cols[i % 2]
        with col:
            st.markdown(f"""
            <div style="background: #FFFFFF; padding: 15px; border-radius: 10px; border: 1px solid #E2E8F0; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
                <strong style="color: #E53E3E;">{html.escape(h['name'])}</strong><br>
                <a href="tel:{html.escape(h['number'])}" style="font-size: 1.3rem; font-weight: 700; color: #008080; text-decoration: none;">
                    📞 {html.escape(h['number'])}
                </a>
            </div>
            """, unsafe_allow_html=True)
