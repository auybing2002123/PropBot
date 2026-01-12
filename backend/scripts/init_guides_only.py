# -*- coding: utf-8 -*-
"""只初始化 guides 知识库"""
import sys
import hashlib
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.chroma import ChromaClient
from app.config.settings import get_settings
from app.utils.logger import setup_logging, get_logger

setup_logging(debug=True)
logger = get_logger("init_guides")

DATA_DIR = Path(__file__).parent.parent / "data" / "knowledge"


def generate_doc_id(content: str, prefix: str = "") -> str:
    hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_val}" if prefix else hash_val


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end < len(text):
            for sep in ["。", "！", "？", "\n\n", "\n"]:
                pos = text.rfind(sep, start, end)
                if pos > start:
                    end = pos + len(sep)
                    break
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start = end - overlap
    return chunks


def main():
    settings = get_settings()
    chroma_url = settings.CHROMA_URL
    if chroma_url.startswith("http://"):
        chroma_url = chroma_url[7:]
    parts = chroma_url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8001
    
    embedding_model_path = getattr(settings, 'EMBEDDING_MODEL_PATH', None)
    logger.info(f"Embedding 模型路径: {embedding_model_path}")
    
    client = ChromaClient(host=host, port=port, embedding_model_path=embedding_model_path)
    
    guides_dir = DATA_DIR / "guides"
    documents = []
    metadatas = []
    ids = []
    
    for file_path in guides_dir.glob("*.md"):
        logger.info(f"处理文件: {file_path.name}")
        content = file_path.read_text(encoding="utf-8")
        chunks = chunk_text(content, chunk_size=500)
        logger.info(f"  分块数: {len(chunks)}")
        
        for i, chunk in enumerate(chunks):
            doc_id = generate_doc_id(chunk, f"guide_{file_path.stem}_{i}")
            documents.append(chunk)
            metadatas.append({"source": file_path.name, "chunk_index": i, "type": "guide"})
            ids.append(doc_id)
    
    logger.info(f"总文档数: {len(documents)}")
    
    if documents:
        client.add_documents(
            collection_name=ChromaClient.COLLECTION_GUIDES,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info("guides 初始化完成")
    
    # 验证
    count = client.count_documents(ChromaClient.COLLECTION_GUIDES)
    logger.info(f"guides collection 文档数: {count}")


if __name__ == "__main__":
    main()
