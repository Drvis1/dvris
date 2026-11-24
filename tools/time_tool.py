from langchain_core.tools import tool
from datetime import datetime
import pytz

@tool
def get_beijing_time() -> str:
    """
    获取当前北京时间，返回年月日时分秒
    """
    tz = pytz.timezone("Asia/Shanghai")
    now = datetime.now(tz)
    return f"当前北京时间：{now.strftime('%Y-%m-%d %H:%M:%S')}"