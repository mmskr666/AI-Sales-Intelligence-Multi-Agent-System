import streamlit as st
import json
import requests
import time

# 页面全局配置：深色模式 + 宽布局
st.set_page_config(
    page_title="AI 销售智能分析 Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义全局样式：深色主题 + 布局优化
st.markdown("""
<style>
/* 全局深色背景 */
.stApp {
    background-color: #121212;
    color: #ffffff;
}
/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background-color: #1e1e1e;
    border-right: 1px solid #333333;
}
/* 主聊天区容器 */
.main-chat-area {
    height: 85vh;
    display: flex;
    flex-direction: column;
    padding: 20px;
}
/* 聊天消息列表 */
.chat-messages {
    flex: 1;
    overflow-y: auto;
    margin-bottom: 20px;
    padding-right: 10px;
}
/* 输入框容器 */
.chat-input {
    padding: 10px 0;
}
/* 消息气泡样式 */
.user-message {
    background-color: #2f73f6;
    color: white;
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 70%;
    margin-left: auto;
}
.ai-message {
    background-color: #333333;
    color: white;
    padding: 12px 16px;
    border-radius: 12px;
    margin: 8px 0;
    max-width: 70%;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ======================
# 左侧侧边栏（按你的设计）
# ======================
with st.sidebar:
    # 1. 智能体介绍/图标头像区
    st.markdown("### 📊 AI 销售智能分析 Agent")
    st.markdown("**企业级多智能体决策系统**")
    st.divider()

    # 2. 历史对话列表区（预留接口位）
    st.markdown("#### 📜 历史对话")
    st.info("后续可接入对话查询接口，展示历史会话")

    # 预留历史对话列表占位（可后续扩展）
    if st.button("🔄 新建对话"):
        st.session_state.messages = []
        st.session_state.session_id = f"user_{int(time.time())}"
        st.rerun()

# ======================
# 右侧主聊天区
# ======================
# 初始化会话状态
if "session_id" not in st.session_state:
    st.session_state.session_id = f"user_{int(time.time())}"
if "messages" not in st.session_state:
    st.session_state.messages = []

# 主聊天区容器
st.markdown('<div class="main-chat-area">', unsafe_allow_html=True)

# 1. 聊天消息展示区
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-message">{msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# 2. 输入框区
st.markdown('<div class="chat-input">', unsafe_allow_html=True)
prompt = st.chat_input("输入你要分析的公司、行业或问题...")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 消息发送与流式响应逻辑
# ======================
if prompt:
    # 1. 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.rerun()  # 刷新页面显示用户消息

    # 2. 调用后端接口，流式获取AI回复
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_resp = ""

        url = "http://127.0.0.1:8000/api/chat/dialogue"
        data = {
            "session_id": st.session_state.session_id,
            "question": prompt
        }

        try:
            with requests.post(url, json=data, stream=True, timeout=300) as resp:
                resp.raise_for_status()
                for chunk in resp.iter_lines():
                    if chunk:
                        try:
                            line = chunk.decode("utf-8")
                            data = json.loads(line)
                            full_resp = json.dumps(data, ensure_ascii=False, indent=2)
                            placeholder.markdown(full_resp)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            full_resp = f"❌ 请求异常：{str(e)}"
            placeholder.error(full_resp)

        # 3. 保存AI回复到会话
        st.session_state.messages.append({"role": "assistant", "content": full_resp})
        st.rerun()