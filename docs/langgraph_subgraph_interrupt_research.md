# LangGraph Subgraph + Interrupt + Resume 研究报告

## 研究目标

理解如何在 LangGraph 中实现：
1. Subgraph 内部的 interrupt
2. 父图如何 resume 到 subgraph
3. Checkpointer 的配置方式

## 核心发现

### 1. Checkpointer 配置 ✅

**结论：Subgraph 不需要自己的 checkpointer**

```python
# ✅ 正确的方式
# Subgraph - 不传 checkpointer
subgraph = subgraph_builder.compile()

# Parent graph - 只在父图传 checkpointer
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)
```

**原理**：LangGraph 会自动将父图的 checkpointer 传播到所有子图。

**来源**：Context7 文档 - "Add Persistence to Parent Graph with Subgraph"

### 2. Subgraph Interrupt 机制 ✅

**工作流程**：

```python
# Subgraph 定义
def subgraph_node_1(state: State):
    value = interrupt("Provide value:")  # interrupt 在 subgraph 内部
    return {"foo": state["foo"] + value}

subgraph_builder = StateGraph(State)
subgraph_builder.add_node(subgraph_node_1)
subgraph = subgraph_builder.compile()  # 无 checkpointer

# Parent graph
builder = StateGraph(State)
builder.add_node("node_1", subgraph)  # 直接将 subgraph 作为节点
graph = builder.compile(checkpointer=MemorySaver())

# 执行
config = {"configurable": {"thread_id": "1"}}
graph.invoke({"foo": ""}, config)  # 暂停在 subgraph 的 interrupt

# Resume
graph.invoke(Command(resume="bar"), config)  # ✅ 自动恢复到 subgraph 内部
```

**关键点**：
- Interrupt 发生在 subgraph 内部时，父图的 invoke 会暂停
- Resume 时直接调用父图，LangGraph 会自动将 resume 值传递到 subgraph 的 interrupt 点
- 不需要手动管理 subgraph 的状态恢复

**来源**：Context7 文档 - "View Interrupted Subgraph State"

### 3. 节点函数可以接收 config 参数 ✅

**发现**：节点函数可以声明 `config: RunnableConfig` 参数，LangGraph 会自动注入。

```python
from langchain_core.runnables import RunnableConfig

def node_with_config(state: State, config: RunnableConfig):
    print("Thread ID:", config["configurable"]["thread_id"])
    return {"results": f"Hello, {state['input']}!"}

builder.add_node("my_node", node_with_config)
```

**来源**：Context7 文档 - "Create and Add Nodes to a LangGraph StateGraph"

## 当前代码的问题分析

### 问题 1：手动调用 Subgraph 时未传递 config ❌

**当前代码**：
```python
async def enhance_node(state: StorybookState) -> dict:
    subgraph = get_enhance_subgraph()
    result = await subgraph.ainvoke({
        "messages": [HumanMessage(content=user_story)]
    })  # ❌ 没有传递 config
```

**问题**：
- 节点函数没有接收 `config` 参数
- 手动调用 `subgraph.ainvoke()` 时无法传递 config
- Subgraph 无法从 checkpointer 恢复状态
- Resume 时会失败

### 问题 2：Subgraph 不是直接作为节点

**文档示例**（直接将 subgraph 作为节点）：
```python
builder.add_node("node_1", subgraph)  # ✅ 直接添加
```

**当前代码**（在节点函数内部调用 subgraph）：
```python
async def enhance_node(state):
    subgraph = get_enhance_subgraph()
    result = await subgraph.ainvoke(...)  # ❌ 手动调用

builder.add_node("enhance", enhance_node)
```

**问题**：
- 需要在调用 subgraph 前后做输入/输出转换
- 无法直接将 subgraph 作为节点
- 但手动调用时需要传递 config

## 解决方案

### 方案 A：节点函数接收 config 参数（推荐）✅

```python
from langchain_core.runnables import RunnableConfig

async def enhance_node(state: StorybookState, config: RunnableConfig) -> dict:
    """
    Call enhance subgraph with config propagation.
    """
    logger.info("[NODE] enhance_node - invoking subgraph")

    try:
        # Build minimal input
        user_story = None
        for msg in state["messages"]:
            if hasattr(msg, "type") and msg.type == "human":
                user_story = msg.content
                break

        if not user_story:
            user_story = "Create a story"

        # Invoke subgraph with config ✅
        subgraph = get_enhance_subgraph()
        result = await subgraph.ainvoke({
            "messages": [HumanMessage(content=user_story)]
        }, config)  # ✅ 传递 config

        # Extract outputs
        interaction_data = extract_user_interaction_data(result["messages"])
        enhanced_story = interaction_data.get("enhanced_story") if interaction_data else None
        characters = interaction_data.get("characters", []) if interaction_data else []

        return {
            "messages": [AIMessage(content=f"Enhanced story with {len(characters)} characters")],
            "enhanced_story": enhanced_story,
            "characters": characters,
            "current_stage": "enhance",
        }

    except Exception as e:
        logger.error(f"[NODE] enhance_node failed: {e}")
        return {
            "messages": [AIMessage(content=f"Error: {e}")],
            "current_stage": "enhance",
        }
```

**优点**：
- 最小改动
- 保留输入/输出转换逻辑
- Config 正确传递到 subgraph
- Interrupt/Resume 可以正常工作

**需要修改的文件**：
- `backend/app/graphs/storybook_graph.py`
  - `enhance_node` 添加 `config` 参数
  - `portrait_node` 添加 `config` 参数
  - `story_node` 添加 `config` 参数

### 方案 B：直接使用 Subgraph 作为节点（不推荐）

```python
# 不做输入/输出转换，直接使用 subgraph
builder.add_node("enhance", get_enhance_subgraph())
```

**缺点**：
- 无法做输入转换（从 StorybookState 提取 user_story）
- 无法做输出转换（从 subgraph messages 提取 enhanced_story）
- 需要重新设计状态结构

## Resume 流程详解

### 完整流程

1. **初始调用**：
```python
graph.ainvoke({"messages": [HumanMessage("创作企鹅故事")]}, config)
```

2. **执行路径**：
```
orchestrator → enhance_node → enhance_subgraph → enhance_agent_node
```

3. **Enhance Agent 调用 user_interaction**：
```python
user_interaction(
    type="story_review",
    intention="self",
    prompt="企鹅住在南极还是动物园？"
)
```

4. **Interrupt 触发**：
```python
# 在 user_interaction 工具内部
return interrupt({
    "type": "story_review",
    "intention": "self",
    "prompt": "企鹅住在南极还是动物园？"
})
```

5. **图暂停**：
- `interrupt()` 抛出 `GraphInterrupt` 异常
- 异常从 subgraph → enhance_node → 父图
- 父图的执行引擎捕获异常
- 当前状态保存到 checkpointer
- `ainvoke` 返回（或抛出异常）

6. **用户回复**：
```python
graph.ainvoke(Command(resume="南极"), config)
```

7. **Resume 执行**：
- 父图从 checkpointer 加载状态
- 发现暂停在 `enhance_node`
- 重新执行 `enhance_node(state, config)`
- `enhance_node` 调用 `subgraph.ainvoke(..., config)`
- Subgraph 检测到 config 中有 resume 值
- Subgraph 从 checkpointer 恢复状态
- 找到 interrupt 点
- `interrupt()` 返回 "南极"（resume 值）
- Enhance agent 继续执行

### 关键点

1. **Config 传递是关键**：
   - 必须在调用 `subgraph.ainvoke()` 时传递 config
   - Config 包含 thread_id，用于从 checkpointer 恢复状态

2. **Resume 值的传递**：
   - `Command(resume="南极")` 中的值会通过 config 传递
   - Subgraph 内部的 `interrupt()` 会返回这个值

3. **节点函数会重新执行**：
   - Resume 时，`enhance_node` 会重新执行
   - 但 subgraph 会从 checkpointer 恢复，不会重新开始

## 查看 Subgraph 状态

```python
# 获取父图状态
parent_state = graph.get_state(config)

# 获取 subgraph 状态（只在 interrupt 时可用）
subgraph_state = graph.get_state(config, subgraphs=True).tasks[0].state
```

## 实现检查清单

- [ ] 修改 `enhance_node` 添加 `config: RunnableConfig` 参数
- [ ] 修改 `portrait_node` 添加 `config: RunnableConfig` 参数
- [ ] 修改 `story_node` 添加 `config: RunnableConfig` 参数
- [ ] 在所有 `subgraph.ainvoke()` 调用中传递 `config`
- [ ] 测试 interrupt 是否正常触发
- [ ] 测试 resume 是否正确恢复到 subgraph
- [ ] 验证 resume 值是否正确传递到 agent

## 参考文档

- Context7 - "Add Persistence to Parent Graph with Subgraph"
- Context7 - "View Interrupted Subgraph State"
- Context7 - "Create and Add Nodes to a LangGraph StateGraph"
- LangGraph 官方文档 - Interrupt 和 Resume API
