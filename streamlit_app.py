"""
Streamlit UI for Restaurant Chatbot vs ReAct Agent comparison.

Usage:
    streamlit run streamlit_app.py
"""

import os
import sys
from dotenv import load_dotenv

import streamlit as st

# Setup path
load_dotenv()
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.chatbot.chatbot import RestaurantChatbot
from src.agent.agent import ReActAgent
from src.tools import TOOL_REGISTRY


def build_provider(provider_name: str = None):
    """Build LLM provider based on env config."""
    provider_name = provider_name or os.getenv("DEFAULT_PROVIDER", "openai")
    
    if provider_name == "openai":
        from src.core.openai_provider import OpenAIProvider
        return OpenAIProvider(
            model_name=os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    elif provider_name == "google":
        from src.core.gemini_provider import GeminiProvider
        return GeminiProvider(
            model_name=os.getenv("DEFAULT_MODEL", "gemini-1.5-flash"),
            api_key=os.getenv("GEMINI_API_KEY"),
        )
    elif provider_name == "local":
        from src.core.local_provider import LocalProvider
        return LocalProvider(
            model_path=os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        )
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def main():
    st.set_page_config(
        page_title="餐廳助手 - Chatbot vs Agent",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🍗 Nhà hàng Gà Rán - Chatbot vs ReAct Agent")
    st.markdown(
        "So sánh câu trả lời giữa Chatbot thường và ReAct Agent (v1/v2)"
    )

    # Sidebar configuration
    st.sidebar.header("⚙️ Cấu hình")
    provider_name = st.sidebar.selectbox(
        "Chọn LLM Provider:",
        ["openai", "google", "local"],
        index=0,
    )
    
    agent_version = st.sidebar.selectbox(
        "Chọn phiên bản Agent:",
        ["agent_v1", "agent_v2"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "💡 **Lưu ý:**\n"
        "- Chatbot dùng tool data nhưng không suy luận đa bước\n"
        "- Agent v1 là baseline ReAct loop\n"
        "- Agent v2 là cải tiến với grounding + guard\n"
    )

    # Initialize session state
    if "llm" not in st.session_state:
        try:
            st.session_state.llm = build_provider(provider_name)
            st.session_state.chatbot = RestaurantChatbot(st.session_state.llm)
            st.session_state.agent = ReActAgent(
                st.session_state.llm,
                TOOL_REGISTRY,
                max_steps=7 if agent_version == "agent_v2" else 5,
                version=agent_version.replace("agent_", ""),
            )
            st.sidebar.success(
                f"✅ Đã load {provider_name} ({st.session_state.llm.model_name})"
            )
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi khi load provider: {e}")
            return

    # Input section
    st.markdown("### 📝 Nhập câu hỏi")
    user_input = st.text_area(
        "Câu hỏi của bạn:",
        placeholder="Ví dụ: Combo nào rẻ nhất? / Giao hàng được không? / Có voucher nào không?",
        height=80,
        key="user_input",
    )

    # Query button
    col_btn1, col_btn2 = st.columns([1, 4])
    with col_btn1:
        run_query = st.button("🚀 Gửi", use_container_width=True)
    with col_btn2:
        st.markdown("")

    if run_query and user_input.strip():
        st.markdown("---")
        st.markdown("### 📊 Kết quả so sánh")

        # Run in parallel
        with st.spinner("⏳ Đang xử lý..."):
            try:
                # Chatbot response
                chatbot_response = st.session_state.chatbot.chat(user_input.strip())
                
                # Agent response
                agent_response = st.session_state.agent.run(user_input.strip())

            except Exception as e:
                st.error(f"❌ Lỗi khi xử lý: {e}")
                return

        # Display results in two columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🤖 Chatbot (Baseline)")
            st.markdown(
                f"""
<div style="background-color: #003d99; color: #ffffff; padding: 15px; border-radius: 8px; border-left: 4px solid #0052cc; font-size: 14px; line-height: 1.6;">
{chatbot_response}
</div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(f"#### 🧠 Agent ({agent_version.upper()})")
            st.markdown(
                f"""
<div style="background-color: #1a6d1a; color: #ffffff; padding: 15px; border-radius: 8px; border-left: 4px solid #33a333; font-size: 14px; line-height: 1.6;">
{agent_response}
</div>
                """,
                unsafe_allow_html=True,
            )

        # Analysis section
        st.markdown("---")
        st.markdown("### 🔍 Nhận xét")
        
        is_same = chatbot_response.strip() == agent_response.strip()
        if is_same:
            st.info("✅ Chatbot và Agent có câu trả lời giống nhau.")
        else:
            st.warning("⚠️ Chatbot và Agent có câu trả lời khác nhau. Kiểm tra lý do tại log hoặc phân tích sự khác biệt.")

        # Reset chatbot state for next conversation
        st.session_state.chatbot.history = []

    elif run_query and not user_input.strip():
        st.warning("⚠️ Vui lòng nhập một câu hỏi.")

    # Footer
    st.markdown("---")
    st.markdown(
        """
<div style="text-align: center; color: #666;">
    <small>Lab 3: From Chatbot to Agentic ReAct | AI 20K26</small>
</div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
