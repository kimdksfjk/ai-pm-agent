from langchain_core.tools import tool


@tool
def analyze_requirement(description: str, actors: str = "", context: str = "") -> str:
    """
    对用户描述的需求进行结构化分析，输出分析报告。

    Args:
        description: 用户的需求描述
        actors: 涉及的角色，多个用逗号分隔，例如 "买家,卖家,管理员"
        context: 补充的项目背景信息，可为空
    """
    report_lines = ["## 需求分析报告\n"]
    report_lines.append(f"### 需求概述\n{description}\n")

    if actors:
        actor_list = [a.strip() for a in actors.split(",") if a.strip()]
        report_lines.append("### 涉及角色")
        for a in actor_list:
            report_lines.append(f"- {a}")
        report_lines.append("")

    if context:
        report_lines.append(f"### 项目背景\n{context}\n")

    report_lines.append("### 待澄清问题")
    report_lines.append("1. [角色] 每个角色的具体权限边界是什么？")
    report_lines.append("2. [场景] 是否存在需要特殊处理的异常场景？")
    report_lines.append("3. [数据] 哪些数据需要持久化存储？")
    report_lines.append("4. [优先级] 这个需求是 P0/P1/P2/P3 哪一级？")
    report_lines.append("5. [验收] 怎样判断这个需求已经「完成」了？")
    report_lines.append("")
    report_lines.append("### 建议验收标准")
    report_lines.append("- [ ] 正向流程可走通")
    report_lines.append("- [ ] 异常场景有兜底处理")
    report_lines.append("- [ ] 各角色权限边界清晰")
    report_lines.append("")
    report_lines.append("请根据以上框架逐项与需求方确认。")
    return "\n".join(report_lines)


@tool
def generate_use_case_diagram(
    actors: str,
    use_cases: str,
    relations: str = "",
    title: str = "系统用例图"
) -> str:
    """
    生成 PlantUML 用例图代码。

    Args:
        actors: 角色列表，格式: "角色名1,角色名2"，如 "普通用户,管理员"
        use_cases: 用例列表，格式: "用例名1,用例名2"，如 "注册账号,发布内容,审核内容"
        relations: 关系描述，格式: "角色--用例,角色--用例"，如 "普通用户--注册账号,管理员--审核内容"
        title: 图表标题
    """
    actor_list = [a.strip() for a in actors.split(",") if a.strip()]
    uc_list = [u.strip() for u in use_cases.split(",") if u.strip()]

    lines = ["@startuml", f"title {title}", "", "left to right direction", ""]

    for actor in actor_list:
        safe_actor = actor.replace(" ", "_")
        lines.append(f"actor \"{actor}\" as {safe_actor}")

    lines.append("")

    for i, uc in enumerate(uc_list):
        safe_uc = f"UC{i+1}"
        lines.append(f"usecase \"{uc}\" as {safe_uc}")

    lines.append("")

    if relations:
        for rel in relations.split(","):
            rel = rel.strip()
            if "--" in rel:
                parts = rel.split("--")
                if len(parts) == 2:
                    src = parts[0].strip().replace(" ", "_")
                    tgt = parts[1].strip().replace(" ", "_")
                    lines.append(f"{src} --> {tgt}")
            elif "..>" in rel:
                parts = rel.split("..>")
                if len(parts) == 2:
                    src = parts[0].strip().replace(" ", "_")
                    tgt = parts[1].strip().replace(" ", "_")
                    lines.append(f"{src} ..> {tgt} : <<extend>>")

    lines.append("")
    lines.append("@enduml")
    return "\n".join(lines)


@tool
def generate_activity_diagram(
    steps: str,
    title: str = "业务流程图",
    decision_points: str = ""
) -> str:
    """
    生成 PlantUML 活动图（流程图）代码。

    Args:
        steps: 流程步骤，用逗号分隔，如 "用户登录,浏览商品,加入购物车,提交订单,支付"
        title: 图表标题
        decision_points: 判断节点描述，格式: "步骤名:条件1->分支1,条件2->分支2"
            如 "支付:成功->订单确认,失败->重新支付"
    """
    step_list = [s.strip() for s in steps.split(",") if s.strip()]
    decision_map = {}
    if decision_points:
        for dp in decision_points.split(";"):
            dp = dp.strip()
            if ":" in dp:
                node, branches_str = dp.split(":", 1)
                branches = {}
                for br in branches_str.split(","):
                    if "->" in br:
                        cond, target = br.split("->", 1)
                        branches[cond.strip()] = target.strip()
                decision_map[node.strip()] = branches

    lines = ["@startuml", f"title {title}", "", "start", ""]

    for step in step_list:
        if step in decision_map:
            lines.append(f":{step};")
            branches = decision_map[step]
            cond_items = list(branches.items())
            lines.append("switch ()")
            for i, (cond, target) in enumerate(cond_items):
                prefix = "case" if i == 0 else "case"
                lines.append(f"{prefix} ( {cond} )")
                lines.append(f"  :{target};")
            lines.append("endswitch")
        else:
            lines.append(f":{step};")
        lines.append("")

    lines.append("stop")
    lines.append("@enduml")
    return "\n".join(lines)


@tool
def generate_prd(
    title: str,
    background: str = "",
    actors: str = "",
    core_flow: str = "",
    acceptance_criteria: str = ""
) -> str:
    """
    生成 PRD（产品需求文档）概要。

    Args:
        title: 需求标题
        background: 需求背景和业务价值
        actors: 涉及角色，逗号分隔
        core_flow: 核心流程描述，逗号分隔
        acceptance_criteria: 验收标准，逗号分隔
    """
    lines = [f"# PRD: {title}", ""]

    if background:
        lines.append("## 1. 需求背景")
        lines.append(background)
        lines.append("")

    if actors:
        lines.append("## 2. 涉及角色")
        for a in actors.split(","):
            lines.append(f"- {a.strip()}")
        lines.append("")

    if core_flow:
        lines.append("## 3. 核心流程")
        for i, step in enumerate(core_flow.split(","), 1):
            lines.append(f"{i}. {step.strip()}")
        lines.append("")

    lines.append("## 4. 非功能性需求")
    lines.append("- 性能要求：待确认")
    lines.append("- 安全要求：待确认")
    lines.append("- 兼容性要求：待确认")
    lines.append("")

    lines.append("## 5. 边界与异常")
    lines.append("- 边界条件：待补充")
    lines.append("- 异常场景：待补充")
    lines.append("")

    if acceptance_criteria:
        lines.append("## 6. 验收标准")
        for ac in acceptance_criteria.split(","):
            lines.append(f"- [ ] {ac.strip()}")
        lines.append("")

    lines.append("---")
    lines.append("*本文档由 AI PM Agent 自动生成，请逐项确认*")
    return "\n".join(lines)


PM_TOOLS = [
    analyze_requirement,
    generate_use_case_diagram,
    generate_activity_diagram,
    generate_prd,
]
