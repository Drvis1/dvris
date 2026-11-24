from rag.milvus_store import get_milvus_vector_store

def get_rag_retriever(k=4):
    vector_db = get_milvus_vector_store()
    retriever = vector_db.as_retriever(search_kwargs={"k":k})
    return retriever