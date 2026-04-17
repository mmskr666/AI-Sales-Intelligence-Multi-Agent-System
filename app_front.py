import streamlit as st
import json
import requests
import time
from datetime import datetime

# --------------------------
# 页面配置
# --------------------------
st.set_page_config(
    page_title="AI 销售智能分析 Agent",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="📊"
)

# --------------------------
# 自定义样式优化
# --------------------------
st.markdown("""
<style>
/* 主容器样式 */
.main {
    padding-top: 20px;
}
.main .block-container {
    padding-top: 20px;
}

/* 侧边栏样式 */
[data-testid="stSidebar"] {
    background-color: #f8f9fa;
}
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #2c3e50;
}

/* 会话列表样式 */
.session-item {
    padding: 8px 12px;
    border-radius: 8px;
    margin: 4px 0;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
}
.session-item:hover {
    background-color: #f0f7ff;
    border-color: #d0e3ff;
}
.session-item.active {
    background-color: #e6f0ff;
    border-color: #0066cc;
    font-weight: 500;
}
.session-item .title {
    font-size: 14px;
    color: #2c3e50;
    margin-bottom: 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.session-item .time {
    font-size: 12px;
    color: #666;
}

/* 消息气泡样式 */
.stChatMessage {
    padding: 0.5rem 0;
}
[data-testid="stChatMessage"] > div {
    width: 100%;
}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
    background-color: transparent;
}
.user-message {
    background-color: #f0f7ff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 16px;
    margin: 4px 0;
    max-width: 80%;
    margin-left: auto;
}
.assistant-message {
    background-color: #ffffff;
    border: 1px solid #eee;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 16px;
    margin: 4px 0;
    max-width: 80%;
    margin-right: auto;
}

/* 按钮样式优化 */
.stButton > button {
    border-radius: 8px;
    transition: all 0.3s ease;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

/* 输入框样式 */
[data-testid="stChatInputContainer"] {
    background: white;
    border-radius: 12px;
    border: 1px solid #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
[data-testid="stChatInputTextArea"] textarea {
    min-height: 60px;
}

/* 状态指示器 */
.status-indicator {
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
}
.status-active {
    background-color: #28a745;
}
.status-inactive {
    background-color: #dc3545;
}
</style>
""", unsafe_allow_html=True)


# --------------------------
# API 工具函数
# --------------------------
def api_create_session():
    """创建新会话"""
    try:
        res = requests.get("http://127.0.0.1:8000/api/chat/add_session", timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == "success":
                session_id = data.get("data", "")

                # 创建会话标题
                title = f"会话 {datetime.now().strftime('%m-%d %H:%M')}"

                # 保存到本地状态
                sessions = st.session_state.get("sessions", [])
                sessions.insert(0, {
                    "session_id": session_id,
                    "title": title,
                    "time": datetime.now().isoformat()
                })
                st.session_state.sessions = sessions

                return session_id
    except Exception as e:
        st.error(f"创建会话失败: {str(e)}")
    return ""


def api_get_sessions():
    """获取会话列表"""
    try:
        res = requests.get("http://127.0.0.1:8000/api/chat/get_sessions?skip=0&limit=20", timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == "success":
                sessions = data.get("data", [])
                # 如果会话没有标题，添加默认标题
                for session in sessions:
                    if not session.get("title"):
                        # 从session_id解析或生成标题
                        if "create_time" in session:
                            session["title"] = f"会话 {session['create_time'][5:10]}"
                        else:
                            session["title"] = "新会话"
                return sessions
    except Exception as e:
        st.warning("无法获取历史会话列表")
    return []


def api_get_session_messages(session_id):
    """获取会话消息"""
    try:
        res = requests.get(f"http://127.0.0.1:8000/api/chat/get_session/{session_id}", timeout=60)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == "success":
                messages = data.get("data", [])
                # 格式化消息
                formatted_messages = []
                for msg in messages:
                    formatted_messages.append({
                        "role": msg.get("role", "user"),
                        "content": msg.get("content", "")
                    })
                return formatted_messages
    except Exception as e:
        st.warning(f"获取消息失败: {str(e)}")
    return []


def api_send_message(session_id, question):
    """发送消息并获取流式响应"""
    try:
        response = requests.post(
            url="http://127.0.0.1:8000/api/chat/dialogue",
            json={
                "session_id": session_id,
                "question": question
            },
            stream=True,
            timeout=300
        )
        return response
    except Exception as e:
        st.error(f"请求失败: {str(e)}")
    return None


# --------------------------
# 会话状态管理
# --------------------------
def initialize_session_state():
    """初始化会话状态"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_id" not in st.session_state:
        st.session_state.session_id = ""
    if "waiting_for_response" not in st.session_state:
        st.session_state.waiting_for_response = False
    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = ""
    if "sessions" not in st.session_state:
        st.session_state.sessions = []
    if "api_status" not in st.session_state:
        st.session_state.api_status = "checking"  # checking, online, offline


# --------------------------
# 侧边栏组件
# --------------------------
def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # 标题区域
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("📊", unsafe_allow_html=True)
        with col2:
            st.markdown("### AI 销售智能分析")
        st.caption("企业级多智能体决策系统")
        st.divider()

        # 状态指示器
        status_col1, status_col2 = st.columns([1, 4])
        with status_col1:
            status_color = "#28a745" if st.session_state.api_status == "online" else "#dc3545"
            st.markdown(f'<span class="status-indicator" style="background-color: {status_color};"></span>',
                        unsafe_allow_html=True)
        with status_col2:
            status_text = "服务正常" if st.session_state.api_status == "online" else "服务异常"
            st.caption(f"状态: {status_text}")

        st.divider()

        # 新建会话按钮
        if st.button("➕ 新建对话", use_container_width=True, type="primary"):
            new_sid = api_create_session()
            if new_sid:
                st.session_state.session_id = new_sid
                st.session_state.messages = []
                st.rerun()

        st.divider()

        # 历史对话列表
        st.markdown("### 📜 历史对话")

        # 加载会话列表
        if not st.session_state.sessions:
            sessions = api_get_sessions()
            st.session_state.sessions = sessions
        else:
            sessions = st.session_state.sessions

        if sessions:
            for idx, sess in enumerate(sessions):
                sid = sess.get("session_id", "")
                title = sess.get("title", "未命名会话")
                time_str = ""

                # 格式化时间
                if "create_time" in sess:
                    time_str = sess["create_time"][5:10]  # MM-DD
                elif "time" in sess:
                    try:
                        dt = datetime.fromisoformat(sess["time"].replace('Z', '+00:00'))
                        time_str = dt.strftime("%m-%d %H:%M")
                    except:
                        time_str = ""

                # 会话项容器
                is_active = sid == st.session_state.session_id
                active_class = "active" if is_active else ""

                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="session-item {active_class}" onclick="console.log('clicked')">
                            <div class="title">{title}</div>
                            <div class="time">{time_str}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("切换", key=f"switch_{idx}", use_container_width=True,
                                     type="secondary" if not is_active else "primary"):
                            st.session_state.session_id = sid
                            st.session_state.messages = api_get_session_messages(sid)
                            st.rerun()
        else:
            st.info("暂无历史对话记录")
            st.markdown("---")
            st.caption("点击上方按钮创建新对话")


# --------------------------
# 主界面组件
# --------------------------
def render_main_content():
    """渲染主界面"""
    # 顶部标题栏
    col1, col2, col3 = st.columns([6, 1, 1])
    with col1:
        st.markdown("## 🤖AI销售智能分析代理")
    with col2:
        st.markdown("### 🎯专业版")
    with col3:
        if st.button("🚀部署", use_container_width=True):
            st.info("部署功能开发中...")

    # 当前会话信息
    if st.session_state.session_id:
        sessions = st.session_state.sessions
        current_session = next((s for s in sessions if s.get("session_id") == st.session_state.session_id), None)
        if current_session:
            st.caption(f"当前会话: {current_session.get('title', '未命名会话')}")

    # 聊天消息区域
    chat_container = st.container()

    with chat_container:
        # 显示欢迎消息
        if not st.session_state.messages and not st.session_state.session_id:
            st.markdown("---")
            st.markdown("### 👋 欢迎使用 AI 销售智能分析代理")
            st.markdown("""
            **功能介绍：**
            - 💼 智能销售策略分析
            - 📈 市场趋势预测
            - 👥 客户画像分析
            - 🤖 多智能体协同决策

            **使用方式：**
            1. 点击左侧"新建对话"开始
            2. 输入您的销售相关问题
            3. 获取专业的智能分析
            """)

        # 显示聊天历史
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                # 使用自定义样式包装消息
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-message">{msg["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="assistant-message">{msg["content"]}</div>', unsafe_allow_html=True)

    # 输入区域
    st.markdown("---")
    prompt = st.chat_input(
        "输入您想分析的内容...",
        disabled=st.session_state.waiting_for_response,
        key="chat_input"
    )

    return prompt


# --------------------------
# 处理消息发送
# --------------------------
def handle_user_message(prompt):
    """处理用户发送的消息"""
    if not st.session_state.session_id:
        new_sid = api_create_session()
        if not new_sid:
            st.error("创建会话失败")
            return
        st.session_state.session_id = new_sid

    # 添加用户消息到界面
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.session_state.waiting_for_response = True

    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(f'<div class="user-message">{prompt}</div>', unsafe_allow_html=True)

    st.rerun()


# --------------------------
# 处理AI响应
# --------------------------
def handle_ai_response():
    """处理AI响应"""
    if not st.session_state.waiting_for_response or not st.session_state.pending_prompt:
        return

    with st.chat_message("assistant"):
        response_container = st.empty()
        full_response = ""

        try:
            # 发送请求获取流式响应
            response = api_send_message(
                st.session_state.session_id,
                st.session_state.pending_prompt
            )

            if response and response.status_code == 200:
                st.session_state.api_status = "online"

                # 处理流式响应
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line.decode("utf-8"))
                            # 根据您的API响应结构调整
                            if "summary" in data and "result" in data["summary"]:
                                chunk = data["summary"]["result"].get("analysis", "")
                            elif "analysis" in data:
                                chunk = data["analysis"]
                            else:
                                # 尝试其他可能的字段
                                chunk = str(data)

                            if chunk:
                                full_response += chunk
                                response_container.markdown(f'<div class="assistant-message">{full_response}</div>',
                                                            unsafe_allow_html=True)
                        except json.JSONDecodeError:
                            continue
            else:
                full_response = "❌ 服务暂时不可用，请稍后重试"
                response_container.markdown(f'<div class="assistant-message">{full_response}</div>',
                                            unsafe_allow_html=True)

        except Exception as e:
            full_response = f"❌ 请求发生错误: {str(e)}"
            response_container.markdown(f'<div class="assistant-message">{full_response}</div>', unsafe_allow_html=True)
            st.session_state.api_status = "offline"

        # 保存响应到消息历史
        st.session_state.messages.append({"role": "assistant", "content": full_response})

    # 重置状态
    st.session_state.pending_prompt = ""
    st.session_state.waiting_for_response = False
    st.rerun()


# --------------------------
# 主应用逻辑
# --------------------------
def main():
    """主应用函数"""
    # 初始化状态
    initialize_session_state()

    # 渲染侧边栏
    render_sidebar()

    # 渲染主内容
    prompt = render_main_content()

    # 处理用户输入
    if prompt and not st.session_state.waiting_for_response:
        handle_user_message(prompt)

    # 处理AI响应
    if st.session_state.waiting_for_response:
        handle_ai_response()

    # 检查API状态
    if st.session_state.api_status == "checking":
        try:
            # 简单测试API连接
            test_response = requests.get("http://127.0.0.1:8000/api/chat/get_sessions?skip=0&limit=1", timeout=60)
            if test_response.status_code == 200:
                st.session_state.api_status = "online"
            else:
                st.session_state.api_status = "offline"
        except:
            st.session_state.api_status = "offline"


# --------------------------
# 运行应用
# --------------------------
if __name__ == "__main__":
    main()