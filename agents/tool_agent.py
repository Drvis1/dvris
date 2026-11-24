from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from tools.calculator_tool import calculator
from tools.time_tool import get_beijing_time
from tools.weather_tool import get_weather
from config.settings import settings

def build_tool_agent():
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.BASE_URL,
        temperature=0
    )
    tools = [calculator, get_beijing_time, get_weather]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是工具助手，根据用户问题调用工具，只使用提供的工具。"),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ])
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)
    return agent_executor