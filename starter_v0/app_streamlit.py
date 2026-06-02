import streamlit as st
import json
from pathlib import Path

from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from chat import run_model_tool_loop, trim_history

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"

# ----------------- PAGE CONFIG -----------------
st.set_page_config(page_title="Cognitive Lab", page_icon="🧪", layout="wide", initial_sidebar_state="expanded")

# ----------------- CSS INJECTION -----------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif !important;
        color: #334155;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Layout styling */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 3rem !important;
        max-width: 100%;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* Main Area / Top Nav simulation */
    .top-nav {
        display: flex;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
    .top-nav-items {
        display: flex;
        gap: 20px;
        font-weight: 500;
        color: #64748b;
        flex-grow: 1;
    }
    .top-nav-items span.active {
        color: #2563eb;
        border-bottom: 2px solid #2563eb;
        padding-bottom: 12px;
    }
    
    /* Empty State Cards */
    .empty-card {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        background-color: #ffffff;
        height: 100%;
        transition: box-shadow 0.2s;
    }
    .empty-card:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .empty-card-icon {
        color: #2563eb;
        font-size: 1.5rem;
        margin-bottom: 10px;
    }
    .empty-card-title {
        font-weight: 600;
        margin-bottom: 5px;
        color: #0f172a;
    }
    .empty-card-desc {
        color: #64748b;
        font-size: 0.875rem;
    }
    
    /* Main Chat vs Right Panel */
    [data-testid="stHorizontalBlock"]:nth-of-type(2) > [data-testid="column"]:nth-of-type(2) {
        border-left: 1px solid #e2e8f0;
        padding-left: 20px;
        background-color: #f8fafc;
        height: 85vh;
        overflow-y: auto;
        position: sticky;
        top: 20px;
        scrollbar-width: thin;
        scrollbar-color: #cbd5e1 transparent;
    }
    
    /* Smooth smooth smooth */
    html {
        scroll-behavior: smooth;
    }
    
    /* Top Nav specific */
    div[data-testid="column"]:has(#top-nav-marker) {
        /* Optional: specific top nav styling */
    }
    
    /* Multiselect Tag styling */
    span[data-baseweb="tag"] {
        background-color: #e0e7ff !important;
        color: #3b82f6 !important;
        border-radius: 9999px !important;
    }
    span[data-baseweb="tag"] span {
        color: #3b82f6 !important;
    }
    
    .stButton>button {
        border-radius: 8px;
    }
    
    .primary-btn>button {
        background-color: #2563eb !important;
        color: white !important;
    }
    
    /* Help Settings Bottom Nav */
    .sidebar-bottom {
        position: absolute;
        bottom: 20px;
        left: 0;
        width: 100%;
        border-top: 1px solid #e2e8f0;
        padding-top: 15px;
        padding-left: 20px;
    }
    .sidebar-bottom-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #334155;
        margin-bottom: 15px;
        font-weight: 500;
        cursor: pointer;
    }
    
    /* Chat Disclaimer */
    .chat-disclaimer {
        position: fixed;
        bottom: 15px;
        left: 50%;
        transform: translateX(-50%);
        font-size: 0.75rem;
        color: #94a3b8;
        font-family: monospace;
        z-index: 100;
        pointer-events: none;
    }
    
    /* Chat Input Styling */
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #2563eb !important;
        border-radius: 50% !important;
        color: white !important;
        padding: 5px !important;
        margin-right: 5px;
    }
    button[data-testid="stChatInputSubmitButton"] svg {
        fill: white !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- HÀM PHỤ TRỢ -----------------
@st.cache_data
def get_available_tools():
    tools_path = ARTIFACTS_DIR / "tools.yaml"
    if tools_path.exists():
        declarations = load_tool_declarations(tools_path)
        return declarations
    return []

all_tools = get_available_tools()
tool_names = [tool['name'] for tool in all_tools]

# ----------------- KHOI TẠO STATE -----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "system_prompt" not in st.session_state:
    system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
    st.session_state.system_prompt = system_prompt_path.read_text(encoding="utf-8") if system_prompt_path.exists() else "You are a research agent."

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.markdown("<h3 style='color: #1e3a8a; margin-bottom: 0;'>Cognitive Lab</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #64748b; font-size: 0.9rem;'>AI Research System</p>", unsafe_allow_html=True)
    st.markdown("<br/>", unsafe_allow_html=True)
    
    st.markdown("<p style='color: #94a3b8; font-size: 0.75rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase;'>CẤU HÌNH HỆ THỐNG</p>", unsafe_allow_html=True)
    
    provider_choice = st.selectbox("Nhà cung cấp (Provider)", ["openrouter", "openai", "anthropic", "gemini"])
    
    st.markdown("<br/>", unsafe_allow_html=True)
    selected_tool_names = st.multiselect(
        "Bật/Tắt Công cụ",
        options=tool_names,
        default=tool_names
    )
    
    st.markdown("<br/>", unsafe_allow_html=True)
    max_tool_rounds = st.slider("Số vòng lặp Tool tối đa", min_value=1, max_value=10, value=4)
    
    st.markdown("<br/><br/><br/><br/><br/><br/><br/>", unsafe_allow_html=True)
    st.markdown("""
    <div class="sidebar-bottom">
        <div class="sidebar-bottom-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            Help
        </div>
        <div class="sidebar-bottom-item">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            Settings
        </div>
    </div>
    """, unsafe_allow_html=True)
active_tools = [t for t in all_tools if t['name'] in selected_tool_names]
openai_tools = to_openai_tools(active_tools) if active_tools else []

# ----------------- TOP NAV HACK -----------------
st.markdown("""
<style>
.stButton>button {
    height: 40px;
}
.header-actions {
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 15px;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

top_col1, top_col2, top_col3 = st.columns([5, 3, 1], gap="small")
with top_col1:
    st.markdown("""
    <div class="top-nav">
        <div class="top-nav-items">
            <span class="active">Models</span>
            <span>Provider</span>
            <span>Tools</span>
            <span>Iterations</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with top_col2:
    b1, b2 = st.columns([1, 1], gap="small")
    with b1:
        if st.button("🚀 New Research", type="primary", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with b2:
        st.button("Export", use_container_width=True)
with top_col3:
    st.markdown("""
    <div style='display: flex; align-items: center; gap: 15px; height: 100%; justify-content: flex-end; margin-top: 5px;'>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#64748b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path><path d="M13.73 21a2 2 0 0 1-3.46 0"></path></svg>
        <div style="width: 30px; height: 30px; background-color: #0f172a; border-radius: 50%; overflow: hidden;">
            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=Felix" width="100%" height="100%"/>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ----------------- MAIN LAYOUT -----------------
main_col, log_col = st.columns([7, 3])

with main_col:
    st.markdown("### Trợ lý Nghiên cứu AI")
    st.markdown("Chào mừng bạn! Tôi có thể đọc báo, tìm kiếm thông tin trên mạng, kiểm tra thời tiết và nhiều tiện ích khác.")
    st.markdown("<hr style='margin-top: 10px; margin-bottom: 30px; border-top: 1px solid #e2e8f0;'/>", unsafe_allow_html=True)
    
    # Khu vực chat
    if not st.session_state.messages:
        # Empty State
        st.markdown("""
        <div style="background-color: #f1f5f9; border-radius: 12px; padding: 40px 20px; text-align: center; margin-bottom: 30px;">
            <div style="background-color: #dbeafe; color: #1e3a8a; width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 1.5rem; margin-bottom: 15px;">
                💬
            </div>
            <h4 style="margin: 0 0 10px 0; color: #0f172a;">Sẵn sàng hỗ trợ</h4>
            <p style="color: #64748b; max-width: 400px; margin: 0 auto; line-height: 1.5;">Hãy bắt đầu cuộc trò chuyện bằng cách nhập câu hỏi ở bên dưới nhé! Tôi sẽ sử dụng hệ thống kiến thức và các công cụ được cấu hình để cung cấp câu trả lời chính xác nhất.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Cards
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="empty-card">
                <div class="empty-card-icon">📰</div>
                <div class="empty-card-title">Tin tức mới nhất</div>
                <div class="empty-card-desc">Tổng hợp tình hình công nghệ hôm nay</div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="empty-card">
                <div class="empty-card-icon">📊</div>
                <div class="empty-card-title">Phân tích dữ liệu</div>
                <div class="empty-card-desc">Phân tích báo cáo thị trường quý 3</div>
            </div>
            """, unsafe_allow_html=True)
            
    for message in st.session_state.messages:
        if message["role"] in ["user", "assistant"]:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

with log_col:
    st.markdown('<div id="right-sidebar-marker"></div>', unsafe_allow_html=True)
    st.markdown("""
    <h4 style='color: #0f172a; margin-top:0; display: flex; align-items: center; gap: 8px;'>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2a10 10 0 1 0 10 10H12V2z"></path>
            <path d="M22 12A10 10 0 0 0 12 2v10z"></path>
            <circle cx="12" cy="12" r="3"></circle>
            <path d="M19.07 4.93a10 10 0 0 0-14.14 0"></path>
        </svg> 
        Quá trình Suy nghĩ & Tool
    </h4>
    """, unsafe_allow_html=True)
    has_logs = False
    
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "assistant" and message.get("tool_events"):
            has_logs = True
            events = message["tool_events"]
            with st.expander(f"Hệ thống đang ở trạng thái chờ lệnh...", expanded=False):
                for event in events:
                    tool_name = event.get("tool", "Unknown")
                    args = event.get("args", {})
                    result = event.get("result", {})
                    
                    st.markdown(f"**Tool:** `{tool_name}`")
                    st.markdown("**Input:**")
                    st.code(json.dumps(args, ensure_ascii=False, indent=2), language="json")
                    
                    st.markdown("**Output:**")
                    if isinstance(result, dict) and "error" in result:
                        st.error(f"{result.get('error')}")
                    else:
                        res_str = json.dumps(result, ensure_ascii=False, indent=2)
                        st.code(res_str[:300] + ("\n..." if len(res_str) > 300 else ""), language="json")
                    st.divider()
                    
    if not has_logs:
        st.markdown("""
        <div style="text-align: center; margin-top: 100px;">
            <div style="background-color: #f1f5f9; width: 60px; height: 60px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 20px;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#94a3b8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect>
                    <line x1="6" y1="8" x2="6.01" y2="8"></line>
                    <line x1="10" y1="8" x2="10.01" y2="8"></line>
                    <line x1="14" y1="8" x2="14.01" y2="8"></line>
                    <line x1="18" y1="8" x2="18.01" y2="8"></line>
                    <line x1="8" y1="12" x2="16" y2="12"></line>
                </svg>
            </div>
            <p style="color: #94a3b8; font-size: 0.9rem;">Chưa có quá trình sử<br/>dụng tool nào được ghi<br/>nhận.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div style="margin-top: 50px; background-color: #0f172a; border-radius: 12px; padding: 20px; color: white; text-align: center;">
        <p style="font-size: 0.8rem; font-family: monospace; margin: 0; padding-top: 100px;">Visualizing Thought Vectors...</p>
    </div>
    """, unsafe_allow_html=True)


# ----------------- CHAT INPUT -----------------
# We use st.chat_input, it automatically anchors to the bottom
if prompt := st.chat_input("Nhập câu hỏi của bạn vào đây (VD: Tìm tin tức công nghệ hôm nay)..."):
    load_lab_env(ROOT)
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with main_col:
        with st.chat_message("user"):
            st.markdown(prompt)

    st.markdown("<div class='chat-disclaimer'>AI Research System có thể mắc lỗi. Hãy kiểm tra các thông tin quan trọng.</div>", unsafe_allow_html=True)
    
    try:
        provider = make_provider(provider_choice)
        
        messages_for_llm = [{"role": "system", "content": st.session_state.system_prompt}]
        chat_history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        history_to_trim = chat_history[:-1]
        
        messages_for_llm.extend(trim_history(history_to_trim, 5))
        messages_for_llm.append({"role": "user", "content": prompt})

        with main_col:
            with st.chat_message("assistant"):
                with st.spinner("Đang phân tích..."):
                    result = run_model_tool_loop(
                        provider=provider,
                        messages=messages_for_llm,
                        tools=openai_tools,
                        model=getattr(provider, "default_model", None),
                        max_tool_rounds=max_tool_rounds,
                    )
                    
                assistant_text = result.get("assistant_text", "")
                if assistant_text:
                    st.markdown(assistant_text)
                
        tool_events = result.get("tool_events", [])
        st.session_state.messages.append({
            "role": "assistant", 
            "content": assistant_text,
            "tool_events": tool_events
        })
        
        st.rerun()
            
    except Exception as e:
        st.error(f"Lỗi: {str(e)}")
