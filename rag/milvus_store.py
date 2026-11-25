from langchain_milvus import Milvus
from pymilvus import MilvusClient
from langchain_community.embeddings import DashScopeEmbeddings
from config.settings import settings

def get_embedding():
    return DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )

def get_milvus_client() -> MilvusClient:
    """Milvus Lite 本地文件模式"""
    client = MilvusClient(uri=settings.MILVUS_LITE_URI)
    return client

def get_milvus_vector_store():
    embeddings = get_embedding()
    vector_db = Milvus(
        embeddings,
        collection_name=settings.MILVUS_COLLECTION,
        # Milvus Lite 只需要uri参数
        connection_args={
            "uri": settings.MILVUS_LITE_URI
        },
        auto_id=True
    )
    return vector_db

def add_documents_to_milvus(docs):
    vector_db = get_milvus_vector_store()
    vector_db.add_documents(docs)
    return True