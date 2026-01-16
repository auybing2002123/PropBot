"""
Chroma 向量数据库客户端
用于知识库的语义检索，使用本地 BGE 模型生成向量
"""
from typing import Optional
from pathlib import Path
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions

from app.utils.logger import get_logger

logger = get_logger("house_advisor.db.chroma")


class ChromaClient:
    """Chroma 向量数据库客户端"""
    
    # Collection 名称常量
    COLLECTION_POLICIES = "policies"  # 限购限贷政策
    COLLECTION_FAQ = "faq"            # 常见问题
    COLLECTION_GUIDES = "guides"      # 购房指南
    
    def __init__(
        self, 
        host: str = "localhost", 
        port: int = 8001,
        embedding_model_path: Optional[str] = None
    ):
        """
        初始化 Chroma 客户端
        
        Args:
            host: Chroma 服务地址
            port: Chroma 服务端口
            embedding_model_path: 本地 embedding 模型路径（如 ~/models/bge-base-zh-v1.5）
        """
        self._host = host
        self._port = port
        self._client: Optional[chromadb.HttpClient] = None
        self._collections: dict = {}
        self._embedding_fn = None
        
        # 设置本地 embedding 模型
        if embedding_model_path:
            model_path = Path(embedding_model_path).expanduser()
            if model_path.exists():
                logger.info(f"使用本地 embedding 模型: {model_path}")
                self._embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=str(model_path)
                )
            else:
                logger.warning(f"本地模型路径不存在: {model_path}，将使用 Chroma 默认模型")
        
        # 如果没有指定本地模型，使用默认的 sentence-transformers 模型
        if self._embedding_fn is None:
            logger.info("使用默认 embedding 模型")
            self._embedding_fn = embedding_functions.DefaultEmbeddingFunction()
    
    async def connect(self) -> None:
        """连接 Chroma 服务"""
        try:
            self._client = chromadb.HttpClient(
                host=self._host,
                port=self._port,
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            # 测试连接
            self._client.heartbeat()
            logger.info(f"Chroma 连接成功: {self._host}:{self._port}")
        except Exception as e:
            logger.error(f"Chroma 连接失败: {e}")
            raise
    
    async def disconnect(self) -> None:
        """断开连接"""
        self._client = None
        self._collections = {}
        logger.info("Chroma 连接已关闭")
    
    async def check_health(self) -> bool:
        """检查连接状态"""
        try:
            if self._client:
                self._client.heartbeat()
                return True
            return False
        except Exception:
            return False
    
    def get_or_create_collection(
        self,
        name: str,
        metadata: Optional[dict] = None
    ):
        """
        获取或创建 Collection
        
        Args:
            name: Collection 名称
            metadata: Collection 元数据
        
        Returns:
            Collection 对象
        """
        if not self._client:
            raise RuntimeError("Chroma 客户端未连接")
        
        if name not in self._collections:
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                metadata=metadata or {"hnsw:space": "cosine"},
                embedding_function=self._embedding_fn
            )
            logger.info(f"获取/创建 Collection: {name}")
        
        return self._collections[name]
    
    def add_documents(
        self,
        collection_name: str,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str]
    ) -> None:
        """
        添加文档到 Collection
        
        Args:
            collection_name: Collection 名称
            documents: 文档内容列表
            metadatas: 元数据列表
            ids: 文档ID列表
        """
        collection = self.get_or_create_collection(collection_name)
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"添加 {len(documents)} 个文档到 {collection_name}")
    
    def query(
        self,
        collection_name: str,
        query_text: str,
        n_results: int = 5,
        where: Optional[dict] = None
    ) -> dict:
        """
        查询相似文档
        
        Args:
            collection_name: Collection 名称
            query_text: 查询文本
            n_results: 返回结果数量
            where: 过滤条件
        
        Returns:
            查询结果
        """
        collection = self.get_or_create_collection(collection_name)
        
        query_params = {
            "query_texts": [query_text],
            "n_results": n_results
        }
        
        if where:
            query_params["where"] = where
        
        results = collection.query(**query_params)
        
        logger.debug(f"查询 {collection_name}: query={query_text[:50]}..., results={len(results.get('documents', [[]])[0])}")
        
        return results
    
    def delete_collection(self, name: str) -> None:
        """
        删除 Collection
        
        Args:
            name: Collection 名称
        """
        if not self._client:
            raise RuntimeError("Chroma 客户端未连接")
        
        try:
            self._client.delete_collection(name)
            if name in self._collections:
                del self._collections[name]
            logger.info(f"删除 Collection: {name}")
        except Exception as e:
            logger.warning(f"删除 Collection 失败: {e}")
    
    def count_documents(self, collection_name: str) -> int:
        """
        统计 Collection 中的文档数量
        
        Args:
            collection_name: Collection 名称
        
        Returns:
            文档数量
        """
        collection = self.get_or_create_collection(collection_name)
        return collection.count()


# 全局 Chroma 客户端实例
chroma_client: Optional[ChromaClient] = None


def get_chroma() -> ChromaClient:
    """获取 Chroma 客户端实例"""
    if chroma_client is None:
        raise RuntimeError("Chroma 客户端未初始化")
    return chroma_client
