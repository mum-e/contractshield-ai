"""
ContractShield AI - Frontend
- Supports actual PDF/DOCX upload
- Job-based workflow (uploaded → parsing → analyzing → completed)
- Mock backend API calls (ready for real API integration)
- Complete evidence viewer and report export
"""

import streamlit as st
import pandas as pd
import time
import json
import uuid
from datetime import datetime
from io import BytesIO
import base64

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="ContractShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# GLOBAL CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #0b0f1a;
    color: #e8eaf0;
}
.stApp { background-color: #0b0f1a; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1200px; }

#MainMenu, footer, header { visibility: hidden; }

/* ── Hero Banner ── */
.hero {
    background: linear-gradient(135deg, #0d1b3e 0%, #0b2a4a 50%, #091f38 100%);
    border: 1px solid #1e3a5f;
    border-radius: 20px;
    padding: 3rem 3.5rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(0,180,255,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-tag {
    display: inline-block;
    background: rgba(0,180,255,0.15);
    color: #00b4ff;
    border: 1px solid rgba(0,180,255,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    font-family: 'Syne', sans-serif;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero h1 {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.6rem;
    line-height: 1.15;
}
.hero h1 span { color: #00b4ff; }
.hero p {
    font-size: 1rem;
    color: #8a9ab8;
    max-width: 560px;
    line-height: 1.65;
    margin: 0;
}

/* ── Workflow Bar ── */
.workflow-bar {
    display: flex;
    gap: 0;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    overflow: hidden;
    margin-bottom: 2.5rem;
}
.step {
    flex: 1;
    padding: 1rem 0.8rem;
    text-align: center;
    border-right: 1px solid #1e293b;
    position: relative;
    transition: background 0.2s;
}
.step:last-child { border-right: none; }
.step.active { background: rgba(0,180,255,0.08); }
.step-num {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px; height: 28px;
    border-radius: 50%;
    background: #1e293b;
    color: #64748b;
    font-size: 0.75rem;
    font-weight: 700;
    font-family: 'Syne', sans-serif;
    margin-bottom: 0.4rem;
}
.step.active .step-num {
    background: #00b4ff;
    color: #fff;
}
.step.done .step-num {
    background: #00c97a;
    color: #fff;
}
.step-label {
    display: block;
    font-size: 0.72rem;
    color: #64748b;
    font-weight: 500;
    letter-spacing: 0.03em;
}
.step.active .step-label { color: #00b4ff; }
.step.done .step-label  { color: #00c97a; }

/* ── Section Title ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 1rem;
    letter-spacing: 0.02em;
}

/* ── Upload Area ── */
.upload-box {
    border: 2px dashed #1e3a5f;
    border-radius: 14px;
    padding: 2.5rem;
    text-align: center;
    background: rgba(13, 27, 62, 0.4);
    transition: border-color 0.2s, background 0.2s;
}
.upload-box:hover {
    border-color: #00b4ff;
    background: rgba(13, 27, 62, 0.7);
}
.upload-icon {
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
}
.upload-text {
    font-size: 0.95rem;
    color: #8a9ab8;
    margin-bottom: 0.3rem;
}
.upload-hint {
    font-size: 0.8rem;
    color: #64748b;
}

/* ── Contract Type Selector ── */
.contract-type-card {
    background: #111827;
    border: 1.5px solid #1e293b;
    border-radius: 12px;
    padding: 1rem;
    cursor: pointer;
    transition: border-color 0.2s, transform 0.15s;
    text-align: center;
    margin-bottom: 0.8rem;
}
.contract-type-card:hover {
    border-color: #00b4ff;
    transform: translateY(-2px);
}
.contract-type-card.selected {
    border-color: #00b4ff;
    background: rgba(0,180,255,0.06);
}
.contract-type-label {
    font-size: 0.8rem;
    font-family: 'Syne', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #00b4ff;
    margin-bottom: 0.2rem;
}
.contract-type-name {
    font-size: 0.9rem;
    font-weight: 600;
    color: #e8eaf0;
}

/* ── Score Box ── */
.score-box {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 16px;
    padding: 1.8rem;
    text-align: center;
}
.score-label {
    font-size: 0.75rem;
    font-family: 'Syne', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.score-value {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1;
}
.score-sublabel {
    font-size: 0.8rem;
    color: #64748b;
    margin-top: 0.3rem;
}

/* ── Badge ── */
.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
.badge-high   { background: rgba(255,77,109,0.15);  color: #ff4d6d;  border: 1px solid rgba(255,77,109,0.3); }
.badge-medium { background: rgba(255,179,71,0.15);  color: #ffb347;  border: 1px solid rgba(255,179,71,0.3); }
.badge-low    { background: rgba(0,201,122,0.15);   color: #00c97a;  border: 1px solid rgba(0,201,122,0.3); }
.badge-legal  { background: rgba(138,99,255,0.15);  color: #a78bfa;  border: 1px solid rgba(138,99,255,0.3); }
.badge-financial { background: rgba(0,180,255,0.15); color: #00b4ff; border: 1px solid rgba(0,180,255,0.3); }
.badge-operational { background: rgba(251,191,36,0.15); color: #fbbf24; border: 1px solid rgba(251,191,36,0.3); }

/* ── Clause Card ── */
.clause-card {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 0.9rem;
    border-left: 3px solid #1e293b;
    cursor: pointer;
    transition: border-left-color 0.2s, border-color 0.2s;
}
.clause-card:hover {
    border-color: #1e3a5f;
}
.clause-card.high   { border-left-color: #ff4d6d; }
.clause-card.medium { border-left-color: #ffb347; }
.clause-card.low    { border-left-color: #00c97a; }
.clause-title {
    font-weight: 600;
    font-size: 0.95rem;
    color: #e8eaf0;
    margin-bottom: 0.4rem;
}
.clause-explain {
    font-size: 0.84rem;
    color: #8a9ab8;
    line-height: 1.55;
    margin-bottom: 0.5rem;
}
.clause-q {
    font-size: 0.82rem;
    color: #00b4ff;
    font-style: italic;
}

/* ── Evidence Box ── */
.evidence-box {
    background: #0d1427;
    border: 1px solid #1e2a3a;
    border-radius: 12px;
    padding: 1.3rem;
    margin-top: 1rem;
    margin-bottom: 1rem;
}
.evidence-label {
    font-size: 0.75rem;
    font-family: 'Syne', sans-serif;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 0.5rem;
}
.evidence-text {
    font-size: 0.85rem;
    color: #c0cce0;
    line-height: 1.6;
    font-style: italic;
    border-left: 2px solid #00b4ff;
    padding-left: 0.8rem;
}

/* ── Summary Box ── */
.summary-box {
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    line-height: 1.75;
    font-size: 0.92rem;
    color: #c0cce0;
}

/* ── Checklist Item ── */
.check-item {
    display: flex;
    align-items: flex-start;
    gap: 0.8rem;
    background: #111827;
    border: 1px solid #1e293b;
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.7rem;
}
.check-icon {
    font-size: 1.1rem;
    margin-top: 1px;
    flex-shrink: 0;
}
.check-text {
    font-size: 0.88rem;
    color: #c0cce0;
    line-height: 1.5;
}

/* ── Divider ── */
.divider {
    border: none;
    border-top: 1px solid #1e293b;
    margin: 2rem 0;
}

/* ── Disclaimer ── */
.disclaimer-box {
    background: rgba(0, 180, 255, 0.08);
    border: 1px solid rgba(0, 180, 255, 0.3);
    border-radius: 12px;
    padding: 1.2rem;
    margin: 1.5rem 0;
    font-size: 0.85rem;
    color: #a8bfd4;
    line-height: 1.6;
}

/* ── Buttons ── */
.stButton > button {
    background: #00b4ff !important;
    color: #fff !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 2rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

/* ── File uploader ── */
div[data-testid="stFileUploadDropzone"] {
    border-color: #1e3a5f !important;
    background: rgba(13, 27, 62, 0.2) !important;
}

/* ── Tabs ── */
div[data-testid="stTabs"] button[role="tab"] {
    color: #64748b !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
}
div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: #00b4ff !important;
    border-bottom-color: #00b4ff !important;
}

/* ── Selectbox ── */
div[data-testid="stSelectbox"] label,
div[data-testid="stRadio"] label { 
    color: #8a9ab8 !important; 
}

/* ── Progress Bar ── */
.stProgress > div > div > div > div { background: #00b4ff !important; }

/* ── Info Box ── */
.stInfo {
    background: rgba(0, 180, 255, 0.1) !important;
    border: 1px solid rgba(0, 180, 255, 0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MOCK BACKEND API
# ─────────────────────────────────────────────
class MockAnalysisAPI:
    """
    Mock backend API for demonstration.
    Will be replaced with real API calls to backend in future.
    """
    
    ANALYSIS_RESPONSES = {
        "employment": {
            "summary": (
                "This is an employment contract between the employee and the employer. "
                "The contract specifies a monthly salary, working hours, probation period, and termination conditions. "
                "A non-disclosure clause covers company information, and there are no explicit benefits or overtime policies mentioned. "
                "Dispute resolution is not clearly defined, which may create complications if disputes arise."
            ),
            "overall_score": 68,
            "scores": {"Legal": 55, "Financial": 72, "Operational": 78},
            "clauses": [
                {
                    "clause": "Termination can happen at any time by employer without notice",
                    "risk_type": "Legal",
                    "severity": "High",
                    "explanation": "Allows employer to terminate without advance notice, creating an unfair power imbalance.",
                    "original_text": "Either party may terminate this employment at any time without providing notice to the other party.",
                    "question": "Can a minimum 2-week termination notice period be added for both parties?",
                },
                {
                    "clause": "Working hours: Mon–Fri, 9AM–6PM (no overtime policy)",
                    "risk_type": "Operational",
                    "severity": "High",
                    "explanation": "No overtime compensation policy may violate labor standards.",
                    "original_text": "Employee shall work Monday through Friday, 9:00 AM to 6:00 PM. Any additional work beyond these hours is not compensated.",
                    "question": "What is the overtime compensation policy?",
                },
                {
                    "clause": "NDA covers 'all company information' indefinitely",
                    "risk_type": "Legal",
                    "severity": "Medium",
                    "explanation": "Overly broad NDA with no time limit could prevent future career moves.",
                    "original_text": "Employee agrees to maintain confidentiality of all company information in perpetuity.",
                    "question": "Can the NDA be limited to 2 years post-employment?",
                },
                {
                    "clause": "Monthly salary: $3,000 (no increment clause)",
                    "risk_type": "Financial",
                    "severity": "Medium",
                    "explanation": "No mention of salary review or increment schedule.",
                    "original_text": "Monthly salary is fixed at $3,000.00 USD.",
                    "question": "Is there any provision for annual salary review or increment?",
                },
            ]
        },
        "business": {
            "summary": (
                "This is a business service agreement between a service provider and client. "
                "The contract specifies deliverables, payment terms, timeline, and intellectual property rights. "
                "Payment is structured with an upfront deposit and final payment upon completion. "
                "Deliverables are described generally, and there are no clear revision limits or cancellation clauses. "
                "The agreement lacks detail on dispute resolution and liability limitations."
            ),
            "overall_score": 58,
            "scores": {"Legal": 62, "Financial": 45, "Operational": 66},
            "clauses": [
                {
                    "clause": "Deliverables defined as 'professional service'",
                    "risk_type": "Operational",
                    "severity": "High",
                    "explanation": "Vague deliverable descriptions frequently cause disputes during acceptance.",
                    "original_text": "Service Provider agrees to deliver a professional service to Client.",
                    "question": "Can we agree on a detailed specification of deliverables?",
                },
                {
                    "clause": "Unlimited revisions at no cost",
                    "risk_type": "Financial",
                    "severity": "High",
                    "explanation": "Unlimited revisions without cost creates financial risk.",
                    "original_text": "Client may request unlimited revisions at no additional charge.",
                    "question": "Can revisions be limited to 2 rounds at no cost?",
                },
                {
                    "clause": "No cancellation fee clause",
                    "risk_type": "Financial",
                    "severity": "Medium",
                    "explanation": "If client cancels mid-project, service provider may receive no compensation.",
                    "original_text": "Either party may cancel this agreement at any time.",
                    "question": "Can a cancellation fee be included?",
                },
            ]
        },
    }

    @staticmethod
    def simulate_upload_and_parse(filename: str, contract_type: str):
        """
        Mock API call: POST /api/upload
        Returns job_id for tracking analysis progress
        """
        job_id = str(uuid.uuid4())[:8]
        return {
            "status": "success",
            "job_id": job_id,
            "filename": filename,
            "contract_type": contract_type,
            "uploaded_at": datetime.now().isoformat(),
        }

    @staticmethod
    def simulate_analysis(job_id: str, contract_type: str = "employment"):
        """
        Mock API call: GET /api/analysis/{job_id}
        Returns full analysis with clauses, scores, etc.
        """
        response_data = MockAnalysisAPI.ANALYSIS_RESPONSES.get(
            contract_type.lower(), 
            MockAnalysisAPI.ANALYSIS_RESPONSES["employment"]
        )
        
        return {
            "status": "completed",
            "job_id": job_id,
            "contract_type": contract_type,
            "analysis": response_data,
            "completed_at": datetime.now().isoformat(),
        }

    @staticmethod
    def generate_report(job_id: str, analysis_data: dict):
        """
        Mock API call: POST /api/report/{job_id}
        Generates negotiation memo in JSON format
        """
        return {
            "status": "success",
            "job_id": job_id,
            "report": {
                "title": "ContractShield AI - Negotiation Memo",
                "generated_at": datetime.now().isoformat(),
                "overall_score": analysis_data["scores"].get("overall", 0),
                "summary": analysis_data.get("summary", ""),
                "top_risks": [c for c in analysis_data.get("clauses", []) if c["severity"] == "High"],
                "all_risks": analysis_data.get("clauses", []),
                "recommendations": [
                    f"Address: {c['clause']}" 
                    for c in analysis_data.get("clauses", [])
                    if c["severity"] == "High"
                ]
            }
        }


# ─────────────────────────────────────────────
# SESSION STATE INITIALIZATION
# ─────────────────────────────────────────────
if "current_page" not in st.session_state:
    st.session_state.current_page = "home"  # home, upload, processing, results

if "job_id" not in st.session_state:
    st.session_state.job_id = None

if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None

if "contract_type" not in st.session_state:
    st.session_state.contract_type = "employment"

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

if "selected_risk_idx" not in st.session_state:
    st.session_state.selected_risk_idx = None

if "active_tab" not in st.session_state:
    st.session_state.active_tab = "summary"


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def workflow_step_indicator(step: int):
    """Display workflow progress: 1=select, 2=upload, 3=analyzing, 4=results"""
    steps = [
        ("1", "Contract Type"),
        ("2", "Upload File"),
        ("3", "Analyzing"),
        ("4", "Results"),
    ]
    html = '<div class="workflow-bar">'
    for i, (num, label) in enumerate(steps):
        if i + 1 < step:
            cls = "step done"
            num_display = "✓"
        elif i + 1 == step:
            cls = "step active"
            num_display = num
        else:
            cls = "step"
            num_display = num
        html += f'<div class="{cls}"><div class="step-num">{num_display}</div><span class="step-label">{label}</span></div>'
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def severity_to_color(severity: str):
    colors = {
        "High": "#ff4d6d",
        "Medium": "#ffb347",
        "Low": "#00c97a",
    }
    return colors.get(severity, "#fff")


def risk_type_color(risk_type: str):
    colors = {
        "Legal": "#a78bfa",
        "Financial": "#00b4ff",
        "Operational": "#fbbf24",
    }
    return colors.get(risk_type, "#fff")


# ─────────────────────────────────────────────
# PAGE: HOME - Disclaimer & Introduction
# ─────────────────────────────────────────────
def page_home():
    st.markdown("""
    <div class="hero">
      <div class="hero-tag">🛡️ AI Contract Risk Copilot</div>
      <h1>Contract<span>Shield</span> AI</h1>
      <p>Upload your employment or business contract and get an AI-powered risk analysis 
         before you sign. We identify risky clauses, score your contract safety, and generate 
         a negotiation checklist tailored to your agreement.</p>
    </div>
    """, unsafe_allow_html=True)

    workflow_step_indicator(1)

    st.markdown('<div class="section-title">⚖️ Disclaimer & Privacy Notice</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer-box">
    <strong>Important:</strong> ContractShield AI is an informational tool designed to help you 
    understand contracts and identify potential risks. It is NOT a substitute for professional 
    legal advice. <br><br>
    
    <strong>How we handle your data:</strong><br>
    • Your uploaded contract is processed for analysis only<br>
    • We do NOT train AI models on your contracts<br>
    • Temporary files are deleted after analysis completes<br>
    • No personal or confidential information is stored long-term<br>
    • You maintain full ownership of your documents<br><br>
    
    <strong>Recommendations:</strong><br>
    • Always consult a qualified lawyer before signing important contracts<br>
    • Use this tool as a first-layer reviewer to ask better questions<br>
    • Never rely solely on AI analysis for legal decisions
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col2:
        agree = st.checkbox("I understand and agree to the terms above")
    
    if agree:
        if st.button("🚀 Start Analysis"):
            st.session_state.current_page = "upload"
            st.rerun()
    else:
        st.info("Please check the box above to proceed.", icon="ℹ️")


# ─────────────────────────────────────────────
# PAGE: UPLOAD - File Upload & Contract Type
# ─────────────────────────────────────────────
def page_upload():
    workflow_step_indicator(2)
    st.markdown('<div class="section-title">📋 Step 1: Select Contract Type</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "📄 Employment Contract",
            key="btn_employment",
            use_container_width=True,
        ):
            st.session_state.contract_type = "employment"

    with col2:
        if st.button(
            "🏢 Business Contract",
            key="btn_business",
            use_container_width=True,
        ):
            st.session_state.contract_type = "business"

    selected_type = "Employment Contract" if st.session_state.contract_type == "employment" else "Business Contract"
    st.markdown(f"""
    <div style='background:#111827;border:1px solid #1e293b;border-radius:10px;padding:1rem;
    text-align:center;margin:1rem 0;color:#8a9ab8;'>
    Selected: <span style='color:#00b4ff;font-weight:600;'>{selected_type}</span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title" style="margin-top:2rem">📁 Step 2: Upload Your Contract</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload PDF or DOCX contract",
        type=["pdf", "docx"],
        help="Max 10MB. Supported: PDF, DOCX"
    )

    if uploaded_file:
        st.session_state.uploaded_file = uploaded_file
        st.success(f"✅ File loaded: {uploaded_file.name}")

        if st.button("📤 Analyze Contract", use_container_width=True):
            st.session_state.current_page = "processing"
            st.rerun()
    else:
        st.markdown("""
        <div class="disclaimer-box">
        💡 <strong>Tip:</strong> You can also paste the filename of a test contract for demonstration.
        </div>
        """, unsafe_allow_html=True)

    if st.button("⬅️ Back", use_container_width=False):
        st.session_state.current_page = "home"
        st.rerun()


# ─────────────────────────────────────────────
# PAGE: PROCESSING - Simulate Analysis
# ─────────────────────────────────────────────
def page_processing():
    workflow_step_indicator(3)
    st.markdown('<div class="section-title">⏳ Analyzing Your Contract</div>', unsafe_allow_html=True)

    filename = st.session_state.uploaded_file.name if st.session_state.uploaded_file else "contract.pdf"

    # Simulate upload
    upload_response = MockAnalysisAPI.simulate_upload_and_parse(
        filename, 
        st.session_state.contract_type
    )
    st.session_state.job_id = upload_response["job_id"]

    progress_bar = st.progress(0)
    status = st.empty()

    stages = [
        (10, "📤 Uploading contract..."),
        (30, "📄 Parsing document..."),
        (50, "🔍 Extracting clauses..."),
        (70, "⚙️ Analyzing risks..."),
        (90, "📊 Computing scores..."),
        (100, "✅ Complete!"),
    ]

    for progress, msg in stages:
        status.markdown(f"<span style='color:#8a9ab8;font-size:0.88rem'>{msg}</span>", unsafe_allow_html=True)
        progress_bar.progress(progress)
        time.sleep(0.6)

    # Simulate analysis API call
    analysis_response = MockAnalysisAPI.simulate_analysis(
        st.session_state.job_id,
        st.session_state.contract_type
    )
    st.session_state.analysis_data = analysis_response["analysis"]

    time.sleep(0.5)
    st.session_state.current_page = "results"
    st.rerun()


# ─────────────────────────────────────────────
# PAGE: RESULTS - Dashboard & Analysis
# ─────────────────────────────────────────────
def page_results():
    workflow_step_indicator(4)

    if not st.session_state.analysis_data:
        st.error("No analysis data available. Please upload a contract first.")
        if st.button("⬅️ Back to Upload"):
            st.session_state.current_page = "upload"
            st.rerun()
        return

    analysis = st.session_state.analysis_data
    overall_score = analysis["overall_score"]
    scores = analysis["scores"]
    clauses = analysis["clauses"]

    # ── Score verdict logic ──
    if overall_score >= 75:
        score_color = "#00c97a"
        score_verdict = "Low Risk"
    elif overall_score >= 55:
        score_color = "#ffb347"
        score_verdict = "Medium Risk"
    else:
        score_color = "#ff4d6d"
        score_verdict = "High Risk"

    st.markdown('<div class="section-title">📊 Analysis Dashboard</div>', unsafe_allow_html=True)

    # ── Score cards row ──
    c0, c1, c2, c3 = st.columns([2, 1, 1, 1])
    with c0:
        st.markdown(f"""
        <div class="score-box">
          <div class="score-label">Overall Contract Safety</div>
          <div class="score-value" style="color:{score_color}">{overall_score}<span style="font-size:1.4rem;color:#64748b">/100</span></div>
          <div class="score-sublabel">{score_verdict}</div>
        </div>
        """, unsafe_allow_html=True)

    risk_types = ["Legal", "Financial", "Operational"]
    type_colors = {"Legal": "#a78bfa", "Financial": "#00b4ff", "Operational": "#fbbf24"}

    for col, risk_type in zip([c1, c2, c3], risk_types):
        with col:
            val = scores.get(risk_type, 0)
            verd = "Low" if val >= 75 else ("Medium" if val >= 55 else "High")
            clr = type_colors[risk_type]
            st.markdown(f"""
            <div class="score-box" style="height:100%">
              <div class="score-label">{risk_type}</div>
              <div class="score-value" style="color:{clr};font-size:2.2rem">{val}<span style="font-size:1rem;color:#64748b">/100</span></div>
              <div class="score-sublabel">{verd}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    # ── Tabs ──
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Summary", "⚠️ Risk Clauses", "✅ Checklist", "📄 Report"])

    with tab1:
        st.markdown('<div class="section-title">Plain-Language Summary</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="summary-box">{analysis.get("summary", "")}</div>', unsafe_allow_html=True)

        # Risk breakdown table
        clause_data = []
        for c in clauses:
            clause_data.append({
                "Clause": c["clause"],
                "Risk Type": c["risk_type"],
                "Severity": c["severity"],
            })
        clause_df = pd.DataFrame(clause_data)
        st.markdown('<div class="section-title" style="margin-top:1.5rem">Detected Risks</div>', unsafe_allow_html=True)
        st.dataframe(clause_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown('<div class="section-title">Clause-Level Risk Analysis</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            sev_filter = st.selectbox("Filter by Severity", ["All", "High", "Medium", "Low"], key="sev_filter")
        with col2:
            type_filter = st.selectbox("Filter by Type", ["All", "Legal", "Financial", "Operational"], key="type_filter")

        for idx, clause in enumerate(clauses):
            if sev_filter != "All" and clause["severity"] != sev_filter:
                continue
            if type_filter != "All" and clause["risk_type"] != type_filter:
                continue

            sev_badge = f'<span class="badge badge-{clause["severity"].lower()}">{clause["severity"]}</span>'
            type_badge = f'<span class="badge badge-{clause["risk_type"].lower()}">{clause["risk_type"]}</span>'

            st.markdown(f"""
            <div class="clause-card {clause['severity'].lower()}">
              <div class="clause-title">{clause['clause']} &nbsp; {sev_badge} &nbsp; {type_badge}</div>
              <div class="clause-explain">⚠️ {clause['explanation']}</div>
              <div class="clause-q">💬 Suggested question: "{clause['question']}"</div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"View Original Clause", key=f"view_clause_{idx}"):
                st.session_state.selected_risk_idx = idx
                st.rerun()

        # Display selected risk detail
        if st.session_state.selected_risk_idx is not None and st.session_state.selected_risk_idx < len(clauses):
            selected = clauses[st.session_state.selected_risk_idx]
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            st.markdown('<div class="section-title">📖 Original Clause (Evidence)</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="evidence-box">
              <div class="evidence-label">Original Contract Text</div>
              <div class="evidence-text">{selected.get('original_text', 'No original text available')}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"**Why this is risky:** {selected['explanation']}")
            st.markdown(f"**Suggested action:** {selected['question']}")

            if st.button("Clear Detail"):
                st.session_state.selected_risk_idx = None
                st.rerun()

    with tab3:
        st.markdown('<div class="section-title">Negotiation Checklist</div>', unsafe_allow_html=True)
        st.markdown("Before signing, ensure you've addressed these questions:")

        for idx, clause in enumerate(clauses):
            icon = "🔴" if clause["severity"] == "High" else ("🟡" if clause["severity"] == "Medium" else "🟢")
            st.markdown(f"""
            <div class="check-item">
              <div class="check-icon">{icon}</div>
              <div class="check-text">
                <strong>{clause['clause']}</strong><br>
                {clause['question']}
              </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="section-title">📄 Negotiation Memo</div>', unsafe_allow_html=True)

        report_response = MockAnalysisAPI.generate_report(
            st.session_state.job_id,
            analysis
        )
        report = report_response["report"]

        # Display memo
        memo_html = f"""
        <div class="summary-box">
        <h3 style='color:#fff;margin-top:0;'>ContractShield AI - Negotiation Memo</h3>
        <p><strong>Overall Safety Score:</strong> {report['overall_score']}/100</p>
        <p><strong>Generated:</strong> {report['generated_at']}</p>
        <hr style='border:none;border-top:1px solid #1e293b;'>
        <h4>Executive Summary</h4>
        <p>{report['summary']}</p>
        <h4>Top Priority Issues</h4>
        <ul>
        """
        for risk in report['top_risks']:
            memo_html += f"<li><strong>{risk['clause']}</strong> — {risk['explanation']}</li>"
        memo_html += "</ul></div>"

        st.markdown(memo_html, unsafe_allow_html=True)

        # Export options
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📋 Copy to Clipboard"):
                st.success("Report copied! (Demo only)")

        with col2:
            if st.button("💾 Download as JSON"):
                json_str = json.dumps(report, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"analysis_{st.session_state.job_id}.json",
                    mime="application/json"
                )

        with col3:
            if st.button("📄 Download as TXT"):
                txt_content = f"""ContractShield AI - Negotiation Memo
Generated: {report['generated_at']}

OVERALL SAFETY SCORE: {report['overall_score']}/100

EXECUTIVE SUMMARY:
{report['summary']}

TOP PRIORITY ISSUES:
"""
                for risk in report['top_risks']:
                    txt_content += f"\n- {risk['clause']}\n  {risk['explanation']}\n"
                
                st.download_button(
                    label="Download TXT",
                    data=txt_content,
                    file_name=f"analysis_{st.session_state.job_id}.txt",
                    mime="text/plain"
                )

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("🔄 Analyze Another Contract"):
            st.session_state.current_page = "upload"
            st.session_state.uploaded_file = None
            st.session_state.analysis_data = None
            st.session_state.selected_risk_idx = None
            st.rerun()

    with col3:
        if st.button("🏠 Back to Home"):
            st.session_state.current_page = "home"
            st.session_state.uploaded_file = None
            st.session_state.analysis_data = None
            st.session_state.selected_risk_idx = None
            st.rerun()

    # Disclaimer at bottom
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="disclaimer-box">
    ⚠️ <strong>Final Reminder:</strong> This analysis is for informational purposes only. 
    Always consult a qualified lawyer before signing any contract. ContractShield AI is a 
    first-layer reviewer, not a substitute for professional legal advice.
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN APP ROUTING
# ─────────────────────────────────────────────
if __name__ == "__main__":
    page = st.session_state.current_page

    if page == "home":
        page_home()
    elif page == "upload":
        page_upload()
    elif page == "processing":
        page_processing()
    elif page == "results":
        page_results()
    else:
        page_home()
