"""
Streamlit UI for Restaurant Chatbot vs ReAct Agent comparison with Monitoring.

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
from src.agent.agent import ReActAgent as ReActAgentCustom
from src.agent.agent_v2 import ReActAgent as ReActAgentV2
from src.agent.agent_v2 import _build_menu_tools
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
        page_title="Chatbot vs Agent",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("🍗 Nhà hàng Gà Rán - Chatbot vs ReAct Agent")

    # Global tracking session state
    if "global_metrics" not in st.session_state or "chatbot" not in st.session_state.global_metrics:
        st.session_state.global_metrics = {
            "chatbot": {"total_cost": 0.0, "total_tokens": 0, "queries": 0},
            "agent": {"total_cost": 0.0, "total_tokens": 0, "queries": 0},
        }

    # Sidebar configuration
    st.sidebar.header("⚙️ Cấu hình")
    
    app_mode = st.sidebar.radio(
        "Chế độ hiển thị (Mode):",
        ["Chat", "Monitor"]
    )

    provider_name = st.sidebar.selectbox(
        "Chọn LLM Provider:",
        ["openai", "google", "local"],
        index=0,
    )
    
    agent_selection = st.sidebar.selectbox(
        "Chọn phiên bản Agent:",
        [
            "Agent (agent.py)",
            "Agent V2 - OpenAI Tools (agent_v2.py)"
        ],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "💡 **Lưu ý:**\n"
        "- Chatbot dùng tool data nhưng không suy luận đa bước\n"
        "- Agent (agent.py) là ReAct loop tự xây với Thought/Action/Observation\n"
        "- Agent V2 (agent_v2.py) sử dụng OpenAI Function Calling (Chỉ hỗ trợ OpenAI)\n"
    )

    # Force re-init if config changes, or if cached objects are missing new metric attrs (stale session)
    _stale = (
        "chatbot" not in st.session_state
        or not hasattr(st.session_state.get("chatbot"), "last_cost")
        or "active_agent" not in st.session_state
        or not hasattr(st.session_state.get("active_agent"), "last_cost")
    )
    if _stale or "llm_provider_name" not in st.session_state or st.session_state.llm_provider_name != provider_name or "agent_selection" not in st.session_state or st.session_state.agent_selection != agent_selection:
        try:
            st.session_state.llm = build_provider(provider_name)
            st.session_state.chatbot = RestaurantChatbot(st.session_state.llm)
            
            if agent_selection == "Agent (agent.py)":
                st.session_state.active_agent = ReActAgentCustom(
                    st.session_state.llm,
                    TOOL_REGISTRY,
                    max_steps=5,
                    version="v1",
                )
            elif agent_selection == "Agent V2 - OpenAI Tools (agent_v2.py)":
                v2_tools = _build_menu_tools("data/mock_data.json")
                st.session_state.active_agent = ReActAgentV2(
                    st.session_state.llm,
                    v2_tools,
                    max_steps=6,
                    trace_enabled=True,
                )
            
            st.session_state.llm_provider_name = provider_name
            st.session_state.agent_selection = agent_selection
            st.sidebar.success(
                f"✅ Đã load {provider_name} ({st.session_state.llm.model_name})"
            )
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi khi load provider: {e}")
            return

    if app_mode == "Chat":
        st.markdown(
            "So sánh câu trả lời giữa Chatbot thường và phiên bản Agent được chọn. Lịch sử trò chuyện được lưu trữ toàn phiên."
        )

        col1, col2 = st.columns(2)

        # Render conversation histories
        with col1:
            st.markdown("#### 🤖 Chatbot (Baseline)")
            for msg in st.session_state.chatbot.history:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    if msg["role"] == "assistant" and "metrics" in msg:
                        m = msg["metrics"]
                        st.caption(f"**⏱️ Time:** {m['latency']:.2f} ms | **🪙 Tokens:** {m['tokens']} | **💵 Cost:** ${m['cost']:.5f} | **⚖️ Ratio:** {m['ratio']:.2f}")
                    
        with col2:
            st.markdown(f"#### 🧠 {agent_selection}")
            if hasattr(st.session_state.active_agent, "history"):
                for idx, msg in enumerate(st.session_state.active_agent.history):
                    with st.chat_message(msg["role"]):
                        st.markdown(msg["content"])
                        if msg["role"] == "assistant":
                            if "metrics" in msg:
                                m = msg["metrics"]
                                st.caption(f"**⏱️ Time:** {m['latency']:.2f} ms | **🪙 Tokens:** {m['tokens']} | **💵 Cost:** ${m['cost']:.5f} | **⚖️ Ratio:** {m['ratio']:.2f}")

                            if "trace" in msg and msg["trace"]:
                                with st.expander(f"🛠️ Xem Trace & Suy Luận (Lượt {idx // 2 + 1})"):
                                    if agent_selection == "Agent V2 - OpenAI Tools (agent_v2.py)":
                                        for t_idx, t in enumerate(msg["trace"]):
                                            st.markdown(f"#### 🔄 Lần gọi Tool {t_idx + 1} (Vòng lặp LLM {t.get('step', '?')})")
                                            st.markdown(f"**🛠️ Gọi Tool:** `{t.get('action')}`")
                                            st.markdown("**📥 Tham số (Args):**")
                                            import json
                                            st.code(json.dumps(t.get('args', {}), indent=2, ensure_ascii=False), language="json")
                                            st.markdown("**📤 Kết quả (Observation):**")
                                            try:
                                                obs_json = json.loads(t.get('observation', '{}'))
                                                st.json(obs_json, expanded=False)
                                            except:
                                                st.code(t.get('observation', ''), language="json")
                                            st.divider()
                                    else:
                                        step_idx = 1
                                        import json
                                        for line in msg["trace"]:
                                            if line.startswith("Thought:") or line.startswith("Thought :"):
                                                st.markdown(f"#### 🔄 Bước suy luận {step_idx}")
                                                step_idx += 1
                                                st.markdown(f"**🧠 Suy nghĩ:** {line.split(':', 1)[1].strip()}")
                                            elif line.startswith("Action:") or line.startswith("Action :"):
                                                st.markdown(f"**🛠️ Hành động:** `{line.split(':', 1)[1].strip()}`")
                                            elif line.startswith("Observation:") or line.startswith("Observation :"):
                                                st.markdown("**📤 Kết quả:**")
                                                obs_text = line.split(':', 1)[1].strip()
                                                try:
                                                    st.json(json.loads(obs_text), expanded=False)
                                                except:
                                                    st.code(obs_text, language="json")
                                                st.divider()
                                            else:
                                                st.markdown(f"> *{line}*")

        # Chat input element pinning to the bottom of the screen
        user_input = st.chat_input("Nhập câu hỏi của bạn (VD: Combo nào rẻ nhất? / Giao hàng được không?)")

        if user_input:
            with st.spinner("⏳ Hệ thống đang xử lý..."):
                try:
                    _ = st.session_state.chatbot.chat(user_input.strip())
                    _ = st.session_state.active_agent.run(user_input.strip())
                    
                    # Accumulate Global Metrics (Chatbot)
                    st.session_state.global_metrics["chatbot"]["total_tokens"] += st.session_state.chatbot.last_tokens
                    st.session_state.global_metrics["chatbot"]["total_cost"] += st.session_state.chatbot.last_cost
                    st.session_state.global_metrics["chatbot"]["queries"] += 1

                    # Accumulate Global Metrics (Agent)
                    st.session_state.global_metrics["agent"]["total_tokens"] += st.session_state.active_agent.last_tokens
                    st.session_state.global_metrics["agent"]["total_cost"] += st.session_state.active_agent.last_cost
                    st.session_state.global_metrics["agent"]["queries"] += 1
                except Exception as e:
                    st.error(f"❌ Lỗi khi xử lý: {e}")
            st.rerun()

    elif app_mode == "Monitor":
        st.markdown("## 📈 Global Metrics Dashboard (Monitor)")
        st.markdown("Theo dõi chi phí và số lượng token hệ thống đã sử dụng cho mỗi phiên bản.")

        st.markdown("### 🤖 Chatbot (Baseline)")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Tokens", f"{st.session_state.global_metrics['chatbot']['total_tokens']:,}")
        c2.metric("Total Cost (USD)", f"${st.session_state.global_metrics['chatbot']['total_cost']:.5f}")
        c3.metric("Queries Executed", st.session_state.global_metrics['chatbot']['queries'])

        st.markdown("---")
        st.markdown(f"### 🧠 {agent_selection}")
        a1, a2, a3 = st.columns(3)
        a1.metric("Total Tokens", f"{st.session_state.global_metrics['agent']['total_tokens']:,}")
        a2.metric("Total Cost (USD)", f"${st.session_state.global_metrics['agent']['total_cost']:.5f}")
        a3.metric("Queries Executed", st.session_state.global_metrics['agent']['queries'])

        st.markdown("---")
        st.markdown("### 📊 Tổng cộng (Total System)")
        t_tokens = st.session_state.global_metrics['chatbot']['total_tokens'] + st.session_state.global_metrics['agent']['total_tokens']
        t_cost = st.session_state.global_metrics['chatbot']['total_cost'] + st.session_state.global_metrics['agent']['total_cost']
        t_queries = st.session_state.global_metrics['chatbot']['queries'] # Same as agent queries usually

        t1, t2, t3 = st.columns(3)
        t1.metric("Combined Tokens", f"{t_tokens:,}")
        t2.metric("Combined Cost (USD)", f"${t_cost:.5f}")
        t3.metric("Total Queries", t_queries)

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
