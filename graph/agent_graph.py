from langgraph.graph import StateGraph, END
from typing import TypedDict
from langchain_core.messages import BaseMessage
from agents.tool_agent import build_tool_agent
from agents.rag_agent import build_rag_agent

# 状态定义
class GraphState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_type: str
    output: str

tool_agent = build_tool_agent()

def router(state: GraphState) -> str:
    """路由判断：判断用户问题交给哪个Agent
    包含文件、文档、资料、检索 -> rag_agent_node
    时间、天气、温度、计算 -> tool_agent_node
    """
    user_input = state["input"].lower()
    rag_keywords = ["文档", "文件", "pdf", "docx", "资料", "检索", "里面内容"]
    tool_keywords = ["几点", "时间", "天气", "温度", "计算", "等于"]
    if any(k in user_input for k in rag_keywords):
        return "rag_agent_node"
    elif any(k in user_input for k in tool_keywords):
        return "tool_agent_node"
    else:
        # 默认路由工具agent
        return "tool_agent_node"

def tool_agent_node(state: GraphState) -> GraphState:
    res = tool_agent.invoke({
        "input": state["input"],
        "chat_history": state["chat_history"]
    })
    state["output"] = res["output"]
    return state

def rag_agent_node(state: GraphState) -> GraphState:
    rag_agent = build_rag_agent()
    res = rag_agent.invoke({
        "question": state["input"],
        "chat_history": state["chat_history"]
    })
    state["output"] = res
    return state

def build_graph():
    workflow = StateGraph(GraphState)
    workflow.add_node("tool_agent_node", tool_agent_node)
    workflow.add_node("rag_agent_node", rag_agent_node)
    workflow.set_conditional_entry_point(router, {
        "tool_agent_node": "tool_agent_node",
        "rag_agent_node": "rag_agent_node"
    })
    workflow.add_edge("tool_agent_node", END)
    workflow.add_edge("rag_agent_node", END)
    graph = workflow.compile()
    return graph