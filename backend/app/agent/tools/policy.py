# 政策检索工具
# 使用 Chroma 向量数据库实现 RAG 检索
# 支持 Redis 缓存加速

import json
from pathlib import Path
from typing import Any

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import register_tool
from app.config.settings import get_settings
from app.db.redis import KnowledgeCache
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 知识库数据目录
KNOWLEDGE_BASE_DIR = Path(__file__).parent.parent.parent.parent / "data" / "knowledge"


class PolicyKnowledgeBase:
    """
    政策知识库管理类
    负责加载知识库数据并提供检索功能
    支持两种模式：
    1. Chroma 向量检索（需要 Chroma 服务）
    2. 关键词匹配（降级方案）
    """
    
    _instance: "PolicyKnowledgeBase | None" = None
    _initialized: bool = False
    
    def __new__(cls) -> "PolicyKnowledgeBase":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._policies: list[dict] = []
        self._faqs: list[dict] = []
        self._guides: list[dict] = []
        self._chroma_client = None
        self._use_vector_search = False
        
        # 加载知识库数据
        self._load_knowledge_base()
        
        # 尝试初始化 Chroma
        self._init_chroma()
        
        self._initialized = True
    
    def _load_knowledge_base(self) -> None:
        """加载知识库数据"""
        # 加载政策文档
        policies_dir = KNOWLEDGE_BASE_DIR / "policies"
        if policies_dir.exists():
            for policy_file in policies_dir.glob("*.md"):
                content = policy_file.read_text(encoding="utf-8")
                city = self._extract_city_from_filename(policy_file.name)
                
                # 解析 Markdown 文档
                policy_doc = {
                    "id": f"policy_{policy_file.stem}",
                    "type": "policy",
                    "city": city,
                    "filename": policy_file.name,
                    "content": content,
                    "title": self._extract_title(content),
                    "keywords": self._extract_keywords(content)
                }
                self._policies.append(policy_doc)
                logger.info(f"加载政策文档: {policy_file.name}")
        
        # 加载 FAQ
        faq_file = KNOWLEDGE_BASE_DIR / "faq" / "faq.json"
        if faq_file.exists():
            with open(faq_file, "r", encoding="utf-8") as f:
                faqs = json.load(f)
                for faq in faqs:
                    faq["type"] = "faq"
                    faq["id"] = faq.get("faq_id", f"faq_{len(self._faqs)}")
                self._faqs = faqs
                logger.info(f"加载 FAQ: {len(faqs)} 条")
        
        # 加载购房指南
        guides_dir = KNOWLEDGE_BASE_DIR / "guides"
        if guides_dir.exists():
            for guide_file in guides_dir.glob("*.md"):
                content = guide_file.read_text(encoding="utf-8")
                guide_doc = {
                    "id": f"guide_{guide_file.stem}",
                    "type": "guide",
                    "city": None,  # 指南通常不限城市
                    "filename": guide_file.name,
                    "content": content,
                    "title": self._extract_title(content),
                    "keywords": self._extract_keywords(content)
                }
                self._guides.append(guide_doc)
                logger.info(f"加载购房指南: {guide_file.name}")
    
    def _extract_city_from_filename(self, filename: str) -> str | None:
        """从文件名提取城市"""
        filename_lower = filename.lower()
        if "nanning" in filename_lower or "南宁" in filename:
            return "南宁"
        elif "liuzhou" in filename_lower or "柳州" in filename:
            return "柳州"
        return None
    
    def _extract_title(self, content: str) -> str:
        """从 Markdown 内容提取标题"""
        lines = content.strip().split("\n")
        for line in lines:
            if line.startswith("# "):
                return line[2:].strip()
        return "未知标题"
    
    def _extract_keywords(self, content: str) -> list[str]:
        """从内容提取关键词"""
        keywords = []
        
        # 查找关键词行
        lines = content.split("\n")
        for line in lines:
            if line.startswith("**关键词"):
                # 提取关键词
                parts = line.split(":")
                if len(parts) > 1:
                    kw_str = parts[1].strip().rstrip("*")
                    keywords = [k.strip() for k in kw_str.split(",")]
                break
        
        return keywords
    
    def _init_chroma(self) -> None:
        """初始化 Chroma 向量数据库连接（延迟初始化）"""
        # 不在这里初始化，改为在查询时动态获取
        self._use_vector_search = False
        self._chroma_client = None
    
    def _get_chroma_client(self):
        """动态获取 Chroma 客户端（每次查询时检查）"""
        try:
            from app.db.chroma import chroma_client
            if chroma_client is not None:
                return chroma_client
        except Exception:
            pass
        return None
    
    def search_policy(
        self,
        query: str,
        city: str | None = None,
        top_k: int = 3
    ) -> list[dict]:
        """
        搜索政策文档
        
        Args:
            query: 搜索查询
            city: 城市过滤（可选）
            top_k: 返回结果数量
            
        Returns:
            匹配的政策文档列表
        """
        if self._use_vector_search:
            return self._vector_search("policies", query, city, top_k)
        else:
            return self._keyword_search(query, "policy", city, top_k)
    
    def search_faq(
        self,
        query: str,
        city: str | None = None,
        category: str | None = None,
        top_k: int = 3
    ) -> list[dict]:
        """
        搜索 FAQ
        
        Args:
            query: 搜索查询
            city: 城市过滤（可选）
            category: 分类过滤（可选）
            top_k: 返回结果数量
            
        Returns:
            匹配的 FAQ 列表
        """
        if self._use_vector_search:
            results = self._vector_search("faq", query, city, top_k * 2)  # 多取一些用于过滤
            # 额外按分类过滤
            if category:
                results = [r for r in results if r.get("category") == category]
            return results[:top_k]
        else:
            return self._keyword_search_faq(query, city, category, top_k)
    
    def search_guide(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:
        """
        搜索购房指南
        
        Args:
            query: 搜索查询
            top_k: 返回结果数量
            
        Returns:
            匹配的指南列表
        """
        if self._use_vector_search:
            return self._vector_search("guides", query, None, top_k)
        else:
            return self._keyword_search(query, "guide", None, top_k)
    
    def _vector_search(
        self,
        collection_name: str,
        query: str,
        city: str | None,
        top_k: int
    ) -> list[dict]:
        """使用 Chroma 向量检索"""
        # 动态获取 Chroma 客户端
        chroma = self._get_chroma_client()
        if chroma is None:
            # 降级到关键词搜索
            logger.debug("Chroma 客户端不可用，降级到关键词搜索")
            doc_type = "policy" if collection_name == "policies" else collection_name.rstrip("s")
            if doc_type == "faq":
                return self._keyword_search_faq(query, city, None, top_k)
            return self._keyword_search(query, doc_type, city, top_k)
        
        try:
            # 构建过滤条件
            where_filter = None
            if city:
                where_filter = {"city": city}
            
            # 使用全局 chroma_client 查询
            results = chroma.query(
                collection_name=collection_name,
                query_text=query,
                n_results=top_k,
                where=where_filter
            )
            
            # 格式化结果
            formatted_results = []
            if results and results.get("documents") and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results.get("metadatas") else {}
                    distance = results["distances"][0][i] if results.get("distances") else 0
                    
                    # 将距离转换为相似度分数（距离越小越相似）
                    relevance_score = max(0, 1 - distance) if distance else 0.5
                    
                    # 对于 FAQ，answer 可能存储在 content 中或 metadata 中
                    answer = metadata.get("answer")
                    if not answer and collection_name == "faq":
                        # 如果 metadata 中没有 answer，尝试从 content 获取
                        answer = doc
                    
                    formatted_results.append({
                        "id": results["ids"][0][i] if results.get("ids") else f"doc_{i}",
                        "content": doc,
                        "relevance_score": relevance_score,
                        "type": metadata.get("type", collection_name),
                        "city": metadata.get("city"),
                        "title": metadata.get("title"),
                        "category": metadata.get("category"),
                        "keywords": metadata.get("keywords", "").split(",") if metadata.get("keywords") else [],
                        "question": metadata.get("question"),
                        "answer": answer
                    })
            
            logger.debug(f"向量检索 {collection_name}: query={query[:30]}..., results={len(formatted_results)}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"向量检索失败: {e}")
            # 降级到关键词搜索
            doc_type = "policy" if collection_name == "policies" else collection_name.rstrip("s")
            if doc_type == "faq":
                return self._keyword_search_faq(query, city, None, top_k)
            return self._keyword_search(query, doc_type, city, top_k)
    
    def _keyword_search(
        self,
        query: str,
        doc_type: str,
        city: str | None,
        top_k: int
    ) -> list[dict]:
        """使用关键词匹配（降级方案）"""
        results = []
        
        # 选择数据源
        if doc_type == "policy":
            docs = self._policies
        elif doc_type == "guide":
            docs = self._guides
        else:
            docs = self._faqs
        
        # 城市过滤
        if city:
            docs = [d for d in docs if d.get("city") == city or d.get("city") is None]
        
        # 关键词匹配评分
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for doc in docs:
            score = 0
            
            # 检查内容匹配
            content = doc.get("content", "") or doc.get("answer", "")
            content_lower = content.lower()
            
            for term in query_terms:
                if term in content_lower:
                    score += 1
            
            # 检查关键词匹配
            keywords = doc.get("keywords", [])
            if isinstance(keywords, str):
                keywords = keywords.split(",")
            
            for kw in keywords:
                if kw.lower() in query_lower or query_lower in kw.lower():
                    score += 2  # 关键词匹配权重更高
            
            # 检查标题/问题匹配
            title = doc.get("title", "") or doc.get("question", "")
            if query_lower in title.lower():
                score += 3
            
            if score > 0:
                results.append({
                    "id": doc.get("id", ""),
                    "content": content[:500] + "..." if len(content) > 500 else content,
                    "relevance_score": min(score / 10, 1.0),
                    "type": doc_type,
                    "city": doc.get("city"),
                    "title": doc.get("title") or doc.get("question"),
                    "category": doc.get("category"),
                    "keywords": keywords
                })
        
        # 按分数排序
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]
    
    def _keyword_search_faq(
        self,
        query: str,
        city: str | None,
        category: str | None,
        top_k: int
    ) -> list[dict]:
        """FAQ 关键词搜索"""
        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for faq in self._faqs:
            # 城市过滤
            if city and faq.get("city") and faq["city"] != city:
                continue
            
            # 分类过滤
            if category and faq.get("category") != category:
                continue
            
            score = 0
            
            # 问题匹配
            question = faq.get("question", "").lower()
            for term in query_terms:
                if term in question:
                    score += 2
            
            # 答案匹配
            answer = faq.get("answer", "").lower()
            for term in query_terms:
                if term in answer:
                    score += 1
            
            # 关键词匹配
            keywords = faq.get("keywords", [])
            for kw in keywords:
                if kw.lower() in query_lower:
                    score += 3
            
            if score > 0:
                results.append({
                    "id": faq.get("faq_id", ""),
                    "question": faq.get("question", ""),
                    "answer": faq.get("answer", ""),
                    "category": faq.get("category", ""),
                    "city": faq.get("city"),
                    "relevance_score": min(score / 10, 1.0),
                    "keywords": keywords
                })
        
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:top_k]


# 全局知识库实例
_knowledge_base: PolicyKnowledgeBase | None = None


def get_knowledge_base() -> PolicyKnowledgeBase:
    """获取知识库单例"""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = PolicyKnowledgeBase()
    return _knowledge_base



@register_tool
class SearchGuideTool(BaseTool):
    """购房指南检索工具"""
    
    name = "search_guide"
    description = "检索购房流程指南，回答从看房到交房的各环节问题"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="用户问题，如：买房流程、签合同注意事项、交房验收"
        ),
        ToolParameter(
            name="stage",
            type="string",
            description="购房阶段，用于过滤特定阶段的内容",
            required=False,
            enum=["看房", "签约", "贷款", "过户", "交房", "装修"]
        ),
        ToolParameter(
            name="top_k",
            type="integer",
            description="返回结果数量，默认3条",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行购房指南检索
        
        Args:
            query: 搜索查询
            stage: 购房阶段过滤（可选）
            top_k: 返回数量（可选，默认3）
            
        Returns:
            搜索结果
        """
        self.validate_params(**kwargs)
        
        query = kwargs["query"]
        stage = kwargs.get("stage")
        top_k = kwargs.get("top_k", 3)
        
        # 尝试从缓存获取
        cached = await KnowledgeCache.get("search_guide", query, stage=stage, top_k=top_k)
        if cached:
            logger.debug(f"search_guide 缓存命中: {query[:20]}...")
            return cached
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 如果指定了阶段，将阶段关键词加入查询
        search_query = query
        if stage:
            search_query = f"{stage} {query}"
        
        # 搜索指南（使用 guide 类型）
        results = kb._keyword_search(search_query, "guide", None, top_k)
        
        if not results:
            return {
                "success": True,
                "query": query,
                "stage": stage,
                "results": [],
                "count": 0,
                "summary": f"未找到与「{query}」相关的购房指南" + (f"（{stage}阶段）" if stage else "")
            }
        
        # 格式化结果
        formatted_results = []
        for r in results:
            content = r.get("content", "")
            # 提取相关段落
            relevant_section = self._extract_relevant_section(content, query, stage)
            
            formatted_results.append({
                "title": r.get("title", "购房指南"),
                "content": relevant_section,
                "relevance": round(r.get("relevance_score", 0) * 100),
                "keywords": r.get("keywords", [])
            })
        
        # 生成摘要
        summary = f"找到 {len(results)} 条相关指南。"
        if stage:
            summary += f"已筛选{stage}阶段的内容。"
        
        result = {
            "success": True,
            "query": query,
            "stage": stage,
            "results": formatted_results,
            "count": len(results),
            "summary": summary
        }
        
        # 写入缓存
        await KnowledgeCache.set("search_guide", query, result, stage=stage, top_k=top_k)
        
        return result
    
    def _extract_relevant_section(
        self, 
        content: str, 
        query: str, 
        stage: str | None
    ) -> str:
        """提取与查询相关的内容段落"""
        # 按段落分割
        paragraphs = content.split("\n\n")
        
        # 查找包含关键词的段落
        query_terms = query.lower().split()
        if stage:
            query_terms.append(stage.lower())
        
        relevant_paragraphs = []
        for para in paragraphs:
            para_lower = para.lower()
            score = sum(1 for term in query_terms if term in para_lower)
            if score > 0:
                relevant_paragraphs.append((score, para))
        
        # 按相关度排序
        relevant_paragraphs.sort(key=lambda x: x[0], reverse=True)
        
        # 返回最相关的段落（限制长度）
        if relevant_paragraphs:
            result = "\n\n".join(p[1] for p in relevant_paragraphs[:2])
            return result[:800] if len(result) > 800 else result
        
        # 如果没有匹配，返回开头部分
        return content[:500] + "..." if len(content) > 500 else content


@register_tool
class SearchPolicyTool(BaseTool):
    """政策搜索工具"""
    
    name = "search_policy"
    description = "搜索购房相关政策文档，包括限购限贷政策、税费政策、公积金政策等"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="搜索关键词或问题，如：南宁限购政策、首付比例、公积金贷款"
        ),
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，用于过滤特定城市的政策，如：南宁、柳州",
            required=False,
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="top_k",
            type="integer",
            description="返回结果数量，默认3条",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行政策搜索
        
        Args:
            query: 搜索查询
            city: 城市过滤（可选）
            top_k: 返回数量（可选，默认3）
            
        Returns:
            搜索结果
        """
        self.validate_params(**kwargs)
        
        query = kwargs["query"]
        city = kwargs.get("city")
        top_k = kwargs.get("top_k", 3)
        
        # 尝试从缓存获取
        cached = await KnowledgeCache.get("search_policy", query, city, top_k=top_k)
        if cached:
            logger.debug(f"search_policy 缓存命中: {query[:20]}...")
            return cached
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 搜索政策
        results = kb.search_policy(query, city, top_k)
        
        if not results:
            return {
                "success": True,
                "query": query,
                "city": city,
                "results": [],
                "count": 0,
                "summary": f"未找到与「{query}」相关的政策文档" + (f"（{city}）" if city else "")
            }
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                "title": r.get("title", "政策文档"),
                "city": r.get("city"),
                "content": r.get("content", "")[:800],  # 限制内容长度
                "relevance": round(r.get("relevance_score", 0) * 100),
                "keywords": r.get("keywords", [])
            })
        
        # 生成摘要
        top_result = formatted_results[0]
        summary = f"找到 {len(results)} 条相关政策。"
        if top_result.get("city"):
            summary += f"最相关的是{top_result['city']}的政策文档。"
        
        result = {
            "success": True,
            "query": query,
            "city": city,
            "results": formatted_results,
            "count": len(results),
            "summary": summary
        }
        
        # 写入缓存
        await KnowledgeCache.set("search_policy", query, result, city, top_k=top_k)
        
        return result


@register_tool
class SearchFAQTool(BaseTool):
    """FAQ 搜索工具"""
    
    name = "search_faq"
    description = "搜索购房常见问题解答，包括贷款、税费、流程、资格等问题"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="搜索问题，如：公积金贷款额度、首付多少、买房流程"
        ),
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，用于过滤特定城市的问题，如：南宁、柳州",
            required=False,
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="category",
            type="string",
            description="问题分类，如：贷款、税费、流程、购房资格、公积金",
            required=False,
            enum=["贷款", "税费", "流程", "购房资格", "公积金", "首付", "利率", "还款压力"]
        ),
        ToolParameter(
            name="top_k",
            type="integer",
            description="返回结果数量，默认3条",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行 FAQ 搜索
        
        Args:
            query: 搜索查询
            city: 城市过滤（可选）
            category: 分类过滤（可选）
            top_k: 返回数量（可选，默认3）
            
        Returns:
            搜索结果
        """
        self.validate_params(**kwargs)
        
        query = kwargs["query"]
        city = kwargs.get("city")
        category = kwargs.get("category")
        top_k = kwargs.get("top_k", 3)
        
        # 尝试从缓存获取
        cached = await KnowledgeCache.get(
            "search_faq", query, city, category=category, top_k=top_k
        )
        if cached:
            logger.debug(f"search_faq 缓存命中: {query[:20]}...")
            return cached
        
        # 获取知识库
        kb = get_knowledge_base()
        
        # 搜索 FAQ
        results = kb.search_faq(query, city, category, top_k)
        
        if not results:
            return {
                "success": True,
                "query": query,
                "city": city,
                "category": category,
                "results": [],
                "count": 0,
                "summary": f"未找到与「{query}」相关的常见问题"
            }
        
        # 格式化结果
        formatted_results = []
        for r in results:
            formatted_results.append({
                "question": r.get("question", ""),
                "answer": r.get("answer", ""),
                "category": r.get("category", ""),
                "city": r.get("city"),
                "relevance": round(r.get("relevance_score", 0) * 100)
            })
        
        # 生成摘要
        top_result = formatted_results[0]
        summary = f"找到 {len(results)} 个相关问题。最相关的问题是：「{top_result['question'][:30]}...」"
        
        result = {
            "success": True,
            "query": query,
            "city": city,
            "category": category,
            "results": formatted_results,
            "count": len(results),
            "summary": summary,
            # 直接返回最佳答案，方便 Agent 使用
            "best_answer": top_result["answer"] if formatted_results else None
        }
        
        # 写入缓存
        await KnowledgeCache.set(
            "search_faq", query, result, city, category=category, top_k=top_k
        )
        
        return result
