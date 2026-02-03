# Context Isolation + 对话模式设计方案

## 问题 1：Context Isolation（上下文隔离）

### 当前问题
所有消息都在 `StorybookState.messages` 中累积，每个 subgraph 都能看到所有历史消息，导致：
- Agent 上下文过长，影响性能和成本
- Agent 可能被无关消息干扰
- 难以控制每个 agent 的专注领域

### 解决方案：使用不同的 State Schema

#### 方案 A：完全隔离的 State（推荐）

```python
# Parent State - 只保存输出和路由信息
class StorybookState(TypedDict):
    # 不保存详细的对话消息！
    routing_info: Optional[str]  # 简单的路由信息

    # 只保存输出
    enhanced_story: Optional[str]
    characters: list[dict]
    pages: list[dict]
    storybook_id: Optional[str]
    current_stage: Optional[str]

# Subgraph Private State - 完全独立的消息历史
class EnhanceState(TypedDict):
    messages: Annotated[list, add_messages]  # 只属于 enhance agent 的消息

class PortraitState(TypedDict):
    messages: Annotated[list, add_messages]  # 只属于 portrait agent 的消息

class StoryState(TypedDict):
    messages: Annotated[list, add_messages]  # 只属于 story agent 的消息
```

#### 节点实现 - 输入/输出转换

```python
async def enhance_node(state: StorybookState, config: RunnableConfig) -> dict:
    """
    Transform parent state → subgraph input
    Execute subgraph with isolated context
    Transform subgraph output → parent state
    """

    # 1. 构建 subgraph 的输入（只传递必要信息）
    subgraph_input = {
        "messages": [
            SystemMessage(content="你是故事增强专家"),
            HumanMessage(content=state.get("routing_info", "创作故事"))
        ]
    }

    # 2. 调用 subgraph（完全隔离的上下文）
    subgraph = get_enhance_subgraph()
    result = await subgraph.ainvoke(subgraph_input, config)

    # 3. 从 subgraph 的私有消息中提取输出
    enhanced_story = extract_story_from_messages(result["messages"])
    characters = extract_characters_from_messages(result["messages"])

    # 4. 返回到 parent state（不包含详细消息）
    return {
        "enhanced_story": enhanced_story,
        "characters": characters,
        "current_stage": "enhance"
    }
```

#### 优点
- ✅ 每个 subgraph 有完全独立的消息历史
- ✅ Parent state 保持简洁，只有输出数据
- ✅ Agent 上下文专注，不被无关消息干扰
- ✅ 更好的性能和成本控制

#### 方案 B：部分共享的 State

```python
class StorybookState(TypedDict):
    # 共享的核心消息（用户的主要请求）
    user_request: Optional[str]

    # 每个阶段的私有消息
    enhance_messages: Annotated[list, add_messages]
    portrait_messages: Annotated[list, add_messages]
    story_messages: Annotated[list, add_messages]

    # 输出
    enhanced_story: Optional[str]
    characters: list[dict]
    pages: list[dict]
```

这种方式允许在 parent state 中保存每个阶段的消息，但仍然隔离。

---

## 问题 2：两种对话模式

### 场景区分

#### 场景 A：Interrupt（审批模式）
**用途**：展示完成的工作，等待用户批准
```
enhance agent: "我完成了故事增强，请审阅"
  ↓ user_interaction(intention="next", data={...})
  ↓ interrupt() 触发
  ↓ 图暂停
用户: "APPROVED" 或 "修改..."
  ↓ Command(resume=...)
  ↓ 如果 APPROVED → 退出 subgraph
  ↓ 如果有反馈 → 继续在 agent
```

#### 场景 B：普通对话（多轮对话模式）
**用途**：Agent 问问题，收集信息，继续工作
```
enhance agent: "企鹅住在南极还是动物园？"
  ↓ 生成 AI 消息
  ↓ 图正常结束（不 interrupt）
  ↓ 前端显示消息
用户: "南极"
  ↓ 新的 graph.invoke()
  ↓ 从 checkpointer 恢复
  ↓ 路由回到 enhance agent
  ↓ agent 继续工作
```

### 关键问题：如何在多轮对话中保持在同一个 Stage？

#### 解决方案：使用 State + Orchestrator 智能路由

```python
class StorybookState(TypedDict):
    # 当前活跃的阶段
    active_stage: Optional[Literal["enhance", "portrait", "story"]]

    # 阶段是否完成
    stage_completed: bool

    # 其他字段...
    enhanced_story: Optional[str]
    characters: list[dict]
    pages: list[dict]

async def orchestrator_node(state: StorybookState) -> Command:
    """
    智能路由：
    1. 如果有 active_stage 且未完成 → 继续该阶段
    2. 如果阶段完成 → 进入下一阶段
    3. 如果没有 active_stage → 判断用户意图
    """

    # 检查是否有活跃的阶段
    if state.get("active_stage") and not state.get("stage_completed"):
        logger.info(f"[ORCHESTRATOR] Continuing active stage: {state['active_stage']}")
        return Command(goto=state["active_stage"])

    # 检查是否需要进入下一阶段
    if state.get("stage_completed"):
        current = state.get("active_stage")
        next_stage = NEXT_STAGE.get(current)
        if next_stage:
            logger.info(f"[ORCHESTRATOR] Stage {current} completed, moving to {next_stage}")
            return Command(
                goto=next_stage,
                update={"active_stage": next_stage, "stage_completed": False}
            )

    # 判断用户意图（新任务）
    model = get_gemini_model()
    decision = await model.with_structured_output(RouteDecision).ainvoke([
        SystemMessage(content="判断用户意图..."),
        *get_recent_messages(state)  # 只传递最近的消息
    ])

    if decision.intent == "chat":
        return Command(goto=END, update={"messages": [response]})
    else:
        target_stage = decision.next_stage or "enhance"
        return Command(
            goto=target_stage,
            update={"active_stage": target_stage, "stage_completed": False}
        )
```

#### Enhance Agent 的实现

```python
def create_enhance_agent():
    prompt = """你是故事增强专家。

工作流程：
1. 如果用户刚开始，询问故事细节
2. 收集足够信息后，增强故事
3. 完成后，调用 user_interaction(intention="next") 请求审批

**两种对话方式**：

A. 普通问题（收集信息）：
   - 直接生成 AI 消息问问题
   - 不调用任何工具
   - 图会正常结束，等待用户回复
   - 用户回复后，orchestrator 会路由回来

B. 审批（完成工作）：
   - 调用 user_interaction(intention="next", data={...})
   - 触发 interrupt，等待批准
   - 如果批准 → 退出阶段
   - 如果有反馈 → 继续修改

示例：
```
# 普通问题
AI: "企鹅住在南极还是动物园？"  # 直接生成消息，不调用工具

# 审批
user_interaction(
    type="story_review",
    intention="next",
    prompt="请审阅增强后的故事",
    data={"enhanced_story": "...", "characters": [...]}
)
```
"""

    return create_react_agent(
        model=get_gemini_model(),
        tools=ENHANCE_TOOLS,  # 只包含 user_interaction, escalate
        prompt=prompt
    )
```

#### Subgraph 路由逻辑

```python
def route_enhance_subgraph(state: EnhanceState) -> Literal["agent", "__end__"]:
    """
    路由逻辑：
    1. 如果调用了 user_interaction(intention="next") 且批准 → 退出
    2. 如果调用了 escalate → 退出
    3. 如果 agent 生成了普通消息（没有工具调用）→ 退出（等待用户回复）
    4. 否则 → 继续在 agent
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
                return "__end__"  # 批准，退出阶段
            else:
                return "agent"  # 有反馈，继续修改

    # 检查是否是普通消息（agent 问问题）
    if messages:
        last_msg = messages[-1]
        if hasattr(last_msg, "type") and last_msg.type == "ai":
            has_tool_calls = hasattr(last_msg, "tool_calls") and last_msg.tool_calls
            if not has_tool_calls:
                # Agent 生成了普通消息，退出 subgraph
                # 图会正常结束，等待用户回复
                logger.info("[SUBGRAPH] Agent asked question, exiting to wait for user")
                return "__end__"

    # 默认：继续工作
    return "agent"
```

#### Enhance Node 的状态管理

```python
async def enhance_node(state: StorybookState, config: RunnableConfig) -> dict:
    """
    调用 enhance subgraph，管理阶段状态
    """
    logger.info("[NODE] enhance_node")

    try:
        # 构建 subgraph 输入
        subgraph_input = build_enhance_input(state)

        # 调用 subgraph
        subgraph = get_enhance_subgraph()
        result = await subgraph.ainvoke(subgraph_input, config)

        # 检查是否完成
        interaction = get_tool_call(result["messages"], "user_interaction")
        stage_completed = False

        if interaction:
            args = interaction.get("args", {})
            if args.get("intention") == "next":
                response = get_tool_result(result["messages"], "user_interaction")
                if response == "APPROVED":
                    stage_completed = True

        # 提取输出
        enhanced_story = extract_story_from_messages(result["messages"])
        characters = extract_characters_from_messages(result["messages"])

        return {
            "enhanced_story": enhanced_story,
            "characters": characters,
            "active_stage": "enhance",
            "stage_completed": stage_completed,
        }

    except Exception as e:
        logger.error(f"[NODE] enhance_node failed: {e}")
        return {
            "active_stage": "enhance",
            "stage_completed": False,
        }
```

---

## 完整流程示例

### 场景：多轮对话 + 审批

```
# 第 1 轮：用户发起请求
用户: "创作企鹅故事"
  ↓ graph.invoke({"routing_info": "创作企鹅故事"}, config)
  ↓ orchestrator → enhance_node → enhance_subgraph → enhance_agent
  ↓ enhance_agent: "企鹅住在南极还是动物园？"（普通消息，无工具调用）
  ↓ route_enhance_subgraph 检测到普通消息 → 返回 "__end__"
  ↓ enhance_node 返回 {"active_stage": "enhance", "stage_completed": False}
  ↓ 图正常结束

# 第 2 轮：用户回复
用户: "南极"
  ↓ graph.invoke({"routing_info": "南极"}, config)
  ↓ orchestrator 检查 active_stage="enhance", stage_completed=False
  ↓ 路由到 enhance_node
  ↓ enhance_subgraph 从 checkpointer 恢复（包含之前的对话）
  ↓ enhance_agent 收到 "南极"，继续工作
  ↓ enhance_agent: "企鹅叫什么名字？"（又是普通消息）
  ↓ 图再次正常结束

# 第 3 轮：用户回复
用户: "叫 Pingu"
  ↓ graph.invoke({"routing_info": "叫 Pingu"}, config)
  ↓ orchestrator → enhance_node → enhance_subgraph
  ↓ enhance_agent 收到 "叫 Pingu"，完成故事增强
  ↓ enhance_agent 调用 user_interaction(intention="next", data={...})
  ↓ interrupt() 触发
  ↓ 图暂停

# 第 4 轮：用户审批
用户: "APPROVED"
  ↓ graph.invoke(Command(resume="APPROVED"), config)
  ↓ interrupt() 返回 "APPROVED"
  ↓ route_enhance_subgraph 检测到 intention="next" + "APPROVED" → 返回 "__end__"
  ↓ enhance_node 返回 {"stage_completed": True}
  ↓ orchestrator 检测到 stage_completed=True
  ↓ 路由到 portrait_node
```

---

## 实现要点

### 1. Context Isolation
- ✅ 使用不同的 State Schema
- ✅ 在节点中做输入/输出转换
- ✅ Subgraph 有完全独立的消息历史

### 2. 两种对话模式
- ✅ 普通对话：Agent 生成消息，图正常结束，orchestrator 路由回来
- ✅ 审批：使用 interrupt()，等待 Command(resume=...)

### 3. 状态管理
- ✅ `active_stage`：当前活跃的阶段
- ✅ `stage_completed`：阶段是否完成
- ✅ Orchestrator 根据这些字段智能路由

### 4. Checkpointer
- ✅ 只在父图设置 checkpointer
- ✅ Subgraph 自动继承
- ✅ 每次 invoke 都传递相同的 config（thread_id）

---

## 需要修改的文件

1. **backend/app/graphs/storybook_graph.py**
   - 修改 `StorybookState`：添加 `active_stage`, `stage_completed`
   - 修改 `orchestrator_node`：添加智能路由逻辑
   - 修改 `enhance_node`, `portrait_node`, `story_node`：添加 `config` 参数，管理阶段状态
   - 修改 `route_enhance_subgraph` 等：处理普通消息的退出

2. **backend/app/agents/storybook_agents.py**
   - 更新 agent prompt：说明两种对话方式
   - 强调普通问题不需要调用工具

3. **backend/app/tools/hitl_tools.py**
   - 保持不变（已经支持 intention="next"）

---

## 测试场景

1. **多轮对话**：Agent 问多个问题，用户逐个回答
2. **审批**：Agent 完成工作，请求审批
3. **反馈修改**：用户不批准，给出反馈，agent 修改后再次请求审批
4. **跨阶段**：完成 enhance → portrait → story
5. **Context Isolation**：验证每个 agent 只看到自己的消息
