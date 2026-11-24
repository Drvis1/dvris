from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from rag.retriever import get_rag_retriever
from config.settings import settings

def build_rag_agent():
    llm = ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.BASE_URL,
        temperature=0
    )
    retriever = get_rag_retriever()
    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是文档问答助手，根据检索到的文档内容回答用户问题。只使用文档内信息回答，不知道就如实说明。上下文：{context}"),
        ("placeholder", "{chat_history}"),
        ("human", "{question}"),
    ])
    rag_chain = (
        {"context": retriever | (lambda docs: "\n".join([d.page_content for d in docs])),
         "question": RunnablePassthrough(),
         "chat_history": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    return rag_chain