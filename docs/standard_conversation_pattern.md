# LangGraph 标准对话模式（基于文档）

## 核心发现

从 Context7 文档找到的标准模式：

### 模式：Agent 内部循环 + Interrupt

```python
@entrypoint(checkpointer)
def workflow(messages):
    call_active_agent = call_travel_advisor
    while True:
        # Agent 执行
        agent_messages = call_active_agent(messages).result()
        ai_msg = get_last_ai_msg(agent_messages)

        # 如果没有工具调用 → 说明 agent 想和用户对话
        if not ai_msg.tool_calls:
            # 使用 interrupt 等待用户输入
            user_input = interrupt(value="Ready for user input.")
            messages = messages + [{"role": "user", "content": user_input}]
            continue  # 继续循环，回到同一个 agent

        # 如果有工具调用 → 处理工具调用
        messages = messages + agent_messages
        call_active_agent = get_next_agent(messages)

    return entrypoint.final(value=agent_messages[-1], save=messages)
```

## 关键点

1. **Agent 在内部循环中运行**（`while True`）
2. **检查 AI 消息是否有工具调用**：
   - 没有工具调用 → Agent 想和用户对话 → **使用 interrupt**
   - 有工具调用 → 处理工具，可能切换 agent
3. **Interrupt 后 continue** → 回到循环开始，继续同一个 agent

## 答案

**你的问题**："if graph outputs in a subgraph to user, either it uses hitl to interrupt, but if it outputs, it won't get back right?"

**答案**：是的！

- 如果 agent 输出消息给用户，**必须使用 interrupt**
- 否则图会结束，无法回到同一个 agent
- 标准做法：检查 `ai_msg.tool_calls`，如果为空 → 使用 interrupt

## 应用到我们的代码

### Subgraph 内部循环

```python
def build_enhance_subgraph():
    """Enhance subgraph with internal loop for multi-turn conversation."""

    async def enhance_agent_node(state: EnhanceState) -> dict:
        """Agent node that loops until task is complete."""
        agent = AgentCache.get_agent("enhance")
        result = await agent.ainvoke({"messages": state["messages"]})

        # 检查最后一条消息
        messages = result["messages"]
        if messages:
            last_msg = messages[-1]
            if hasattr(last_msg, "type") and last_msg.type == "ai":
                has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
                if not has_tool_calls:
                    # 没有工具调用 = agent 想和用户对话
                    # 使用 interrupt 等待用户输入（统一的 HITL 模式）
                    user_input = interrupt({
                        "type": "text",
                        "intention": "self",
                        "value": last_msg.content  # 使用模型的实际消息内容
                    })
                    # 添加用户消息到历史
                    return {
                        "messages": messages + [HumanMessage(content=user_input)]
                    }

        # 有工具调用 → 返回消息
        return {"messages": messages}

    builder = StateGraph(EnhanceState)
    builder.add_node("agent", enhance_agent_node)
    builder.add_edge(START, "agent")

    # 条件边：检查是否完成
    builder.add_conditional_edges(
        "agent",
        route_enhance_subgraph,
        {
            "agent": "agent",  # 继续循环
            "__end__": END,     # 完成
        }
    )

    return builder.compile()
```

### 路由逻辑

```python
def route_enhance_subgraph(state: EnhanceState) -> Literal["agent", "__end__"]:
    """
    路由逻辑：
    1. 如果调用了 user_interaction(intention="next") 且批准 → 退出
    2. 如果调用了 escalate → 退出
    3. 否则 → 继续在 agent（包括 interrupt 后的情况）
    """
    messages = state["messages"]

    # 检查 escalate
    if get_tool_call(messages, "escalate"):
        return "__end__"

    # 检查 user_interaction(intention="next")
    interaction = get_tool_call(messages, "user_interaction")
    if interaction:
        args = interaction.get("args", {})
        if args.get("intention") == "next":
            response = get_tool_result(messages, "user_interaction")
            if response == "APPROVED":
                return "__end__"

    # 默认：继续在 agent
    return "agent"
```

## 流程示例

```
# 第 1 轮
用户: "创作企鹅故事"
  ↓ orchestrator → enhance_node → enhance_subgraph
  ↓ enhance_agent: "企鹅住在南极还是动物园？"（无工具调用）
  ↓ enhance_agent_node 检测到无工具调用
  ↓ 调用 interrupt(value="Agent is waiting for user input")
  ↓ 图暂停

# 第 2 轮
用户: "南极"
  ↓ graph.invoke(Command(resume="南极"), config)
  ↓ interrupt() 返回 "南极"
  ↓ enhance_agent_node 添加 HumanMessage("南极") 到消息历史
  ↓ route_enhance_subgraph 返回 "agent"（继续循环）
  ↓ enhance_agent_node 再次调用 agent
  ↓ enhance_agent: "企鹅叫什么名字？"（无工具调用）
  ↓ 再次 interrupt
  ↓ 图暂停

# 第 3 轮
用户: "叫 Pingu"
  ↓ graph.invoke(Command(resume="叫 Pingu"), config)
  ↓ interrupt() 返回 "叫 Pingu"
  ↓ enhance_agent 继续工作
  ↓ enhance_agent 完成故事增强
  ↓ 调用 user_interaction(intention="next", data={...})
  ↓ interrupt() 触发（审批）
  ↓ 图暂停

# 第 4 轮
用户: "APPROVED"
  ↓ graph.invoke(Command(resume="APPROVED"), config)
  ↓ user_interaction 返回 "APPROVED"
  ↓ route_enhance_subgraph 检测到 intention="next" + "APPROVED"
  ↓ 返回 "__end__"
  ↓ 退出 subgraph
  ↓ enhance_node 返回结果
  ↓ orchestrator 路由到 portrait
```

## 关键修改

### 1. Agent Node 检查工具调用

```python
async def enhance_agent_node(state: EnhanceState) -> dict:
    agent = AgentCache.get_agent("enhance")
    result = await agent.ainvoke({"messages": state["messages"]})

    messages = result["messages"]
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
            if not has_tool_calls:
                # 没有工具调用 = agent 想和用户对话
                # 使用 interrupt 等待用户输入（统一的 HITL 模式）
                user_input = interrupt({
                    "type": "text",
                    "intention": "self",
                    "value": last_msg.content  # 使用模型的实际消息内容
                })
                return {
                    "messages": messages + [HumanMessage(content=user_input)]
                }

    return {"messages": messages}
```

### 2. 路由逻辑简化

```python
def route_enhance_subgraph(state: EnhanceState) -> Literal["agent", "__end__"]:
    messages = state["messages"]

    # 只检查退出条件
    if get_tool_call(messages, "escalate"):
        return "__end__"

    interaction = get_tool_call(messages, "user_interaction")
    if interaction and interaction["args"].get("intention") == "next":
        if get_tool_result(messages, "user_interaction") == "APPROVED":
            return "__end__"

    # 默认：继续
    return "agent"
```

### 3. Agent Prompt 更新

```python
prompt = """你是故事增强专家。

工作流程：
1. 询问用户故事细节（直接生成消息，不调用工具）
2. 收集足够信息后，增强故事
3. 完成后，调用 user_interaction(intention="next") 请求审批

**重要**：
- 如果想问用户问题 → 直接生成 AI 消息，不调用工具
- 系统会自动 interrupt 并等待用户回复
- 用户回复后，你会继续执行

- 如果完成工作需要审批 → 调用 user_interaction(intention="next")
"""
```

## 总结

1. **所有与用户的对话都使用 interrupt**
2. **Agent node 检查是否有工具调用**：
   - 无工具调用 → interrupt → 等待用户 → 继续循环
   - 有工具调用 → 处理工具 → 检查是否退出
3. **不需要复杂的 orchestrator 路由逻辑**
4. **Subgraph 内部循环处理所有对话**
