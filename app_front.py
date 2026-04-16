import streamlit as st
import json
import requests
import time
from datetime import datetime

# 页面全局配置
st.set_page_config(
    page_title="AI 销售智能分析 Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# 全局样式（纯白 + 干净清爽 + 修复滚动问题）
st.markdown("""
<style>
/* 全局纯白背景 */
.stApp {
    background-color: #ffffff;
    color: #121212;
    overflow: hidden !important; /* 禁止页面整体滚动 */
}
/* 去掉默认边距 */
.block-container {
    padding-top: 0rem !important;
    padding-bottom: 0rem !important;
    max-width: 100% !important;
    height: 100vh !important; /* 占满整个视口高度 */
    display: flex !important;
    flex-direction: row !important;
}

/* 侧边栏改成清爽浅色 */
[data-testid="stSidebar"] {
    background-color: #f8f9fa !important;
    color: #212529 !important;
    border-right: 1px solid #dee2e6 !important;
    padding: 10px 15px !important;
    padding-top: 10px !important;
    position: fixed !important;
    height: 100vh !important;
    width: 350px !important;
    overflow-y: auto !important;
}
/* 隐藏折叠按钮，永远不可折叠 */
button[kind="header"] {
    display: none !important;
}

/* 主聊天区容器：占满剩余高度，flex布局 */
.main-chat-container {
    flex: 1;
    display: flex !important;
    flex-direction: column !important;
    height: 100vh !important;
    padding: 0 !important;
    margin-left: 350px !important; /* 给侧边栏留出空间 */
}

/* 消息滚动区：可滚动，占满剩余空间 */
.chat-messages {
    flex: 1 !important;
    overflow-y: auto !important;
    padding: 20px 50px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 16px !important;
    /* 自动滚动到底部 */
    scroll-behavior: smooth !important;
}

/* 输入框容器：固定在最底部，不滚动 */
.chat-input-container {
    padding: 15px 50px !important;
    background-color: #ffffff !important;
    border-top: 1px solid #f0f0f0 !important;
    flex-shrink: 0 !important; /* 禁止压缩，永远在底部 */
}

/* 消息气泡样式 */
.user-box {
    display: flex;
    justify-content: flex-end;
    width: 100%;
}
.ai-box {
    display: flex;
    justify-content: flex-start;
    width: 100%;
}
.user-bubble {
    background-color: #f0f0f0;
    color: #222;
    padding: 12px 18px;
    border-radius: 16px;
    max-width: 65%;
    word-wrap: break-word;
}
.ai-bubble {
    background-color: #f8f8f8;
    color: #222;
    padding: 12px 18px;
    border-radius: 16px;
    max-width: 65%;
    word-wrap: break-word;
    border: 1px solid #eee;
}

/* 输入框样式 */
[data-testid="stChatInput"] {
    background-color: #ffffff !important;
    border: 1px solid #e0e0e0 !important;
    border-radius: 24px !important;
    width: 100% !important;
    margin: 0 !important;
}
[data-testid="stChatInput"] input {
    background-color: #ffffff !important;
    color: #333 !important;
}

/* 历史会话按钮样式 */
.session-btn {
    width: 100%;
    text-align: left;
    padding: 8px 12px;
    margin: 4px 0;
    border-radius: 8px;
    border: 1px solid #e0e0e0;
    background-color: #ffffff;
    cursor: pointer;
}
.session-btn:hover {
    background-color: #f5f5f5;
}
</style>
""", unsafe_allow_html=True)

# ======================
# 接口请求工具函数
# ======================
def fetch_session_list():
    """获取所有历史会话列表"""
    try:
        res = requests.get("http://127.0.0.1:8000/api/chat/get_sessions?skip=0&limit=20")
        if res.status_code == 200:
            data = res.json()
            return data.get("data", [])
    except Exception as e:
        st.error(f"获取会话列表失败: {e}")
    return []

def fetch_session_messages(session_id: str):
    """根据session_id获取对应会话的所有消息"""
    try:
        res = requests.get(f"http://127.0.0.1:8000/api/chat/get_session/{session_id}")
        if res.status_code == 200:
            data = res.json()
            messages = data.get("data", [])
            # 按create_time升序排序，保证展示顺序正确
            return sorted(messages, key=lambda x: x["create_time"])
    except Exception as e:
        st.error(f"获取会话消息失败: {e}")
    return []

# ======================
# 初始化会话状态
# ======================
if "session_id" not in st.session_state:
    st.session_state.session_id = f"session_{int(time.time())}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_loading" not in st.session_state:
    st.session_state.is_loading = False
if "current_prompt" not in st.session_state:
    st.session_state.current_prompt = ""

# ======================
# 左侧侧边栏（历史会话+点击切换）
# ======================
with st.sidebar:
    st.markdown("### 📊 AI 销售智能分析 Agent")
    st.markdown("""
    <div style='line-height:1.7;color:#444;font-size:14px;'>
    专为销售团队打造的企业级多智能体决策系统，用于快速分析目标客户、行业动态与市场机会，一键生成客户价值评分与合作建议，帮助销售团队精准获客、提升转化效率，让每一次客户沟通都有数据支撑。
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("#### 📜 历史对话")
    sessions = fetch_session_list()

    if sessions:
        for sess in sessions:
            session_id = sess.get("session_id")
            title = sess.get("title", "未命名会话")
            # 用按钮实现点击切换，按钮文本显示title，绑定session_id
            if st.button(f"📝 {title}", key=f"session_{session_id}", use_container_width=True):
                # 点击时：1. 更新当前session_id 2. 加载对应消息 3. 刷新页面
                st.session_state.session_id = session_id
                st.session_state.messages = fetch_session_messages(session_id)
                st.rerun()
    else:
        st.info("暂无历史会话")

    st.divider()

    if st.button("🔄 新建对话", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = f"session_{int(time.time())}"
        st.rerun()

# ======================
# 主聊天区布局
# ======================
# 主容器
st.markdown('<div class="main-chat-container">', unsafe_allow_html=True)

# 1. 聊天消息区（可滚动）
st.markdown('<div class="chat-messages">', unsafe_allow_html=True)

# 渲染历史消息（按时间顺序、正确区分身份）
for msg in st.session_state.messages:
    role = msg.get("role", "assistant")
    content = msg.get("content", "")
    if role == "user":
        st.markdown(f"""
<div class="user-box">
  <div class="user-bubble">{content}</div>
</div>
""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
<div class="ai-box">
  <div class="ai-bubble">{content}</div>
</div>
""", unsafe_allow_html=True)

# 流式回复渲染（加载中状态）
if st.session_state.is_loading:
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_analysis = ""
        url = "http://127.0.0.1:8000/api/chat/dialogue"
        data = {
            "session_id": st.session_state.session_id,
            "question": st.session_state.current_prompt
        }

        try:
            with requests.post(url, json=data, stream=True, timeout=300) as resp:
                for line in resp.iter_lines():
                    if line:
                        try:
                            chunk_data = json.loads(line.decode("utf-8"))
                            result = chunk_data.get("summary", {}).get("result", {})
                            analysis = result.get("analysis", "")
                            if analysis:
                                full_analysis += analysis
                                placeholder.markdown(full_analysis)
                        except:
                            continue
        except Exception as e:
            full_analysis = "❌ 服务异常，请稍后重试"
            placeholder.error(full_analysis)

        # 请求完成，保存AI回复，关闭加载状态
        st.session_state.messages.append({"role": "assistant", "content": full_analysis})
        st.session_state.is_loading = False
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# 2. 输入框区（固定在底部）
st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)
prompt = st.chat_input("输入你想分析的内容...")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ======================
# 发送消息逻辑
# ======================
if prompt and not st.session_state.is_loading:
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.current_prompt = prompt
    st.session_state.is_loading = True
    st.rerun()