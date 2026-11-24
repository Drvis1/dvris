from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from main import run_dvris, upload_file_to_kb

app = FastAPI(title="Dvris智能系统")

# 挂载静态文件夹，访问前端页面
app.mount("/static", StaticFiles(directory="static"), name="static")

# 对话接口
@app.post("/chat")
async def chat(session_id: str = Form(...), query: str = Form(...)):
    try:
        resp = run_dvris(session_id, query)
        return {"code": 0, "msg": "success", "data": {"answer": resp}}
    except Exception:
        return {"code": -1, "msg": "抱歉，我无法回答当前问题", "data": None}

# 文件上传接口：上传文件存入Milvus Lite知识库
@app.post("/upload")
async def upload_kb_file(session_id: str = Form(...), file: UploadFile = File(...)):
    try:
        # 临时保存上传文件
        temp_dir = "./tmp_upload"
        os.makedirs(temp_dir, exist_ok=True)
        save_path = os.path.join(temp_dir, file.filename)
        with open(save_path, "wb") as f:
            f.write(await file.read())
        msg = upload_file_to_kb(save_path)
        # 删除临时文件
        os.remove(save_path)
        return {"code":0, "msg":msg, "data":None}
    except Exception:
        return {"code": -1, "msg": "抱歉，我无法回答当前问题", "data": None}

# 首页路由，直接返回web页面
@app.get("/")
async def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.api_server:app", host="127.0.0.1", port=8000, reload=True)