# streamlit_app.py
import streamlit as st
import json
import requests
import time
from datetime import datetime
import re
from typing import List, Dict, Any, Optional

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
# 自定义CSS样式
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
    display: block;
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
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    line-height: 1.4;
    padding: 2px 0;
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

/* 移除时间显示的CSS */
.no-time-display {
    margin-bottom: 0;
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

/* 分析中动画样式 */
.thinking-container {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
    padding: 12px 16px;
    background-color: #ffffff;
    border: 1px solid #eee;
    border-radius: 18px 18px 18px 4px;
    max-width: 70%;
}
.thinking-dots {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    margin-left: 8px;
}
.thinking-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: #999;
    animation: thinking 1.4s infinite ease-in-out both;
}
.thinking-dot:nth-child(1) {
    animation-delay: -0.32s;
}
.thinking-dot:nth-child(2) {
    animation-delay: -0.16s;
}
@keyframes thinking {
    0%, 80%, 100% { 
        transform: scale(0);
        opacity: 0.5;
    } 
    40% { 
        transform: scale(1.0);
        opacity: 1;
    }
}

/* 分析结果卡片样式 */
.analysis-card {
    background-color: #ffffff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    padding: 20px;
    margin: 10px 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.analysis-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}
.company-name {
    font-size: 20px;
    font-weight: bold;
    color: #1a1a1a;
}
.score-badge {
    background-color: #e6f0ff;
    color: #0066cc;
    padding: 6px 12px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 16px;
}
.analysis-section {
    margin-bottom: 20px;
}
.section-title {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
}
.section-title:before {
    content: "📊";
    margin-right: 8px;
}
.section-content {
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    padding: 12px;
    border-radius: 6px;
    border-left: 4px solid #0066cc;
}
.recommendation-section {
    background-color: #f0f7ff;
    border: 1px solid #cce0ff;
    border-radius: 8px;
    padding: 15px;
    margin-top: 20px;
}
.recommendation-title {
    font-size: 16px;
    font-weight: 600;
    color: #0066cc;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
}
.recommendation-title:before {
    content: "💡";
    margin-right: 8px;
}
.recommendation-content {
    font-size: 14px;
    line-height: 1.6;
    color: #333;
}
</style>
""", unsafe_allow_html=True)


# --------------------------
# 工具函数
# --------------------------
def parse_message_content(content):
    """
    智能解析消息内容
    支持多种格式：JSON字符串、字典、字符串
    """
    if content is None:
        return None

    # 如果是字典，直接返回
    if isinstance(content, dict):
        return content

    # 如果是字符串
    if isinstance(content, str):
        # 去除首尾空白
        content = content.strip()

        # 尝试解析为JSON
        try:
            # 检查是否是JSON字符串
            if content.startswith('{') and content.endswith('}'):
                return json.loads(content)
        except json.JSONDecodeError:
            # 如果解析失败，尝试清理可能的格式问题
            try:
                # 尝试修复常见的JSON格式问题
                # 1. 将单引号替换为双引号
                fixed_content = content.replace("'", '"')
                # 2. 移除多余的空白
                fixed_content = re.sub(r'\s+', ' ', fixed_content)
                return json.loads(fixed_content)
            except:
                # 如果还是失败，返回原字符串
                return content

    # 其他类型，直接返回
    return content


def api_create_session():
    """创建新会话"""
    try:
        res = requests.get("http://127.0.0.1:8000/api/chat/add_session", timeout=20)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200 or data.get("code") == "success":
                return data.get("data", "")
    except:
        pass
    return None


def api_get_sessions():
    """获取会话列表并按时间倒序排序"""
    try:
        res = requests.get(
            "http://127.0.0.1:8000/api/chat/get_sessions?skip=0&limit=20",
            timeout=20
        )
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200 or data.get("code") == "success":
                sessions = data.get("data", [])

                def sort_by_create_time(session):
                    create_time = session.get("create_time", "")
                    try:
                        if "T" in create_time:
                            return datetime.fromisoformat(create_time.replace('Z', '+00:00'))
                        else:
                            return datetime.fromisoformat(create_time)
                    except:
                        return datetime.min

                sessions.sort(key=sort_by_create_time, reverse=True)
                return sessions
    except:
        pass
    return []


def api_get_session_messages(session_id: str):
    """获取会话消息 - 修复版本"""
    try:
        res = requests.get(
            f"http://127.0.0.1:8000/api/chat/get_session/{session_id}",
            timeout=20
        )
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200 or data.get("code") == "success":
                messages = data.get("data", [])

                formatted_messages = []
                for msg in messages:
                    content = msg.get("content", "")
                    role = msg.get("role", "user")

                    # 智能解析内容
                    parsed_content = parse_message_content(content)

                    # 如果是普通文本，但包含JSON结构，尝试进一步解析
                    if isinstance(parsed_content, str) and "{" in parsed_content and "}" in parsed_content:
                        # 尝试提取JSON部分
                        try:
                            start_idx = parsed_content.find('{')
                            end_idx = parsed_content.rfind('}') + 1
                            if start_idx != -1 and end_idx != 0:
                                json_str = parsed_content[start_idx:end_idx]
                                parsed_content = json.loads(json_str)
                        except:
                            pass

                    formatted_messages.append({
                        "role": role,
                        "content": parsed_content
                    })

                return formatted_messages
    except Exception as e:
        st.warning(f"获取会话消息时出错: {str(e)}")
    return []


def api_send_message(session_id: str, question: str):
    """发送消息并获取完整响应"""
    try:
        response = requests.post(
            url="http://127.0.0.1:8000/api/chat/dialogue",
            json={
                "session_id": session_id,
                "question": question
            },
            timeout=300
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("code") == 200 or data.get("code") == "success":
                return data.get("data", {})
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

    if "is_analyzing" not in st.session_state:
        st.session_state.is_analyzing = False

    if "pending_prompt" not in st.session_state:
        st.session_state.pending_prompt = ""

    if "sessions" not in st.session_state:
        st.session_state.sessions = []

    if "api_status" not in st.session_state:
        st.session_state.api_status = "unknown"

    if "last_refresh" not in st.session_state:
        st.session_state.last_refresh = 0


def refresh_sessions():
    """刷新会话列表"""
    try:
        sessions = api_get_sessions()
        st.session_state.sessions = sessions
        st.session_state.last_refresh = time.time()

        if sessions is not None:
            st.session_state.api_status = "online"
        else:
            st.session_state.api_status = "offline"
    except:
        st.session_state.api_status = "offline"


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
            st.markdown("销售智能分析")
        st.caption(
            "用于快速分析目标客户、行业动态与市场机会，一键生成客户价值评分与合作建议，帮助销售团队精准获客、提升转化效率。")
        st.divider()

        # 状态指示器
        status_color = "#28a745" if st.session_state.api_status == "online" else "#dc3545"
        status_text = "服务正常" if st.session_state.api_status == "online" else "服务异常"

        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f'<span class="status-indicator" style="background-color: {status_color};"></span>',
                        unsafe_allow_html=True)
        with col2:
            st.caption(f"状态: {status_text}")

        # 刷新按钮
        if st.button("🔄 刷新列表", use_container_width=True, type="secondary"):
            refresh_sessions()
            st.rerun()

        st.divider()

        # 新建会话按钮
        if st.button("➕ 新建对话", use_container_width=True, type="primary"):
            new_session_id = api_create_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                refresh_sessions()
                st.session_state.messages = []
                st.rerun()

        st.divider()

        # 历史对话列表
        st.markdown("### 📜 历史对话")

        if (time.time() - st.session_state.last_refresh > 30 or
                not st.session_state.sessions):
            refresh_sessions()

        sessions = st.session_state.sessions

        if sessions:
            for idx, sess in enumerate(sessions):
                sid = sess.get("session_id", "")
                title = sess.get("title", "未命名会话")
                display_title = title[:22] + "..." if len(title) > 25 else title
                is_active = sid == st.session_state.session_id
                active_class = "active" if is_active else ""

                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        st.markdown(f"""
                        <div class="session-item {active_class} no-time-display">
                            <div class="title">📝 {display_title}</div>
                        </div>
                        """, unsafe_allow_html=True)

                    with col2:
                        if st.button("切换", key=f"switch_{idx}", use_container_width=True):
                            st.session_state.session_id = sid
                            messages = api_get_session_messages(sid)
                            st.session_state.messages = messages
                            st.rerun()
        else:
            st.info("暂无历史对话记录")
            st.markdown("---")
            st.caption("点击上方按钮创建新对话")


# --------------------------
# 渲染分析结果卡片
# --------------------------
def render_analysis_card(analysis_data: Dict[str, Any]):
    """渲染公司分析卡片"""
    if not analysis_data:
        return

    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-header">
            <div class="company-name">📈 销售智能分析报告</div>
    """, unsafe_allow_html=True)

    # 如果有评分，显示评分
    score = analysis_data.get("score", 0)
    if score and score > 0:
        st.markdown(f'<div class="score-badge">评分: {score}</div>', unsafe_allow_html=True)

    st.markdown("""
        </div>
    """, unsafe_allow_html=True)

    # 公司信息
    company = analysis_data.get("company", "")
    if company and company not in ["未提供", "", "无", "null", "None"]:
        st.markdown("""
        <div class="analysis-section">
            <div class="section-title">目标公司</div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        st.write(f"**{company}**")
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 行业信息
    industry = analysis_data.get("industry", "")
    if industry and industry not in ["未提供", "", "无", "null", "None"]:
        st.markdown("""
        <div class="analysis-section">
            <div class="section-title">所属行业</div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        st.write(f"**{industry}**")
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 分析结果
    analysis = analysis_data.get("analysis", "")
    if analysis:
        st.markdown("""
        <div class="analysis-section">
            <div class="section-title">分析结果</div>
            <div class="section-content">
        """, unsafe_allow_html=True)
        st.write(analysis)
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 合作建议
    recommendation = analysis_data.get("recommendation", "")
    if recommendation and recommendation not in ["自然闲聊", "", "null", "None"]:
        st.markdown("""
        <div class="recommendation-section">
            <div class="recommendation-title">合作建议</div>
            <div class="recommendation-content">
        """, unsafe_allow_html=True)
        st.write(recommendation)
        st.markdown("""
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# --------------------------
# 主界面组件
# --------------------------
def render_main_content():
    """渲染主界面"""
    # 顶部标题栏
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("# 🤖 销售智能分析代理")
    with col2:
        if st.button("📊生成报表", use_container_width=True):
            st.info("报表功能开发中...")

    st.markdown("---")

    # 当前会话信息
    if st.session_state.session_id:
        current_session = None
        for sess in st.session_state.sessions:
            if sess.get("session_id") == st.session_state.session_id:
                current_session = sess
                break

        if current_session:
            title = current_session.get("title", "未命名会话")
            st.caption(f"当前会话: {title}")
        else:
            st.caption(f"当前会话ID: {st.session_state.session_id[:20]}...")
    else:
        st.caption("未选择任何会话，请新建或选择历史会话")

    # 显示聊天历史
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg.get("content", "")

            # 智能解析内容
            parsed_content = parse_message_content(content)

            # 根据内容类型渲染
            if isinstance(parsed_content, dict):
                # 字典类型
                if "type" in parsed_content:
                    # 有type字段的结构化数据
                    if parsed_content.get("type") == "analysis":
                        # 公司分析卡片
                        data = parsed_content.get("data", {})
                        if isinstance(data, dict):
                            render_analysis_card(data)
                        else:
                            st.write(parsed_content.get("content", ""))
                    else:
                        # 自然闲聊
                        st.write(parsed_content.get("content", ""))
                elif "company" in parsed_content or "analysis" in parsed_content:
                    # 可能是analysis格式的直接字典
                    render_analysis_card(parsed_content)
                else:
                    # 其他字典，显示JSON
                    st.json(parsed_content)
            else:
                # 字符串或其他类型
                st.write(str(parsed_content))

    # 显示AI分析中的动画
    if st.session_state.is_analyzing and st.session_state.pending_prompt:
        st.markdown("""
        <div class="thinking-container">
            🤔 AI分析中
            <div class="thinking-dots">
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
                <div class="thinking-dot"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 显示欢迎消息
    if not st.session_state.messages and not st.session_state.session_id and not st.session_state.is_analyzing:
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

    # 输入区域
    st.markdown("---")
    prompt = st.chat_input(
        "输入您想分析的内容...",
        disabled=st.session_state.is_analyzing,
        key="chat_input"
    )

    return prompt


# --------------------------
# 处理消息发送
# --------------------------
def handle_user_message(prompt: str):
    """处理用户发送的消息"""
    # 1. 检查是否有会话ID，没有则创建
    if not st.session_state.session_id:
        new_session_id = api_create_session()
        if not new_session_id:
            st.error("❌ 创建会话失败，无法发送消息")
            return False

        st.session_state.session_id = new_session_id

    # 2. 添加用户消息到历史记录
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 3. 设置状态
    st.session_state.pending_prompt = prompt
    st.session_state.is_analyzing = True

    # 4. 刷新会话列表
    refresh_sessions()

    st.rerun()
    return True


# --------------------------
# 处理AI响应
# --------------------------
def handle_ai_response():
    """处理AI响应"""
    if not st.session_state.is_analyzing or not st.session_state.pending_prompt:
        return

    # 调用API获取AI响应
    try:
        response_data = api_send_message(
            st.session_state.session_id,
            st.session_state.pending_prompt
        )

        if response_data:
            # 保存响应到消息历史
            st.session_state.messages.append({
                "role": "assistant",
                "content": response_data
            })
        else:
            # API调用失败
            st.session_state.messages.append({
                "role": "assistant",
                "content": "❌ 服务暂时不可用，请稍后重试"
            })

    except Exception as e:
        # 异常处理
        st.session_state.messages.append({
            "role": "assistant",
            "content": f"❌ 请求发生错误: {str(e)}"
        })

    # 重置状态
    st.session_state.pending_prompt = ""
    st.session_state.is_analyzing = False

    # 再次刷新会话列表
    refresh_sessions()
    st.rerun()


# --------------------------
# 主应用逻辑
# --------------------------
def main():
    """主应用函数"""
    # 初始化状态
    initialize_session_state()

    # 页面初始化时加载历史会话
    if not st.session_state.sessions or st.session_state.last_refresh == 0:
        refresh_sessions()

    # 渲染侧边栏
    render_sidebar()

    # 渲染主内容
    prompt = render_main_content()

    # 处理用户输入
    if prompt and not st.session_state.is_analyzing:
        success = handle_user_message(prompt)
        if not success:
            st.error("❌ 发送消息失败")

    # 处理AI响应
    if st.session_state.is_analyzing:
        handle_ai_response()


# --------------------------
# 运行应用
# --------------------------
if __name__ == "__main__":
    main()