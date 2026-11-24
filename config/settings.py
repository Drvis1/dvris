from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DASHSCOPE_API_KEY: str
    LLM_MODEL: str
    EMBEDDING_MODEL: str
    BASE_URL: str

    MILVUS_HOST: str
    MILVUS_PORT: int
    MILVUS_COLLECTION: str

    MEMORY_DB_PATH: str

    HEFENG_API_KEY: str

settings = Settings()
# 创建memory文件夹
os.makedirs(os.path.dirname(settings.MEMORY_DB_PATH), exist_ok=True)