from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_core.documents import Document
import os

def load_file(file_path: str) -> list[Document]:
    """
    加载多种文件：pdf,docx,txt,md
    :param file_path: 文件路径
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext in [".docx"]:
        loader = Docx2txtLoader(file_path)
    elif ext in [".txt", ".md"]:
        loader = TextLoader(file_path, encoding="utf-8")
    else:
        raise ValueError("不支持该文件类型")
    docs = loader.load()
    return docs

def split_docs(docs: list[Document], chunk_size=512, chunk_overlap=50):
    """
    文档切割
    :param docs: 用户提供的文档
    :param chunk_size: 切块大小
    :param chunk_overlap: 切块重叠数
    :return:
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)