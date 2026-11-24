from langchain_community.vectorstores.milvus import Milvus
from pymilvus import connections, utility, Collection, FieldSchema, DataType
from langchain_community.embeddings import DashScopeEmbeddings
from config.settings import settings

def get_embedding():
    return DashScopeEmbeddings(
        model=settings.EMBEDDING_MODEL,
        dashscope_api_key=settings.DASHSCOPE_API_KEY
    )

def connect_milvus():
    connections.connect(
        host=settings.MILVUS_HOST,
        port=settings.MILVUS_PORT
    )

def get_milvus_vector_store():
    connect_milvus()
    embeddings = get_embedding()
    vector_db = Milvus(
        embeddings,
        collection_name=settings.MILVUS_COLLECTION,
        connection_args={
            "host": settings.MILVUS_HOST,
            "port": settings.MILVUS_PORT
        },
        auto_id=True
    )
    return vector_db

def add_documents_to_milvus(docs):
    vector_db = get_milvus_vector_store()
    vector_db.add_documents(docs)
    return True