📋 项目简介
AI Sales Intelligence Multi-Agent System 是一个基于多智能体架构的智能销售分析系统。该系统通过多个专业化 AI Agent 的协同工作，为企业提供深度的销售数据分析、客户洞察和商业智能决策支持。
✨ 核心特性
🤖 多智能体协作：采用 LangGraph 编排多个专业 Agent，实现复杂任务分解与执行
💬 会话管理：支持多轮对话上下文记忆，提供连贯的交互体验
🧠 RAG 增强检索：结合 ChromaDB 向量数据库，实现企业知识库的精准检索
💾 数据持久化：PostgreSQL 存储会话历史，Redis 实现短期/长期记忆管理
🎨 可视化界面：基于 Streamlit 的直观前端界面，降低使用门槛
⚡ 高性能 API：FastAPI 构建的异步后端服务，支持高并发访问
🔄 动态路由：LLM 驱动的智能路由，自动选择最优处理路径
🛠️ 技术栈
后端框架​：FastAPI
前端框架​：Streamlit
Agent编排：LangGraph
向量数据库​：ChromaDB
关系型数据库：PostgreSQL​
缓存/记忆​：Redis
ORM​：SQLAlchemy
LLM：DeepSeek
📁 项目结构
AI-Sales-Intelligence-Multi-Agent-System/
├── api/                    # API 路由定义
│   └── endpoints/          # 各模块接口
├── config/                 # 配置文件
├── crud/                   # 数据库 CRUD 操作
├── db/                     # 数据库连接与初始化
├── graph/                  # LangGraph 工作流定义
├── knowledge/              # 企业知识库文件
├── model/                  # LLM 模型配置与管理
├── node/                   # Agent 节点实现
├── prompt/                 # Prompt 模板管理
├── rag/                    # RAG 检索增强生成模块
├── schemas/                # Pydantic 数据模型
├── state/                  # 会话状态管理
├── tools/                  # Agent 可用工具集
├── data/
│   └── chroma_db/         # ChromaDB 数据存储
├── app_front.py           # Streamlit 前端入口
├── main.py                # FastAPI 后端入口
└── README.md
🚀 快速开始
环境要求
Python 3.9+
PostgreSQL 12+
Redis 6+
安装步骤
克隆仓库
git clone https://github.com/mmskr666/AI-Sales-Intelligence-Multi-Agent-System.git
cd AI-Sales-Intelligence-Multi-Agent-System
创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
安装依赖
pip install -r requirements.txt
配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接、API Key 等
初始化数据库
python -m db.init_db
启动服务
启动后端 API：
uvicorn main:app --reload --host 0.0.0.0 --port 8000
访问 http://localhost:8000/docs查看 API 文档
启动前端界面：
streamlit run app_front.py
访问 http://localhost:8501使用 Web 界面

前端功能
💬 智能对话：自然语言查询销售数据
📊 数据可视化：自动生成图表和分析报告
📚 知识库管理：上传和管理企业文档
📝 会话历史：查看和导出历史对话记录

🤝 贡献指南
欢迎提交 Issue 和 Pull Request！
Fork 本项目
创建特性分支 (git checkout -b feature/AmazingFeature)
提交更改 (git commit -m 'Add some AmazingFeature')
推送到分支 (git push origin feature/AmazingFeature)
开启 Pull Request
⭐ 如果这个项目对你有帮助，请给它一个 Star！
