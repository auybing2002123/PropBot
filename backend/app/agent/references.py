"""
引用管理模块
负责收集和管理工具调用产生的引用来源
"""
import json
from dataclasses import dataclass, field
from typing import Any

from app.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Reference:
    """引用来源"""
    id: int                    # 引用编号，如 1, 2, 3
    type: str                  # 来源类型：knowledge, database, web, faq, policy, guide
    title: str                 # 标题
    content: str               # 摘要内容
    source: str = ""           # 具体来源（文件名/表名/URL）
    relevance: int = 0         # 相关度分数（0-100）
    city: str | None = None    # 城市（如适用）
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "source": self.source,
            "relevance": self.relevance,
            "city": self.city
        }


class ReferenceCollector:
    """
    引用收集器
    在工具调用过程中收集检索结果作为引用
    """
    
    def __init__(self):
        self._references: list[Reference] = []
        self._next_id = 1
    
    def clear(self):
        """清空引用"""
        self._references = []
        self._next_id = 1
    
    def add_from_tool_result(self, tool_name: str, result: dict) -> list[Reference]:
        """
        从工具结果中提取引用
        
        Args:
            tool_name: 工具名称
            result: 工具执行结果
            
        Returns:
            新增的引用列表
        """
        new_refs = []
        
        # 根据工具类型提取引用
        if tool_name == "search_policy":
            new_refs = self._extract_policy_refs(result)
        elif tool_name == "search_faq":
            new_refs = self._extract_faq_refs(result)
        elif tool_name == "search_guide":
            new_refs = self._extract_guide_refs(result)
        elif tool_name == "query_market":
            new_refs = self._extract_market_refs(result)
        elif tool_name == "search_news":
            new_refs = self._extract_news_refs(result)
        
        # 添加到引用列表
        for ref in new_refs:
            ref.id = self._next_id
            self._next_id += 1
            self._references.append(ref)
        
        logger.debug(f"从工具 {tool_name} 提取了 {len(new_refs)} 个引用")
        return new_refs
    
    def _extract_policy_refs(self, result: dict) -> list[Reference]:
        """从政策检索结果提取引用"""
        refs = []
        results = result.get("results", [])
        
        for item in results[:3]:  # 最多取3个
            content = item.get("content", "")
            # 截取摘要
            summary = content[:200] + "..." if len(content) > 200 else content
            
            refs.append(Reference(
                id=0,  # 稍后分配
                type="policy",
                title=item.get("title", "政策文档"),
                content=summary,
                source=item.get("title", ""),
                relevance=item.get("relevance", 0),
                city=item.get("city")
            ))
        
        return refs
    
    def _extract_faq_refs(self, result: dict) -> list[Reference]:
        """从 FAQ 检索结果提取引用"""
        refs = []
        results = result.get("results", [])
        
        for item in results[:3]:
            answer = item.get("answer", "")
            summary = answer[:200] + "..." if len(answer) > 200 else answer
            
            refs.append(Reference(
                id=0,
                type="faq",
                title=item.get("question", "常见问题"),
                content=summary,
                source=f"FAQ - {item.get('category', '未分类')}",
                relevance=item.get("relevance", 0),
                city=item.get("city")
            ))
        
        return refs
    
    def _extract_guide_refs(self, result: dict) -> list[Reference]:
        """从购房指南检索结果提取引用"""
        refs = []
        results = result.get("results", [])
        
        for item in results[:3]:
            content = item.get("content", "")
            summary = content[:200] + "..." if len(content) > 200 else content
            
            refs.append(Reference(
                id=0,
                type="guide",
                title=item.get("title", "购房指南"),
                content=summary,
                source="购房流程指南",
                relevance=item.get("relevance", 0)
            ))
        
        return refs
    
    def _extract_market_refs(self, result: dict) -> list[Reference]:
        """从市场数据查询结果提取引用"""
        refs = []
        
        # 市场数据作为单个引用
        if result.get("success"):
            city = result.get("city", "")
            summary = result.get("summary", "")
            
            if summary:
                refs.append(Reference(
                    id=0,
                    type="database",
                    title=f"{city}房产市场数据",
                    content=summary,
                    source="市场数据库",
                    relevance=90,
                    city=city
                ))
        
        return refs
    
    def _extract_news_refs(self, result: dict) -> list[Reference]:
        """从新闻检索结果提取引用"""
        refs = []
        results = result.get("results", [])
        
        for item in results[:3]:
            content = item.get("content", "") or item.get("summary", "")
            summary = content[:200] + "..." if len(content) > 200 else content
            
            refs.append(Reference(
                id=0,
                type="web",
                title=item.get("title", "新闻资讯"),
                content=summary,
                source=item.get("url", "联网搜索"),
                relevance=item.get("relevance", 0)
            ))
        
        return refs
    
    def get_references(self) -> list[Reference]:
        """获取所有引用"""
        return self._references.copy()
    
    def get_references_dict(self) -> list[dict]:
        """获取所有引用（字典格式）"""
        return [ref.to_dict() for ref in self._references]
    
    def get_reference_prompt(self) -> str:
        """
        生成引用提示词，告诉 LLM 如何使用引用
        
        Returns:
            引用提示词
        """
        if not self._references:
            return ""
        
        # 构建引用列表
        ref_list = []
        for ref in self._references:
            ref_list.append(f"[{ref.id}] {ref.title}: {ref.content}")
        
        prompt = f"""
## 参考资料

以下是检索到的参考资料，请在回答中适当引用：

{chr(10).join(ref_list)}

## 引用格式要求

在回答中引用上述资料时，请使用方括号标注引用编号，例如：
- "根据南宁市限购政策[1]，外地人可以购买一套住房。"
- "公积金贷款额度最高为60万元[2]。"

注意：
1. 只在引用具体信息时添加标注，不要过度引用
2. 引用编号要与上述参考资料对应
3. 如果信息来自多个来源，可以标注多个编号，如[1][2]
"""
        return prompt
    
    def has_references(self) -> bool:
        """是否有引用"""
        return len(self._references) > 0
