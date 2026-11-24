from graph.agent_graph import build_graph
from memory.persistent_memory import memory_store
from langchain_core.messages import HumanMessage, AIMessage
from rag.file_loader import load_file, split_docs
from rag.milvus_store import add_documents_to_milvus

graph = build_graph()

def run_dvris(session_id: str, user_query: str):
    try:
        # 加载该会话历史
        chat_history = memory_store.load_messages(session_id)
        state = {
            "input": user_query,
            "chat_history": chat_history,
            "agent_type": "",
            "output": ""
        }
        result = graph.invoke(state)
        resp_text = result["output"]
        # 追加对话历史
        chat_history.append(HumanMessage(content=user_query))
        chat_history.append(AIMessage(content=resp_text))
        memory_store.save_messages(session_id, chat_history)
        return resp_text
    except Exception:
        return "抱歉，我无法回答当前问题"

def upload_file_to_kb(file_path: str):
    """上传文件到RAG知识库，存入Milvus"""
    try:
        raw_docs = load_file(file_path)
        chunked_docs = split_docs(raw_docs)
        add_documents_to_milvus(chunked_docs)
        return "文件已成功解析并存入向量数据库，可以提问文档内容"
    except Exception:
        return "抱歉，我无法回答当前问题"

if __name__ == "__main__":
    print("==== Dvris智能系统 ====")
    sid = "session_001"
    while True:
        user_input = input("\n请输入指令（输入upload:xxx 上传文件；exit退出）：")
        if user_input == "exit":
            print("系统退出，对话记录已保存")
            break
        if user_input.startswith("upload:"):
            fp = user_input.replace("upload:", "").strip()
            msg = upload_file_to_kb(fp)
            print(f"系统：{msg}")
        else:
            ans = run_dvris(sid, user_input)
            print(f"系统：{ans}")