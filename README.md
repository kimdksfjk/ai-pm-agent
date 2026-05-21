# AI PM Agent (ai-pm-agent)

> 基于 LangGraph + DeepSeek 的 LLM 智能产品经理 Agent。通过对话引导用户定义需求，自动生成 PlantUML 用例图、活动图和 PRD 文档。

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-WebSocket-green)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-ReAct Agent-orange)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

## ✨ 核心功能

- **🎭 双模式 Agent** — `PM 模式` 与需求方沟通，`Dev 模式` 与开发者对齐
- **📊 PlantUML 生成** — 根据自然语言自动生成用例图、活动图代码
- **📝 PRD 文档** — 一键生成结构化产品需求文档
- **🧠 AI 推理驱动** — LangGraph ReAct Agent，自主决定何时提问、何时调用工具
- **💬 WebSocket 实时对话** — 深色主题聊天界面，Markdown 实时渲染
- **🧩 结构化需求分析** — 5W1H 框架 + 边界条件 + 验收标准
- **💾 持久化记忆** — SQLite 存储对话历史，刷新页面、重启服务都不丢
- **🔄 自动重连** — 指数退避重连机制，断线自动恢复

## 🏗 架构图

```
┌─────────────────────────────────┐
│     浏览器聊天界面 (WebSocket)     │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│      FastAPI + WebSocket         │  ← 通信层
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│    PMAgent (LangGraph ReAct)     │  ← Agent 核心
│  ┌──────────┬──────────┬──────┐ │
│  │ 工具调用  │ 记忆系统  │ 模式  │ │
│  │ 4个工具  │ SQLite   │ 切换  │ │
│  └──────────┴──────────┴──────┘ │
└──────────────┬──────────────────┘
               │
┌──────────────▼──────────────────┐
│      DeepSeek API (deepseek-chat)│  ← LLM 引擎
└─────────────────────────────────┘
```

## 📁 项目结构

```
agent/
├── agent/
│   ├── __init__.py
│   ├── pm_agent.py       # Agent 核心（LangGraph）
│   ├── prompts.py        # 双模式 System Prompt
│   ├── tools.py          # 4 个 PM 工具
│   ├── memory.py         # 对话记忆（SQLite）
│   └── database.py       # SQLite 增删改查
├── static/
│   └── index.html        # 聊天界面（WebSocket + Markdown）
├── server.py             # FastAPI 入口
├── config.py             # 配置管理
├── .env.example          # 环境变量模板
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 前置条件

- Python 3.10+
- [DeepSeek API Key](https://platform.deepseek.com/)

### 安装

```bash
# 克隆仓库
cd ai-pm-agent

# 创建虚拟环境
python -m venv venv

# 激活（Windows）
venv\Scripts\activate
# 激活（macOS/Linux）
source venv/bin/activate

# 安装依赖
pip install fastapi uvicorn langchain-openai langgraph langchain-classic \
    python-dotenv pydantic
```

### 配置

```bash
# 复制环境变量模板
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux

# 编辑 .env 填入你的 API Key
# OPENAI_API_KEY=sk-your-deepseek-api-key-here
```

### 启动

```bash
python server.py
```

打开 **http://127.0.0.1:8000** 即可与 AI 产品经理对话。

## 🎮 使用方式

### Web 聊天界面

打开浏览器直接跟「老钱」聊需求，他会引导你一步步把模糊的想法变成清晰的产品文档。

### 内置命令

| 命令 | 说明 |
|------|------|
| `/pm` | 切换到 PM 模式（产品定义，通俗语言） |
| `/dev` | 切换到 Dev 模式（开发者沟通，技术语言） |
| `/project <名称>` | 创建或切换到指定项目 |
| `/project` | 查看当前项目信息 |

### API 接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 聊天界面 |
| `/ws?session_id=<id>` | WebSocket | 实时对话 |
| `/chat` | POST | HTTP 对话（JSON: `{"message":"...", "session_id":"..."}`） |
| `/mode` | POST | 切换模式（JSON: `{"mode":"pm|dev", "session_id":"..."}`） |
| `/api` | GET | 接口信息 |

## 🛠 内置 PM 工具

| 工具 | 触发时机 | 输出 |
|------|---------|------|
| `analyze_requirement` | 用户描述需求后 | 结构化分析报告（角色、流程、边界、验收标准） |
| `generate_use_case_diagram` | 角色和用例确认后 | PlantUML 用例图代码 |
| `generate_activity_diagram` | 业务流程清晰后 | PlantUML 活动图/流程图代码 |
| `generate_prd` | 需求讨论充分后 | PRD 文档概要 |

### 示例：生成用例图

```
用户: 我想做一个校园二手交易平台。
老钱: [追问角色、范围、功能...]
用户: 买家可以浏览购买，卖家可以发布商品，管理员审核举报。
老钱: [调用 generate_use_case_diagram]

输出:
@startuml
title 校园二手交易平台
left to right direction
actor "买家" as A1
actor "卖家" as A2
actor "管理员" as A3
usecase "浏览购买" as UC1
usecase "发布商品" as UC2
usecase "审核举报" as UC3
A1 --> UC1
A2 --> UC2
A3 --> UC3
@enduml
```

复制代码到 [plantuml.com](https://www.plantuml.com/) 即可渲染成图。

## 🧠 Agent 人格

Agent 化身「**老钱**」——一个有 8 年经验的产品经理，同时也是严谨的工程师：

- **先问再动** — 永远先通过 5W1H 框架澄清需求，绝不急于输出
- **严谨而宽容** — 会指出逻辑漏洞，但语气建设性、合作式
- **结构化思维** — 场景 → 角色 → 核心流程 → 边界条件 → 验收标准
- **拒绝模糊** — 遇到「大概」「可能」「差不多」立即追问
- **确认后执行** — 先总结理解，等用户确认后再生成图表或文档

## 🔧 技术栈

| 层级 | 技术 |
|------|------|
| Web 框架 | FastAPI + WebSocket |
| Agent 框架 | LangGraph (create_react_agent) |
| 大模型 | DeepSeek (deepseek-chat) |
| 记忆存储 | SQLite（对话持久化） |
| 图表生成 | PlantUML（文本生成图表） |
| 前端 | 原生 HTML/CSS/JS（零框架） |

## 📄 开源协议

MIT — 自由使用、修改、分发。

## 🤝 贡献

这是个人学习与求职作品，欢迎提 Issue 和 PR！
