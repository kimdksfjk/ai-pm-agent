from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from config import LLM_MODEL, LLM_API_KEY, LLM_BASE_URL, LLM_TEMPERATURE
from agent.prompts import build_system_prompt
from agent.memory import MemoryManager
from agent.tools import PM_TOOLS
from agent import database


class PMAgent:
    def __init__(self, project_id: str | None = None):
        self.memory = MemoryManager(project_id or "default")
        self.project_id = project_id
        self.mode = "pm"
        self.use_mock = not LLM_API_KEY
        self._last_ai_message: AIMessage | None = None

        if project_id:
            project = database.get_project(project_id)
            if project:
                self.mode = project.get("mode", "pm")

        if not self.use_mock:
            try:
                self.llm = ChatOpenAI(
                    model=LLM_MODEL,
                    api_key=LLM_API_KEY,
                    base_url=LLM_BASE_URL,
                    temperature=LLM_TEMPERATURE,
                )
                self._build_agent()
            except Exception as e:
                print(f"LLM 初始化失败，进入 Mock 模式: {e}")
                self.use_mock = True
        else:
            print("未设置 API Key，运行在 Mock 模式")

    def _build_agent(self):
        system_text = build_system_prompt(self.mode)
        self.agent = create_react_agent(
            model=self.llm,
            tools=PM_TOOLS,
            prompt=SystemMessage(content=system_text),
        )

    def set_mode(self, mode: str):
        if mode in ("pm", "dev"):
            self.mode = mode
            self._last_ai_message = None
            if not self.use_mock:
                self._build_agent()
            if self.project_id:
                database.update_project(self.project_id, mode=mode)

    def chat(self, user_input: str) -> str:
        if user_input.strip().lower() == "/pm":
            self.set_mode("pm")
            return "已切换到 PM Mode（产品定义模式）。有什么需求想聊的？"

        if user_input.strip().lower() == "/dev":
            self.set_mode("dev")
            return "已切换到 Dev Mode（开发者沟通模式）。有什么需求需要我协助分析？"

        if user_input.strip().lower() == "/project":
            return self._show_project_info()

        if user_input.strip().lower().startswith("/project "):
            return self._create_or_switch_project(user_input)

        self.memory.add_message("human", user_input)

        if self.use_mock:
            response = self._mock_chat(user_input)
            self.memory.add_message("ai", response)
        else:
            response = self._real_chat(user_input)
            if self._last_ai_message is not None:
                self.memory.add_message("ai", self._last_ai_message)
                self._last_ai_message = None
            else:
                self.memory.add_message("ai", response)

        return response

    def _real_chat(self, user_input: str) -> str:
        try:
            chat_history = self.memory.get_chat_history()
            context = self.memory.get_context_for_prompt()

            if context:
                user_input = f"{context}\n\n用户当前输入: {user_input}"

            messages = list(chat_history) + [HumanMessage(content=user_input)]

            result = self.agent.invoke({"messages": messages})
            output_messages = result.get("messages", [])
            if output_messages:
                last_msg = output_messages[-1]
                self._last_ai_message = last_msg
                return last_msg.content
            return "（Agent 未返回内容）"
        except Exception as e:
            return f"[系统错误] {str(e)}\n请重试或输入 /pm 或 /dev 切换模式。"

    def _mock_chat(self, user_input: str) -> str:
        text = user_input.lower()
        if any(kw in text for kw in ["用例图", "用例", "usecase"]):
            example = generate_use_case_diagram.invoke({
                "actors": "买家,卖家", "use_cases": "浏览商品,发布商品,下单购买",
                "relations": "买家--浏览商品,卖家--发布商品,买家--下单购买",
                "title": "二手交易平台用例图"
            })
            return (
                "好的，我帮你生成了一个用例图（Mock 模式）。以下是 PlantUML 代码：\n\n"
                f"```plantuml\n{example}\n```\n\n"
                "配置 API Key 后我可以根据你的具体需求生成更精确的图表。"
            )

        if any(kw in text for kw in ["流程图", "活动图", "流程"]):
            example = generate_activity_diagram.invoke({
                "steps": "用户登录,浏览商品,加入购物车,确认订单,支付,完成",
                "title": "购物流程图"
            })
            return (
                "好的，我帮你生成了一个流程图（Mock 模式）。以下是 PlantUML 代码：\n\n"
                f"```plantuml\n{example}\n```\n\n"
                "配置 API Key 后我可以根据你的具体需求生成更精确的图表。"
            )

        if any(kw in text for kw in ["prd", "需求文档", "需求分析"]):
            example = generate_prd.invoke({
                "title": "校园二手交易平台",
                "background": "为大学生提供校内二手物品交易服务",
                "actors": "买家,卖家,管理员",
                "core_flow": "注册登录,发布商品,浏览搜索,下单交易,确认收货",
                "acceptance_criteria": "用户可以发布商品,用户可以搜索商品,交易流程完整"
            })
            return (
                "好的，我帮你生成了一份 PRD 概要（Mock 模式）：\n\n"
                f"```markdown\n{example}\n```\n\n"
                "配置 API Key 后我可以根据你的具体需求生成更完整的 PRD。"
            )

        return (
            f"收到你的问题：「{user_input}」\n\n"
            "⚠️ 当前运行在 Mock 模式（未配置 API Key）。\n\n"
            "在 Mock 模式下我可以：\n"
            "- 如果你提到「用例图」，我会生成示例 PlantUML 用例图\n"
            "- 如果你提到「流程图」，我会生成示例流程图\n"
            "- 如果你提到「PRD」，我会生成示例 PRD 文档\n\n"
            "要启用真正的 AI 对话能力，请在 .env 文件中设置 OPENAI_API_KEY。\n"
            "使用 /pm 或 /dev 可以切换模式。"
        )

    def _show_project_info(self) -> str:
        if not self.project_id:
            return "当前没有关联项目。使用 /project <项目名> 创建或切换项目。"
        project = database.get_project(self.project_id)
        if not project:
            return "项目不存在。使用 /project <项目名> 创建新项目。"
        reqs = database.list_requirements(self.project_id)
        diagrams = database.list_diagrams(self.project_id)
        lines = [
            f"## 项目: {project['name']}",
            f"模式: {project['mode']}",
            f"背景: {project['context'] or '未设置'}",
            "",
            f"需求数: {len(reqs)}",
            f"图表数: {len(diagrams)}",
        ]
        if reqs:
            lines.append("\n### 需求列表")
            for r in reqs:
                lines.append(f"- [{r['priority']}] {r['title']} ({r['status']})")
        return "\n".join(lines)

    def _create_or_switch_project(self, user_input: str) -> str:
        name = user_input[len("/project "):].strip()
        projects = database.list_projects()
        for p in projects:
            if p["name"] == name:
                self.project_id = p["id"]
                self.mode = p.get("mode", "pm")
                self.memory = MemoryManager(p["id"])
                self._last_ai_message = None
                if not self.use_mock:
                    self._build_agent()
                return f"已切换到项目: {name}（模式: {self.mode}）"
        project = database.create_project(name, "", self.mode)
        self.project_id = project["id"]
        self.memory = MemoryManager(project["id"])
        return f"已创建项目: {name}，当前模式: {self.mode}。请描述你的需求。"


def generate_use_case_diagram(*args, **kwargs):
    return PM_TOOLS[1].invoke(kwargs)


def generate_activity_diagram(*args, **kwargs):
    return PM_TOOLS[2].invoke(kwargs)


def generate_prd(*args, **kwargs):
    return PM_TOOLS[3].invoke(kwargs)
