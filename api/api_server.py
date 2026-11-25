import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import RLock

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="Dvris API", version="1.0.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
lock = RLock()
logger = logging.getLogger(__name__)
MAX_UPLOAD = 20 * 1024 * 1024


class ChatRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_-]+$")
    message: str = Field(min_length=1, max_length=10000)


def backend():
    import main
    return main


def perform(operation):
    try:
        with lock:
            return operation(backend())
    except Exception:
        logger.exception("Dvris operation failed")
        raise HTTPException(500, "处理失败，请检查模型、数据库配置及服务日志。")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat")
def chat(body: ChatRequest):
    if not body.message.strip():
        raise HTTPException(422, "消息不能为空。")

    def run(core):
        from langchain_core.messages import HumanMessage, AIMessage
        history = core.memory_store.load_messages(body.session_id)
        result = core.graph.invoke({"input": body.message.strip(), "chat_history": history,
                                    "agent_type": "", "output": ""})
        answer = result["output"]
        core.memory_store.save_messages(body.session_id, history + [
            HumanMessage(content=body.message.strip()), AIMessage(content=answer)])
        return {"session_id": body.session_id, "answer": answer}
    return perform(run)


@app.get("/api/sessions/{session_id}/messages")
def history(session_id: str):
    return perform(lambda core: {"messages": [
        {"role": "user" if m.type == "human" else "assistant", "content": m.content}
        for m in core.memory_store.load_messages(session_id)]})


@app.delete("/api/sessions/{session_id}/messages")
def clear(session_id: str):
    def run(core):
        core.memory_store.clear_session(session_id)
        return {"message": "会话已清空"}
    return perform(run)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".pdf", ".docx", ".txt", ".md"}:
        await file.close()
        raise HTTPException(400, "仅支持 PDF、DOCX、TXT、MD 文件。")
    try:
        with TemporaryDirectory(prefix="dvris-") as folder:
            path = Path(folder) / ("document" + suffix)
            size = 0
            with path.open("wb") as destination:
                while chunk := await file.read(1024 * 1024):
                    size += len(chunk)
                    if size > MAX_UPLOAD:
                        raise HTTPException(413, "文件不能超过 20 MB。")
                    destination.write(chunk)
            if not size:
                raise HTTPException(400, "文件不能为空。")

            def ingest(core):
                docs = core.split_docs(core.load_file(str(path)))
                if not docs:
                    raise ValueError("No text found in document")
                for doc in docs:
                    doc.metadata["source"] = Path(file.filename.replace("\\", "/")).name
                core.add_documents_to_milvus(docs)
                return {"message": "文件已导入知识库，可以提问文档内容。", "chunks": len(docs)}
            return await run_in_threadpool(perform, ingest)
    finally:
        await file.close()