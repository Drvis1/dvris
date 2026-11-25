# Dvris

在项目根目录执行：

```powershell
python -m pip install -r requirements.txt
python -m uvicorn api.api_server:app --host 127.0.0.1 --port 8000
```

浏览器访问 http://127.0.0.1:8000 ，交互式接口文档位于 `/docs`。
请先按原项目配置 `.env` 中的模型、Milvus 和 SQLite 参数。
PDF 和 DOCX 解析分别需要 `pypdf`、`docx2txt`（已列入依赖）。

接口：

- `GET /api/health`：Web 服务存活检查，不检查模型或数据库连接。
- `POST /api/chat`：JSON `{ "session_id": "demo", "message": "你好" }`。
- `GET /api/sessions/{session_id}/messages`：读取历史。
- `DELETE /api/sessions/{session_id}/messages`：清空历史。
- `POST /api/upload`：multipart 表单字段 `file`，支持 PDF、DOCX、TXT、MD，最多 20 MB。

网页在当前浏览器保存会话 ID，刷新后恢复历史。Enter 发送，Shift+Enter 换行。
知识库沿用原项目的共享集合。当前版本用于本地单进程运行，请勿增加多个 worker；没有用户认证。
