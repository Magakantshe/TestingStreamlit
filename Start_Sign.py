import streamlit as st
import pandas as pd
from datetime import datetime
import re
import base64

# ============================================
# PAGE CONFIGURATION
# ============================================

st.set_page_config(
    page_title="Life Path & Zodiac Personality App",
    page_icon="🔮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 2rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .main-header h1 {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
    }
    .result-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        color: white;
        margin: 1rem 0;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .result-card .life-path-number {
        font-size: 5rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 20px rgba(102,126,234,0.4);
    }
    .career-highlight {
        background: linear-gradient(120deg, #84fab0 0%, #8fd3f4 100%);
        padding: 0.2rem 0.5rem;
        border-radius: 8px;
        font-weight: bold;
        color: #1a1a2e;
    }
    .strength-box {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .weakness-box {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .fade-in {
        animation: fadeIn 0.5s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    </style>
""", unsafe_allow_html=True)


# ============================================
# LOAD EXCEL DATA
# ============================================

@st.cache_data
def load_personality_data(excel_path='zodiac_lifepath_full.xlsx'):
    """Load the Excel file into a dictionary with caching"""
    data = {}
    try:
        df = pd.read_excel(excel_path, engine='openpyxl')
        for _, row in df.iterrows():
            key = (row['zodiac'], str(row['life_path']))
            
            # Extract careers from paragraph
            para2 = row['paragraph2']
            careers = extract_careers(para2)
            
            data[key] = {
                'traits': {
                    'stubborn': int(row['trait_stubborn']),
                    'kind': int(row['trait_kind']),
                    'generous': int(row['trait_generous']),
                    'loyal': int(row['trait_loyal']),
                    'patient': int(row['trait_patient']),
                    'emotional': int(row['trait_emotional']),
                    'ambitious': int(row['trait_ambitious']),
                    'creative': int(row['trait_creative']),
                    'analytical': int(row['trait_analytical'])
                },
                'paragraph1': row['paragraph1'],
                'paragraph2': row['paragraph2'],
                'careers': careers,
                'zodiac': row['zodiac'],
                'life_path': str(row['life_path'])
            }
        return data, df
    except FileNotFoundError:
        st.error(f"❌ Excel file not found! Please make sure 'zodiac_lifepath_full.xlsx' is in the same directory as this app.")
        return None, None
    except Exception as e:
        st.error(f"❌ Error loading Excel: {e}")
        return None, None


def extract_careers(text):
    """Extract career mentions from paragraph text"""
    career_patterns = [
        r'Career(?:s)?(?:\s+in|\s+recommendation|\s+suggestions?)?\s*:?\s*([^\.]+\.)',
        r'Professionally,\s*([^\.]+\.)',
    ]
    for pattern in career_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            career_text = match.group(1)
            careers = [c.strip() for c in career_text.replace('and', ',').split(',')]
            return [c for c in careers if len(c) > 3][:5]
    return ["Entrepreneurship", "Creative fields", "Leadership roles", "Communication", "Service industry"]


# ============================================
# CALCULATE LIFE PATH NUMBER
# ============================================

def calculate_life_path_number(day, month, year):
    def sum_digits(n):
        return sum(int(d) for d in str(n))
    
    day_sum = sum_digits(day)
    month_sum = sum_digits(month)
    year_sum = sum_digits(year)
    total = day_sum + month_sum + year_sum
    
    while total > 9 and total not in [11, 22, 33]:
        total = sum_digits(total)
    return total


# ============================================
# DETERMINE ZODIAC SIGN
# ============================================

def get_zodiac_sign(day, month):
    zodiacs = {
        (3,21,4,19): ("Aries", "♈", "The Ram", "Fire"),
        (4,20,5,20): ("Taurus", "♉", "The Bull", "Earth"),
        (5,21,6,20): ("Gemini", "♊", "The Twins", "Air"),
        (6,21,7,22): ("Cancer", "♋", "The Crab", "Water"),
        (7,23,8,22): ("Leo", "♌", "The Lion", "Fire"),
        (8,23,9,22): ("Virgo", "♍", "The Virgin", "Earth"),
        (9,23,10,22): ("Libra", "♎", "The Scales", "Air"),
        (10,23,11,21): ("Scorpio", "♏", "The Scorpion", "Water"),
        (11,22,12,21): ("Sagittarius", "♐", "The Archer", "Fire"),
        (12,22,1,19): ("Capricorn", "♑", "The Goat", "Earth"),
        (1,20,2,18): ("Aquarius", "♒", "The Water Bearer", "Air"),
        (2,19,3,20): ("Pisces", "♓", "The Fish", "Water")
    }
    for (start_m, start_d, end_m, end_d), (name, symbol, _, element) in zodiacs.items():
        if (month == start_m and day >= start_d) or (month == end_m and day <= end_d):
            return name, symbol, element
    return "Unknown", "❓", "Unknown"


# ============================================
# GET PERSONALITY PROFILE
# ============================================

def get_personality_profile(zodiac, life_path, data):
    key = (zodiac, str(life_path))
    if key in data:
        return data[key]
    else:
        return {
            'traits': {t:5 for t in ['stubborn','kind','generous','loyal','patient','emotional','ambitious','creative','analytical']},
            'paragraph1': f"✨ The combination of {zodiac} with Life Path {life_path} is rare and powerful. You are a unique soul.",
            'paragraph2': "Your journey is to create your own path. Trust your intuition.",
            'careers': ["Creative fields", "Leadership", "Communication", "Service", "Innovation"],
            'zodiac': zodiac,
            'life_path': str(life_path)
        }


# ============================================
# EXTRACT STRENGTHS & WEAKNESSES
# ============================================

def extract_strengths_weaknesses(paragraph):
    strengths = []
    weaknesses = []
    strength_keywords = ['natural', 'excellent', 'gift', 'strength', 'powerful', 'brilliant', 'creative', 'loyal', 'kind']
    weakness_keywords = ['shadow', 'downside', 'struggle', 'challenge', 'prone to', 'tend to']
    sentences = re.split(r'[.!?]+', paragraph)
    for sent in sentences:
        if any(kw in sent.lower() for kw in strength_keywords) and len(sent) > 15:
            strengths.append(sent.strip())
        if any(kw in sent.lower() for kw in weakness_keywords) and len(sent) > 15:
            weaknesses.append(sent.strip())
    return strengths[:3], weaknesses[:3]


# ============================================
# GENERATE HTML REPORT
# ============================================

def generate_html_report(birth_date, zodiac_name, zodiac_symbol, zodiac_element, life_path, traits, para1, para2, careers):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>Personality Report</title>
    <style>
        body {{ font-family: Georgia, serif; padding: 40px; max-width: 800px; margin: 0 auto; background: #f0f2f6; }}
        .container {{ background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        h1 {{ color: #667eea; text-align: center; }}
        .zodiac {{ font-size: 4rem; text-align: center; }}
        .life-path {{ font-size: 3rem; font-weight: bold; color: #764ba2; text-align: center; }}
        .trait-grid {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 10px; margin: 20px 0; }}
        .trait-item {{ background: #f0f2f6; padding: 8px; border-radius: 8px; }}
        .career-box {{ background: #e8f5e9; padding: 15px; border-radius: 10px; margin: 15px 0; }}
        .footer {{ text-align: center; font-size: 0.8rem; color: #999; margin-top: 30px; }}
    </style>
    </head>
    <body>
    <div class="container">
        <div class="zodiac">{zodiac_symbol}</div>
        <h1>{zodiac_name} • Life Path {life_path}</h1>
        <p style="text-align:center">{zodiac_element} Element • {birth_date.strftime('%B %d, %Y')}</p>
        <div class="life-path">{life_path}</div>
        <h2>📊 Personality Traits</h2>
        <div class="trait-grid">
    """
    for trait, score in traits.items():
        html += f'<div class="trait-item"><strong>{trait.capitalize()}</strong> {score}/10<br><progress value="{score}" max="10" style="width:100%"></progress></div>'
    html += f"""
        </div>
        <h2>💼 Recommended Careers</h2>
        <div class="career-box"><ul>
    """
    for c in careers[:5]:
        html += f"<li>{c}</li>"
    html += f"""
        </ul></div>
        <h2>📖 Character Summary</h2>
        <p>{para1}</p>
        <p>{para2}</p>
        <div class="footer">Generated by Life Path & Zodiac App<br>Remember: You are more than any number or star.</div>
    </div>
    </body>
    </html>
    """
    return html


# ============================================
# MAIN APP
# ============================================

def main():
    st.markdown("""
        <div class="main-header">
            <h1>🔮 Life Path & Zodiac Personality App</h1>
            <p>Discover your cosmic blueprint • Career guidance • Personality insights</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Load data
    data, df = load_personality_data()
    if data is None:
        st.stop()
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["🔮 Your Profile", "💼 Career Guide", "📚 About"])
    
    # ========== TAB 1: YOUR PROFILE ==========
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.subheader("📅 Enter Your Birth Date")
            birth_date = st.date_input("Select your birth date", datetime(1990,7,15), min_value=datetime(1900,1,1), max_value=datetime.now())
            calculate = st.button("🔮 Reveal My Personality", use_container_width=True)
        
        if calculate or 'last_result' in st.session_state:
            day, month, year = birth_date.day, birth_date.month, birth_date.year
            life_path = calculate_life_path_number(day, month, year)
            zodiac_name, zodiac_symbol, zodiac_element = get_zodiac_sign(day, month)
            profile = get_personality_profile(zodiac_name, life_path, data)
            strengths, weaknesses = extract_strengths_weaknesses(profile['paragraph1'] + " " + profile['paragraph2'])
            
            st.session_state['last_result'] = {
                'birth_date': birth_date, 'life_path': life_path, 'zodiac_name': zodiac_name,
                'zodiac_symbol': zodiac_symbol, 'zodiac_element': zodiac_element,
                'profile': profile, 'strengths': strengths, 'weaknesses': weaknesses
            }
        
        if 'last_result' in st.session_state:
            r = st.session_state['last_result']
            st.markdown('<div class="fade-in">', unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1,2,1])
            with col2:
                st.markdown(f"""
                    <div class="result-card">
                        <h2>{r['zodiac_symbol']} {r['zodiac_name']} {r['zodiac_symbol']}</h2>
                        <p>{r['zodiac_element']} Element</p>
                        <div class="life-path-number">{r['life_path']}</div>
                        <p>Life Path Number</p>
                        <hr><p>📅 {r['birth_date'].strftime('%B %d, %Y')}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            col_left, col_mid, col_right = st.columns(3)
            with col_left:
                st.subheader("📊 Personality Traits")
                traits = r['profile']['traits']
                for trait, score in traits.items():
                    st.markdown(f"**{trait.capitalize()}**")
                    st.progress(score/10, text=f"{score}/10")
                    st.markdown("<br>", unsafe_allow_html=True)
            
            with col_mid:
                st.subheader("💪 Strengths")
                for s in r['strengths']:
                    st.markdown(f'<div class="strength-box">✅ {s}</div>', unsafe_allow_html=True)
                st.subheader("⚠️ Areas for Growth")
                for w in r['weaknesses']:
                    st.markdown(f'<div class="weakness-box">📌 {w}</div>', unsafe_allow_html=True)
            
            with col_right:
                st.subheader("📖 Character Summary")
                para2_highlighted = r['profile']['paragraph2']
                for career in r['profile']['careers'][:3]:
                    if career in para2_highlighted:
                        para2_highlighted = para2_highlighted.replace(career, f'<span class="career-highlight">{career}</span>')
                st.markdown(f"""
                    <div style="background:#f0f2f6; padding:1rem; border-radius:10px; height:400px; overflow-y:auto;">
                        <p>{r['profile']['paragraph1']}</p>
                        <p>{para2_highlighted}</p>
                    </div>
                """, unsafe_allow_html=True)
            
            # Download button
            html_report = generate_html_report(r['birth_date'], r['zodiac_name'], r['zodiac_symbol'], r['zodiac_element'],
                                               r['life_path'], r['profile']['traits'], r['profile']['paragraph1'],
                                               r['profile']['paragraph2'], r['profile']['careers'])
            b64 = base64.b64encode(html_report.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="personality_report.html" style="text-decoration:none;"><button style="width:100%; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); color: white; border: none; padding: 0.75rem; border-radius: 30px; font-weight: bold;">📥 Download Report (HTML)</button></a>'
            st.markdown(href, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # ========== TAB 2: CAREER GUIDE ==========
    with tab2:
        st.subheader("💼 Career Guidance by Zodiac & Life Path")
        col1, col2 = st.columns(2)
        with col1:
            zodiac_sel = st.selectbox("Zodiac Sign", ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"])
        with col2:
            lp_sel = st.selectbox("Life Path Number", ["1","2","3","4","5","6","7","8","9","11","22","33"])
        if st.button("Show Career Guide", use_container_width=True):
            prof = get_personality_profile(zodiac_sel, lp_sel, data)
            st.markdown(f"<div style='background:linear-gradient(135deg,#667eea,#764ba2); padding:1.5rem; border-radius:15px; color:white; text-align:center; margin:1rem 0'><h2>{zodiac_sel} • Life Path {lp_sel}</h2></div>", unsafe_allow_html=True)
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown("### 🎯 Recommended Careers")
                for i, c in enumerate(prof['careers'][:5],1):
                    st.markdown(f"{i}. **{c}**")
            with col_b:
                st.markdown("### 🌟 Work Style")
                traits = prof['traits']
                st.success(f"✅ Leadership: {'High' if traits['ambitious']>=7 else 'Moderate'}")
                st.success(f"✅ Teamwork: {'High' if traits['kind']>=6 else 'Moderate'}")
                st.success(f"✅ Creativity: {'High' if traits['creative']>=7 else 'Moderate'}")
                st.success(f"✅ Detail Focus: {'High' if traits['analytical']>=7 else 'Moderate'}")
            st.caption("Based on your astrological and numerological profile. Use as inspiration.")
    
    # ========== TAB 3: ABOUT ==========
    with tab3:
        st.subheader("📚 About This App")
        st.markdown("""
        **Life Path Number** – The most important number in numerology, derived from your birth date. It reveals your core personality and life purpose.
        
        **Zodiac Sign** – Based on the sun's position at your birth, it represents your ego, identity, and basic nature.
        
        **Master Numbers** – 11 (visionary), 22 (master builder), 33 (master teacher) carry intensified energy.
        
        **Data Source** – 156+ personality profiles combining 12 zodiac signs and 13 life path numbers.
        
        ---
        **Disclaimer:** This app is for entertainment and self-reflection. Your personality is unique and cannot be fully captured by any system. Take what resonates, leave what doesn't.
        """)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🧘 Daily Insight")
        st.info("✨ The stars incline, they do not compel. You are the author of your story.")
        st.markdown("---")
        st.markdown("## 🔢 Quick Reference")
        with st.expander("Life Path Numbers"):
            st.markdown("1:Leader 2:Diplomat 3:Creative 4:Builder 5:Free 6:Nurturer 7:Seeker 8:Ambitious 9:Humanitarian 11:Visionary 22:Master Builder 33:Master Teacher")
        with st.expander("Zodiac Elements"):
            st.markdown("🔥 Fire: Aries, Leo, Sagittarius\n🌍 Earth: Taurus, Virgo, Capricorn\n💨 Air: Gemini, Libra, Aquarius\n💧 Water: Cancer, Scorpio, Pisces")
        st.caption("Made with ❤️ using Streamlit")

if __name__ == "__main__":
    main()