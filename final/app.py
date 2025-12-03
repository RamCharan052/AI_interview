"""
Streamlit UI for Aikam Interview Bot
Beautiful, professional interview interface
"""

import streamlit as st
import json
from datetime import datetime
from ai_interview_bot import get_aikam_response, clear_session, _bot_instances

# Page configuration
st.set_page_config(
    page_title="Aikam AI Interview",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .bot-message {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        text-align: right;
    }
    .rephrase-message {
        background: #fff8e6;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .metric-card {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    h1, h2, h3 {
        color: white;
    }
    .stTextArea label, .stTextInput label {
        color: white !important;
        font-weight: 600;
    }
    .action-badge {
        background: #667eea;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        margin-left: 5px;
    }
    .rephrased-badge {
        background: #ff6b6b;
        color: white;
        padding: 3px 10px;
        border-radius: 10px;
        font-size: 11px;
        font-weight: 600;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'session_id' not in st.session_state:
    st.session_state.session_id = f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'interview_ended' not in st.session_state:
    st.session_state.interview_ended = False
if 'job_desc_value' not in st.session_state:
    st.session_state.job_desc_value = ""
if 'resume_value' not in st.session_state:
    st.session_state.resume_value = ""
if 'current_round' not in st.session_state:
    st.session_state.current_round = "HR"

# Header
st.title("🎯 Aikam AI Interview Bot")
st.markdown("### Professional AI-Powered Interview Assistant")

# Sidebar - Setup
with st.sidebar:
    st.header("📋 Interview Setup")
    
    if not st.session_state.interview_started:
        st.markdown("#### Job Description")
        job_description = st.text_area(
            "Enter job description",
            value="Senior Python Developer with 5+ years experience in Django, REST APIs, and microservices architecture. Strong problem-solving skills required.",
            height=150,
            key="job_desc_input"
        )
        
        st.markdown("#### Candidate Resume")
        resume = st.text_area(
            "Enter candidate resume",
            value="Python Developer with 5 years experience in Django, FastAPI, and building scalable REST APIs. Worked on e-commerce platforms and data pipelines.",
            height=150,
            key="resume_input"
        )
        
        if st.button("🚀 Start Interview", type="primary", use_container_width=True):
            # Save to session state
            st.session_state.job_desc_value = job_description
            st.session_state.resume_value = resume
            st.session_state.interview_started = True
            
            # Start interview
            response = get_aikam_response(
                st.session_state.session_id,
                job_description,
                resume,
                "HR",
                ""
            )
            
            # Store in format matching backend structure
            st.session_state.chat_history.append({
                "question": response['question'],
                "answer": "",
                "score_out_of_10": response.get('score_out_of_10', 0),
                "round": st.session_state.current_round,
                "is_rephrased": response['is_rephrased'],
                "is_inadequate": response.get('is_inadequate', False),
                "action": response['action'],
                "evaluation_reason": response.get('evaluation_reason', ''),
                "timestamp": datetime.now().isoformat()
            })
            
            st.rerun()
    
    else:
        # Interview status
        st.success("✅ Interview in Progress")
        
        # Get current bot instance
        bot = _bot_instances.get(st.session_state.session_id)
        if bot:
            st.markdown("#### 📊 Interview Stats")
            summary = bot.get_summary()
            st.metric("Questions Asked", summary['question_count'])
            st.metric("Total Score", summary['total_score'])
            st.metric("Current Round", st.session_state.current_round)
        
        if st.button("🛑 End Interview", type="secondary", use_container_width=True):
            st.session_state.interview_ended = True
            st.rerun()

# Main chat area
if st.session_state.interview_started and not st.session_state.interview_ended:
    
    # Display chat history
    st.markdown("### 💬 Interview Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        for i, entry in enumerate(st.session_state.chat_history):
            # Display question
            is_rephrase = entry.get('is_rephrased', False)
            css_class = "rephrase-message" if is_rephrase else "bot-message"
            
            action_html = f'<span class="action-badge">{entry.get("action", "N/A")}</span>'
            rephrase_html = '<span class="rephrased-badge">Rephrased</span>' if is_rephrase else ''
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>🤖 Aikam:</strong><br>
                {entry['question']}
                <br><br>
                <div style="font-size: 11px; color: #666;">
                    {action_html} {rephrase_html}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display answer if exists AND it's not the last entry (waiting for answer)
            if entry.get('answer') and entry.get('answer').strip():
                st.markdown(f"""
                <div class="user-message">
                    <strong>👤 You:</strong><br>
                    {entry['answer']}
                </div>
                """, unsafe_allow_html=True)

    # Input area
    st.markdown("---")
    
    with st.form(key="answer_form", clear_on_submit=True):
        user_answer = st.text_area(
            "Your Answer:",
            height=100,
            placeholder="Type your answer here...",
            key="user_answer_input"
        )
        
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            submit_button = st.form_submit_button("Send 📤", type="primary", use_container_width=True)
        
        with col2:
            skip_button = st.form_submit_button("Skip ⏭️", use_container_width=True)
        
        if submit_button and user_answer.strip():
            # Update last entry with user's answer
            if st.session_state.chat_history:
                st.session_state.chat_history[-1]['answer'] = user_answer
            
            # Get bot response
            with st.spinner("🤔 Aikam is thinking..."):
                response = get_aikam_response(
                    st.session_state.session_id,
                    st.session_state.job_desc_value,
                    st.session_state.resume_value,
                    st.session_state.current_round,
                    user_answer
                )
            
            # Update last entry with evaluation
            if st.session_state.chat_history:
                st.session_state.chat_history[-1]['score_out_of_10'] = response.get('score_out_of_10', 0)
                st.session_state.chat_history[-1]['is_inadequate'] = response.get('is_inadequate', False)
                st.session_state.chat_history[-1]['evaluation_reason'] = response.get('evaluation_reason', '')
            
            # Add new question
            st.session_state.chat_history.append({
                "question": response['question'],
                "answer": "",
                "score_out_of_10": 0,
                "round": st.session_state.current_round,
                "is_rephrased": response['is_rephrased'],
                "is_inadequate": False,
                "action": response['action'],
                "evaluation_reason": "",
                "timestamp": datetime.now().isoformat()
            })
            
            st.rerun()
        
        elif skip_button:
            # Update last entry with skipped answer
            if st.session_state.chat_history:
                st.session_state.chat_history[-1]['answer'] = "[Skipped]"
                st.session_state.chat_history[-1]['score_out_of_10'] = 0
            
            with st.spinner("🤔 Moving to next question..."):
                response = get_aikam_response(
                    st.session_state.session_id,
                    st.session_state.job_desc_value,
                    st.session_state.resume_value,
                    st.session_state.current_round,
                    ""
                )
            
            # Add new question
            st.session_state.chat_history.append({
                "question": response['question'],
                "answer": "",
                "score_out_of_10": 0,
                "round": st.session_state.current_round,
                "is_rephrased": response['is_rephrased'],
                "is_inadequate": False,
                "action": response['action'],
                "evaluation_reason": "",
                "timestamp": datetime.now().isoformat()
            })
            
            st.rerun()

elif st.session_state.interview_ended:
    st.success("✅ Interview Completed!")
    
    # Get final summary
    bot = _bot_instances.get(st.session_state.session_id)
    if bot:
        summary = bot.get_summary()
        
        st.markdown("### 📊 Interview Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Questions Asked", summary['question_count'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("Total Score", summary['total_score'])
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            avg_score = summary['total_score'] / max(summary['question_count'], 1)
            st.metric("Avg Score", f"{avg_score:.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Prepare JSON export in backend-compatible format
    export_data = {
        "session_id": st.session_state.session_id,
        "job_description": st.session_state.job_desc_value,
        "resume": st.session_state.resume_value,
        "interview_start": st.session_state.chat_history[0]['timestamp'] if st.session_state.chat_history else None,
        "interview_end": datetime.now().isoformat(),
        "conversation_history": [
            {
                "question": entry['question'],
                "answer": entry.get('answer', ''),
                "score_out_of_10": entry.get('score_out_of_10', 0),
                "round": entry.get('round', 'HR'),
                "is_rephrased": entry.get('is_rephrased', False),
                "is_inadequate": entry.get('is_inadequate', False),
                "action": entry.get('action', ''),
                "evaluation_reason": entry.get('evaluation_reason', '')
            }
            for entry in st.session_state.chat_history
        ]
    }
    
    json_str = json.dumps(export_data, indent=2)
    
    st.download_button(
        label="📥 Download Interview JSON",
        data=json_str,
        file_name=f"interview_{st.session_state.session_id}.json",
        mime="application/json",
        type="primary",
        use_container_width=True
    )
    
    if st.button("🔄 Start New Interview", type="secondary", use_container_width=True):
        # Clear session
        clear_session(st.session_state.session_id)
        
        # Reset state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        
        st.rerun()

elif not st.session_state.interview_started:
    # Welcome screen
    st.markdown("""
    <div class="chat-container">
        <h2>👋 Welcome to Aikam AI Interview</h2>
        <p style="font-size: 1.1em; color: #555;">
            Get started by entering the job description and candidate resume in the sidebar,
            then click <strong>Start Interview</strong>.
        </p>
        <br>
        <h3>✨ Features:</h3>
        <ul style="font-size: 1em; color: #666;">
            <li>🎯 AI-powered interview questions</li>
            <li>🔄 Intelligent question rephrasing</li>
            <li>📊 Real-time scoring and evaluation</li>
            <li>💾 Download interview transcript as JSON</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)