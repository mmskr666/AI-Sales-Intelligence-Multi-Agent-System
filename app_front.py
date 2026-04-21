from typing import TypedDict, Any, Annotated
import operator
import streamlit as st
import json
import requests
import time
from datetime import datetime
import re
from typing import List, Dict, Any, Optional
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

# ======================
# Excel 工具
# ======================
import pandas as pd

from tools.dict_to_excel import dict_to_excel


# --------------------------
# 邮件发送函数（内置）
# --------------------------
def send_report_email(to_email: str, subject: str, analysis_data: dict):
    try:
        # ------------ 发件邮箱配置 ------------
        smtp_server = "smtp.163.com"       # 根据你的邮箱改：smtp.qq.com / smtp.163.com / smtp.exmail.qq.com
        smtp_port = 465                   # 端口一般 465
        sender_email = "你的邮箱@163.com"
        sender_name = "销售智能分析助手"
        sender_pwd = "你的邮箱授权码"       # 不是登录密码，是授权码
        # ------------------------------------

        # 构造邮件正文
        html = f"""
        <html>
        <body>
        <h2>📊 客户分析报告</h2>
        <p><strong>公司名称：</strong>{analysis_data.get('company', '无')}</p>
        <p><strong>所属行业：</strong>{analysis_data.get('industry', '无')}</p>
        <p><strong>客户评分：</strong>{analysis_data.get('score', '无')}</p>
        <hr>
        <h4>分析结果</h4>
        <p>{analysis_data.get('analysis', '无')}</p>
        <hr>
        <h4>合作建议</h4>
        <p>{analysis_data.get('recommendation', '无')}</p>
        <br>
        <p>—— 由 AI 销售智能分析助手自动发送</p>
        </body>
        </html>
        """

        msg = MIMEText(html, "html", "utf-8")
        msg["From"] = formataddr((sender_name, sender_email))
        msg["To"] = to_email
        msg["Subject"] = subject

        # 发送
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(sender_email, sender_pwd)
            server.sendmail(sender_email, [to_email], msg.as_string())

        return True
    except Exception as e:
        print("邮件发送失败:", e)
        return False


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
# CSS
# --------------------------
st.markdown("""
<style>
.main {padding-top: 20px;}
.main .block-container {padding-top: 20px;}
[data-testid="stSidebar"] {background-color: #f8f9fa;}
.session-item {
    padding: 8px 12px; border-radius: 8px; margin:4px 0; cursor:pointer;
    border:1px solid transparent;
}
.session-item:hover {background:#f0f7ff; border-color:#d0e3ff;}
.session-item.active {background:#e6f0ff; border-color:#0066cc; font-weight:500;}
.stButton>button {border-radius:8px; transition: all .3s;}
.stButton>button:hover {transform:translateY(-1px); box-shadow:0 4px 12px rgba(0,0,0,0.1);}
.thinking-container {
    display:flex; align-items:center; margin-bottom:10px; padding:12px 16px;
    background:#fff; border:1px solid #eee; border-radius:18px 18px 18px 4px; max-width:70%;
}
.thinking-dots {display:inline-flex; gap:4px; margin-left:8px;}
.thinking-dot {width:8px;height:8px;border-radius:50%;background:#999;animation:thinking 1.4s infinite;}
.thinking-dot:nth-child(1){animation-delay:-0.32s;}
.thinking-dot:nth-child(2){animation-delay:-0.16s;}
@keyframes thinking {
    0%,80%,100%{transform:scale(0);opacity:.5;}40%{transform:scale(1);opacity:1;}
}
.analysis-card {
    background:#fff; border:1px solid #e0e0e0; border-radius:8px; padding:20px; margin:10px 0;
    box-shadow:0 2px 8px rgba(0,0,0,0.05);
}
.analysis-header {
    display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;
    padding-bottom:10px; border-bottom:1px solid #eee;
}
.company-name {font-size:20px; font-weight:bold; color:#1a1a1a;}
.score-badge {
    background:#e6f0ff; color:#0066cc; padding:6px 12px; border-radius:20px;
    font-weight:bold; font-size:16px;
}
.analysis-section {margin-bottom:20px;}
.section-title {font-size:16px; font-weight:600; color:#333; margin-bottom:8px; display:flex; align-items:center;}
.section-title:before {content:"📊"; margin-right:8px;}
.section-content {
    font-size:14px; line-height:1.6; color:#333; background:#f8f9fa; padding:12px;
    border-radius:6px; border-left:4px solid #0066cc;
}
.recommendation-section {
    background:#f0f7ff; border:1px solid #cce0ff; border-radius:8px; padding:15px; margin-top:20px;
}
.recommendation-title {font-size:16px; font-weight:600; color:#0066cc; margin-bottom:8px; display:flex;align-items:center;}
.recommendation-title:before {content:"💡"; margin-right:8px;}
.recommendation-content {font-size:14px; line-height:1.6; color:#333;}
</style>
""", unsafe_allow_html=True)


# --------------------------
# 工具函数
# --------------------------
def parse_message_content(content):
    if content is None:
        return None
    if isinstance(content, dict):
        return content
    if isinstance(content, str):
        content = content.strip()
        try:
            if content.startswith('{') and content.endswith('}'):
                return json.loads(content)
        except json.JSONDecodeError:
            try:
                fixed_content = content.replace("'", '"')
                fixed_content = re.sub(r'\s+', ' ', fixed_content)
                return json.loads(fixed_content)
            except:
                return content
    return content


def api_create_session():
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
    try:
        res = requests.get("http://127.0.0.1:8000/api/chat/get_sessions?skip=0&limit=20", timeout=20)
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
    try:
        res = requests.get(f"http://127.0.0.1:8000/api/chat/get_session/{session_id}", timeout=20)
        if res.status_code == 200:
            data = res.json()
            if data.get("code") == 200 or data.get("code") == "success":
                messages = data.get("data", [])
                formatted_messages = []
                for msg in messages:
                    content = msg.get("content", "")
                    role = msg.get("role", "user")
                    parsed_content = parse_message_content(content)
                    if isinstance(parsed_content, str) and "{" in parsed_content and "}" in parsed_content:
                        try:
                            start_idx = parsed_content.find('{')
                            end_idx = parsed_content.rfind('}') + 1
                            if start_idx != -1 and end_idx != 0:
                                json_str = parsed_content[start_idx:end_idx]
                                parsed_content = json.loads(json_str)
                        except:
                            pass
                    formatted_messages.append({"role": role, "content": parsed_content})
                return formatted_messages
    except Exception as e:
        st.warning(f"获取会话消息出错: {str(e)}")
    return []


def api_send_message(session_id: str, question: str):
    try:
        response = requests.post(
            url="http://127.0.0.1:8000/api/chat/dialogue",
            json={"session_id": session_id, "question": question},
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
# 状态初始化
# --------------------------
def initialize_session_state():
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
    try:
        sessions = api_get_sessions()
        st.session_state.sessions = sessions
        st.session_state.last_refresh = time.time()
        st.session_state.api_status = "online" if sessions is not None else "offline"
    except:
        st.session_state.api_status = "offline"


# --------------------------
# 侧边栏
# --------------------------
def render_sidebar():
    with st.sidebar:
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown("📊", unsafe_allow_html=True)
        with col2:
            st.markdown("销售智能分析")
        st.caption("用于快速分析目标客户、行业动态与市场机会，一键生成客户价值评分与合作建议，帮助销售团队精准获客、提升转化效率。")
        st.divider()

        status_color = "#28a745" if st.session_state.api_status == "online" else "#dc3545"
        status_text = "服务正常" if st.session_state.api_status == "online" else "服务异常"
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f'<span class="status-indicator" style="background-color:{status_color};"></span>', unsafe_allow_html=True)
        with col2:
            st.caption(f"状态: {status_text}")

        if st.button("🔄 刷新列表", use_container_width=True, type="secondary"):
            refresh_sessions()
            st.rerun()
        st.divider()

        if st.button("➕ 新建对话", use_container_width=True, type="primary"):
            new_session_id = api_create_session()
            if new_session_id:
                st.session_state.session_id = new_session_id
                refresh_sessions()
                st.session_state.messages = []
                st.rerun()
        st.divider()

        st.markdown("### 📜 历史对话")
        if time.time() - st.session_state.last_refresh > 30 or not st.session_state.sessions:
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
                        st.markdown(f"""<div class="session-item {active_class} no-time-display"><div class="title">📝 {display_title}</div></div>""", unsafe_allow_html=True)
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
# 分析卡片 + 下载 + 发邮件
# --------------------------
def render_analysis_card(analysis_data: Dict[str, Any]):
    if not analysis_data:
        return

    st.markdown("""
    <div class="analysis-card">
        <div class="analysis-header">
            <div class="company-name">📈 销售智能分析报告</div>
    """, unsafe_allow_html=True)

    score = analysis_data.get("score", 0)
    if score and score > 0:
        st.markdown(f'<div class="score-badge">评分: {score}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    company = analysis_data.get("company", "")
    if company and company not in ["未提供", "", "无", "null", "None"]:
        st.markdown("""<div class="analysis-section"><div class="section-title">目标公司</div><div class="section-content">""", unsafe_allow_html=True)
        st.write(f"**{company}**")
        st.markdown("</div></div>", unsafe_allow_html=True)

    industry = analysis_data.get("industry", "")
    if industry and industry not in ["未提供", "", "无", "null", "None"]:
        st.markdown("""<div class="analysis-section"><div class="section-title">所属行业</div><div class="section-content">""", unsafe_allow_html=True)
        st.write(f"**{industry}**")
        st.markdown("</div></div>", unsafe_allow_html=True)

    analysis = analysis_data.get("analysis", "")
    if analysis:
        st.markdown("""<div class="analysis-section"><div class="section-title">分析结果</div><div class="section-content">""", unsafe_allow_html=True)
        st.write(analysis)
        st.markdown("</div></div>", unsafe_allow_html=True)

    recommendation = analysis_data.get("recommendation", "")
    if recommendation and recommendation not in ["自然闲聊", "", "null", "None"]:
        st.markdown("""<div class="recommendation-section"><div class="recommendation-title">合作建议</div><div class="recommendation-content">""", unsafe_allow_html=True)
        st.write(recommendation)
        st.markdown("</div></div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 下载 Excel
    try:
        excel_file = dict_to_excel(analysis_data)
        st.download_button(
            label="📥 下载分析报告 Excel",
            data=excel_file,
            file_name=f"销售分析_{pd.Timestamp.now().strftime('%Y%m%d%H%M')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except:
        pass

    # 发送邮件
    st.markdown("#### 📧 发送报告到邮箱")
    recipient = st.text_input("接收邮箱", placeholder="请输入邮箱地址", key="email_input")
    if st.button("📤 发送分析报告到邮箱", use_container_width=True):
        if not recipient:
            st.warning("请输入接收邮箱")
        else:
            subject = f"【销售分析报告】{analysis_data.get('company', '未知客户')}"
            success = send_report_email(recipient, subject, analysis_data)
            if success:
                st.success(f"✅ 已发送至：{recipient}")
            else:
                st.error("❌ 发送失败，请检查邮箱配置")


# --------------------------
# 主界面
# --------------------------
def render_main_content():
    col1, col2 = st.columns([5, 1])
    with col1:
        st.markdown("# 🤖 销售智能分析代理")
    with col2:
        if st.button("📊生成报表", use_container_width=True):
            st.info("报表功能开发中...")
    st.markdown("---")

    if st.session_state.session_id:
        current_session = None
        for sess in st.session_state.sessions:
            if sess.get("session_id") == st.session_state.session_id:
                current_session = sess
                break
        if current_session:
            st.caption(f"当前会话: {current_session.get('title','未命名会话')}")
        else:
            st.caption(f"当前会话ID: {st.session_state.session_id[:20]}...")
    else:
        st.caption("未选择任何会话，请新建或选择历史会话")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            content = msg.get("content", "")
            parsed_content = parse_message_content(content)

            if isinstance(parsed_content, dict):
                if "type" in parsed_content:
                    if parsed_content.get("type") == "analysis":
                        data = parsed_content.get("data", {})
                        if isinstance(data, dict):
                            render_analysis_card(data)
                    else:
                        st.write(parsed_content.get("content", ""))
                elif "company" in parsed_content or "analysis" in parsed_content:
                    render_analysis_card(parsed_content)
                else:
                    st.json(parsed_content)
            else:
                st.write(str(parsed_content))

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

    if not st.session_state.messages and not st.session_state.session_id and not st.session_state.is_analyzing:
        st.markdown("---")
        st.markdown("### 👋 欢迎使用 AI 销售智能分析代理")
        st.markdown("""
        **功能介绍：**
        - 💼 智能销售策略分析
        - 📈 市场趋势预测
        - 👥 客户画像分析
        - 🤖 多智能体协同决策
        """)

    st.markdown("---")
    prompt = st.chat_input("输入您想分析的内容...", disabled=st.session_state.is_analyzing, key="chat_input")
    return prompt


def handle_user_message(prompt: str):
    if not st.session_state.session_id:
        new_session_id = api_create_session()
        if not new_session_id:
            st.error("❌ 创建会话失败，无法发送消息")
            return False
        st.session_state.session_id = new_session_id

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.pending_prompt = prompt
    st.session_state.is_analyzing = True
    refresh_sessions()
    st.rerun()
    return True


def handle_ai_response():
    if not st.session_state.is_analyzing or not st.session_state.pending_prompt:
        return

    try:
        response_data = api_send_message(st.session_state.session_id, st.session_state.pending_prompt)
        if response_data:
            st.session_state.messages.append({"role": "assistant", "content": response_data})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "❌ 服务暂时不可用，请稍后重试"})
    except Exception as e:
        st.session_state.messages.append({"role": "assistant", "content": f"❌ 请求发生错误: {str(e)}"})

    st.session_state.pending_prompt = ""
    st.session_state.is_analyzing = False
    refresh_sessions()
    st.rerun()


def main():
    initialize_session_state()
    if not st.session_state.sessions or st.session_state.last_refresh == 0:
        refresh_sessions()
    render_sidebar()
    prompt = render_main_content()

    if prompt and not st.session_state.is_analyzing:
        handle_user_message(prompt)

    if st.session_state.is_analyzing:
        handle_ai_response()


if __name__ == "__main__":
    main()