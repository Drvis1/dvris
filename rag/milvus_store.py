from langchain_milvus import Milvus
from pymilvus import MilvusClient
from langchain_community.embeddings import DashScopeEmbeddings
from config.settings import settings

def connection_args():
    return {
        "uri": settings.MILVUS_LITE_URI,
        "grpc_options": {
            "grpc.keepalive_time_ms": 300000,
            "grpc.keepalive_timeout_ms": 20000,
            "grpc.keepalive_permit_without_calls": False,
            "grpc.http2.max_pings_without_data": 2,
        },
    }


def get_embedding():
    return DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )

def get_milvus_client() -> MilvusClient:
    """Milvus Lite 本地文件模式"""
    client = MilvusClient(**connection_args())
    return client

def get_milvus_vector_store():
    embeddings = get_embedding()
    vector_db = Milvus(
        embeddings,
        collection_name=f"{settings.MILVUS_COLLECTION}_metadata_v2",
        enable_dynamic_field=True,
        connection_args=connection_args(),
        auto_id=True
    )
    return vector_db

def add_documents_to_milvus(docs):
    vector_db = get_milvus_vector_store()
    vector_db.add_documents(docs)
    return True