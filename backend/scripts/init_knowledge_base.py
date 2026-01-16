"""
知识库初始化脚本
将政策文档、FAQ、购房指南导入 Chroma 向量数据库
"""
import os
import sys
import json
import hashlib
import asyncio
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.chroma import ChromaClient
from app.config.settings import get_settings
from app.utils.logger import setup_logging, get_logger

# 初始化日志
setup_logging(debug=True)
logger = get_logger("house_advisor.scripts.init_kb")

# 数据目录
DATA_DIR = Path(__file__).parent.parent / "data" / "knowledge"


def generate_doc_id(content: str, prefix: str = "") -> str:
    """生成文档ID"""
    hash_val = hashlib.md5(content.encode()).hexdigest()[:8]
    return f"{prefix}_{hash_val}" if prefix else hash_val


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    将长文本分块
    
    Args:
        text: 原始文本
        chunk_size: 每块大小（字符数）
        overlap: 重叠字符数
    
    Returns:
        文本块列表
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # 尝试在句子边界处分割
        if end < len(text):
            # 向后查找句子结束符
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


def load_markdown_file(file_path: Path) -> tuple[str, dict]:
    """
    加载 Markdown 文件
    
    Returns:
        (内容, 元数据)
    """
    content = file_path.read_text(encoding="utf-8")
    
    # 从文件名提取城市信息
    filename = file_path.stem.lower()
    city = None
    if "nanning" in filename or "南宁" in filename:
        city = "南宁"
    elif "liuzhou" in filename or "柳州" in filename:
        city = "柳州"
    
    metadata = {
        "source": file_path.name,
        "type": "markdown"
    }
    if city:
        metadata["city"] = city
    
    return content, metadata


def load_json_file(file_path: Path) -> list[dict]:
    """
    加载 JSON 文件
    
    Returns:
        数据列表
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and "items" in data:
        return data["items"]
    else:
        return [data]


async def init_policies(client: ChromaClient) -> int:
    """
    初始化政策知识库
    
    Returns:
        导入的文档数量
    """
    logger.info("正在初始化政策知识库...")
    
    policies_dir = DATA_DIR / "policies"
    if not policies_dir.exists():
        logger.warning(f"政策目录不存在: {policies_dir}")
        return 0
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in policies_dir.glob("*.md"):
        content, metadata = load_markdown_file(file_path)
        
        # 分块处理
        chunks = chunk_text(content, chunk_size=500)
        
        for i, chunk in enumerate(chunks):
            doc_id = generate_doc_id(chunk, f"policy_{file_path.stem}_{i}")
            documents.append(chunk)
            metadatas.append({**metadata, "chunk_index": i})
            ids.append(doc_id)
    
    if documents:
        client.add_documents(
            collection_name=ChromaClient.COLLECTION_POLICIES,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    logger.info(f"政策知识库初始化完成，共 {len(documents)} 个文档块")
    return len(documents)


async def init_faq(client: ChromaClient) -> int:
    """
    初始化 FAQ 知识库
    
    Returns:
        导入的文档数量
    """
    logger.info("正在初始化 FAQ 知识库...")
    
    faq_dir = DATA_DIR / "faq"
    if not faq_dir.exists():
        logger.warning(f"FAQ 目录不存在: {faq_dir}")
        return 0
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in faq_dir.glob("*.json"):
        items = load_json_file(file_path)
        
        for item in items:
            question = item.get("question", item.get("q", ""))
            answer = item.get("answer", item.get("a", ""))
            category = item.get("category", "通用")
            
            if not question or not answer:
                continue
            
            # 将问题和答案组合为文档
            doc_content = f"问题：{question}\n答案：{answer}"
            doc_id = generate_doc_id(doc_content, "faq")
            
            documents.append(doc_content)
            metadatas.append({
                "source": file_path.name,
                "type": "faq",
                "category": category,
                "question": question
            })
            ids.append(doc_id)
    
    if documents:
        client.add_documents(
            collection_name=ChromaClient.COLLECTION_FAQ,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    logger.info(f"FAQ 知识库初始化完成，共 {len(documents)} 个文档")
    return len(documents)


async def init_guides(client: ChromaClient) -> int:
    """
    初始化购房指南知识库
    
    Returns:
        导入的文档数量
    """
    logger.info("正在初始化购房指南知识库...")
    
    guides_dir = DATA_DIR / "guides"
    if not guides_dir.exists():
        logger.warning(f"指南目录不存在: {guides_dir}")
        return 0
    
    documents = []
    metadatas = []
    ids = []
    
    for file_path in guides_dir.glob("*.md"):
        content, metadata = load_markdown_file(file_path)
        
        # 分块处理
        chunks = chunk_text(content, chunk_size=500)
        
        for i, chunk in enumerate(chunks):
            doc_id = generate_doc_id(chunk, f"guide_{file_path.stem}_{i}")
            documents.append(chunk)
            metadatas.append({**metadata, "chunk_index": i, "type": "guide"})
            ids.append(doc_id)
    
    if documents:
        client.add_documents(
            collection_name=ChromaClient.COLLECTION_GUIDES,
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    
    logger.info(f"购房指南知识库初始化完成，共 {len(documents)} 个文档块")
    return len(documents)


async def main():
    """主函数"""
    logger.info("=" * 50)
    logger.info("开始初始化知识库")
    logger.info("=" * 50)
    
    # 获取配置
    settings = get_settings()
    
    # 解析 Chroma URL
    chroma_url = settings.CHROMA_URL
    if chroma_url.startswith("http://"):
        chroma_url = chroma_url[7:]
    elif chroma_url.startswith("https://"):
        chroma_url = chroma_url[8:]
    
    parts = chroma_url.split(":")
    host = parts[0]
    port = int(parts[1]) if len(parts) > 1 else 8001
    
    # 获取本地 embedding 模型路径
    embedding_model_path = getattr(settings, 'EMBEDDING_MODEL_PATH', None)
    logger.info(f"Embedding 模型路径: {embedding_model_path}")
    
    # 创建 Chroma 客户端（使用本地 BGE 模型）
    client = ChromaClient(
        host=host, 
        port=port,
        embedding_model_path=embedding_model_path
    )
    
    try:
        await client.connect()
        
        # 清空现有数据（可选）
        logger.info("清空现有 Collection...")
        for collection_name in [
            ChromaClient.COLLECTION_POLICIES,
            ChromaClient.COLLECTION_FAQ,
            ChromaClient.COLLECTION_GUIDES
        ]:
            try:
                client.delete_collection(collection_name)
            except Exception:
                pass
        
        # 初始化各知识库
        total = 0
        total += await init_policies(client)
        total += await init_faq(client)
        total += await init_guides(client)
        
        logger.info("=" * 50)
        logger.info(f"知识库初始化完成，共导入 {total} 个文档")
        logger.info("=" * 50)
        
        # 验证
        logger.info("验证 Collection 状态:")
        for name in [
            ChromaClient.COLLECTION_POLICIES,
            ChromaClient.COLLECTION_FAQ,
            ChromaClient.COLLECTION_GUIDES
        ]:
            count = client.count_documents(name)
            logger.info(f"  - {name}: {count} 个文档")
        
    except Exception as e:
        logger.error(f"初始化失败: {e}")
        raise
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
