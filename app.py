import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import plotly.express as px

# --- 1. Page Configuration (Professional Look) ---
st.set_page_config(page_title="PACE GK Academy", page_icon="📚", layout="wide")

# --- 2. Custom CSS (Bilkul PACE jaisa Design) ---
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; color: #0d6efd; font-weight: bold; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 1.1rem; color: #6c757d; text-align: center; margin-bottom: 20px; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-left: 6px solid #0d6efd; margin-bottom: 15px; }
    .card-title { font-weight: 600; color: #212529; font-size: 1.1rem; margin-bottom: 10px; }
    .card-text { color: #495057; font-size: 0.95rem; }
    .option { padding: 8px; margin: 4px 0; background-color: #f8f9fa; border-radius: 6px; border: 1px solid #e9ecef; }
    .correct-option { background-color: #d1e7dd; border-color: #badbcc; font-weight: bold; color: #0f5132; }
    .explanation-box { background-color: #e3f2fd; padding: 15px; border-radius: 8px; border-left: 4px solid #0d6efd; margin-top: 10px; font-size: 0.95rem; }
    .metric-card { background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); text-align: center; border-top: 4px solid #0d6efd; }
</style>
""", unsafe_allow_html=True)

# --- 3. Gemini API Setup ---
# Streamlit Secrets se API Key uthana
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    api_status = True
except Exception as e:
    api_status = False
    st.error("⚠️ Gemini API Key nahi mili. Please Streamlit Secrets mein 'GEMINI_API_KEY' add karein.")

# --- 4. Functions to Fetch Data from Gemini ---
@st.cache_data(show_spinner=False, ttl=3600)
def generate_past_papers_from_gemini(exam_type, dept):
    """Gemini se past papers ka data generate karwata hai"""
    if not api_status: return []
    
    prompt = f"""
    You are an expert PPSC/FPSC examiner. Generate a JSON list of 6 realistic past paper titles for the exam '{exam_type}' for the department '{dept}'.
    Return ONLY valid JSON. No markdown, no backticks.
    Format:
    [
      {{
        "year": "2026",
        "title": "Name of the post/paper",
        "department": "{dept}",
        "marks": 100
      }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:-3]
        if raw_text.startswith("```"): raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        return []

@st.cache_data(show_spinner=False, ttl=3600)
def generate_mcqs_from_gemini(topic, count=5):
    """Gemini se MCQs aur Explanation generate karwata hai"""
    if not api_status: return []
    
    prompt = f"""
    You are an expert examiner for Pakistani competitive exams. Generate {count} high-quality MCQs on the topic: '{topic}'.
    Return ONLY valid JSON. No markdown, no backticks.
    Format:
    [
      {{
        "question": "Question text here?",
        "options": ["A. Option 1", "B. Option 2", "C. Option 3", "D. Option 4"],
        "correct_answer": "A",
        "explanation": "Detailed explanation of why this is correct."
      }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"): raw_text = raw_text[7:-3]
        if raw_text.startswith("```"): raw_text = raw_text[3:-3]
        return json.loads(raw_text)
    except Exception as e:
        return []

# --- 5. Main App Layout ---
st.markdown('<div class="main-header">PACE GK ACADEMY</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Pakistan Competitive Exam Intelligence & AI Paper Generation System</div>', unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📄 Past Papers Library", "🧠 AI MCQs Generator"])

# --- Tab 1: Dashboard ---
with tab1:
    st.markdown("### 📊 Dashboard Overview")
    
    # Metrics (Demo Data for visual appeal)
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown('<div class="metric-card"><h2>1,250+</h2><p>Past Papers</p></div>', unsafe_allow_html=True)
    col2.markdown('<div class="metric-card"><h2>10,000+</h2><p>MCQs Database</p></div>', unsafe_allow_html=True)
    col3.markdown('<div class="metric-card"><h2>150+</h2><p>Mock Tests</p></div>', unsafe_allow_html=True)
    col4.markdown('<div class="metric-card"><h2>AI</h2><p>Powered by Gemini</p></div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.subheader("📈 Subject-Wise Distribution")
    
    # Plotly Chart
    chart_data = pd.DataFrame({
        "Subject": ["Pakistan Studies", "English", "General Knowledge", "Islamic Studies", "Everyday Science", "Current Affairs"],
        "MCQs": [350, 280, 200, 180, 150, 120]
    })
    fig = px.pie(chart_data, values='MCQs', names='Subject', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("🔥 Recent Past Papers")
    # Auto-generate papers for dashboard display
    recent_papers = generate_past_papers_from_gemini("PPSC", "Miscellaneous")
    if recent_papers:
        for paper in recent_papers[:3]:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📄 {paper['title']}</div>
                <div class="card-text"><b>Year:</b> {paper['year']} | <b>Dept:</b> {paper['department']} | <b>Marks:</b> {paper['marks']}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Loading papers... (Ensure Gemini API Key is correct)")

# --- Tab 2: Past Papers Library ---
with tab2:
    st.markdown("### 📄 Past Papers Library")
    st.write("Select an exam and department to view AI-generated past papers.")
    
    col1, col2 = st.columns(2)
    with col1:
        exam_type = st.selectbox("Select Exam", ["PPSC", "FPSC", "CSS", "PMS"])
    with col2:
        dept = st.selectbox("Select Department", ["Miscellaneous", "Finance", "Punjab Police", "Health", "Education"])
    
    if st.button("🔄 Fetch Papers"):
        st.cache_data.clear()
        st.rerun()
        
    papers = generate_past_papers_from_gemini(exam_type, dept)
    
    if papers:
        for paper in papers:
            st.markdown(f"""
            <div class="card">
                <div class="card-title">📄 {paper['title']}</div>
                <div class="card-text">
                    <b>Year:</b> {paper['year']} | <b>Department:</b> {paper['department']} | <b>Total Marks:</b> {paper['marks']}
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("No papers found. Please check your API key or try another filter.")

# --- Tab 3: AI MCQs Generator ---
with tab3:
    st.markdown("### 🧠 MCQs Master Database (AI Generated)")
    st.write("Select a topic. Gemini AI will generate MCQs with detailed explanations.")
    
    topic = st.selectbox("Select Topic", ["Pakistan Studies", "Islamic Studies", "English Grammar", "General Knowledge", "Everyday Science", "Computer Science"])
    
    if st.button("🧠 Generate MCQs"):
        with st.spinner("Gemini AI MCQs bana raha hai..."):
            mcqs = generate_mcqs_from_gemini(topic, count=5)
            
            if mcqs:
                for idx, mcq in enumerate(mcqs):
                    with st.expander(f"Q{idx+1}. {mcq['question']}"):
                        for opt in mcq['options']:
                            # Highlight correct option
                            if opt.startswith(mcq['correct_answer']):
                                st.markdown(f'<div class="option correct-option">{opt} ✅</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="option">{opt}</div>', unsafe_allow_html=True)
                        
                        st.markdown(f'<div class="explanation-box"><b>Explanation:</b><br>{mcq["explanation"]}</div>', unsafe_allow_html=True)
            else:
                st.warning("MCQs generate nahi ho sake. Please check your API key.")
