# 新闻搜索工具
# 搜索最新的房产政策新闻和市场动态
# 使用模拟数据（比赛演示用）
# 支持 Redis 缓存加速

from datetime import datetime, timedelta
from typing import Any

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import register_tool
from app.db.redis import KnowledgeCache
from app.utils.logger import get_logger

logger = get_logger(__name__)


# 模拟新闻数据（比赛演示用）
MOCK_NEWS_DATA = [
    {
        "id": "news_001",
        "title": "南宁市发布2025年房地产市场调控新政",
        "summary": "南宁市住建局发布最新通知，进一步优化限购政策，支持刚性和改善性住房需求。首套房首付比例下调至20%，二套房首付比例下调至30%。",
        "source": "南宁市住建局",
        "url": "https://example.com/news/001",
        "publish_date": "2025-12-15",
        "city": "南宁",
        "keywords": ["限购", "首付", "调控"]
    },
    {
        "id": "news_002",
        "title": "广西公积金贷款额度上调 最高可贷80万",
        "summary": "广西住房公积金管理中心发布通知，自2026年1月1日起，双职工家庭公积金贷款最高额度由60万元上调至80万元，单职工最高50万元。",
        "source": "广西住房公积金管理中心",
        "url": "https://example.com/news/002",
        "publish_date": "2025-12-20",
        "city": None,
        "keywords": ["公积金", "贷款额度", "广西"]
    },
    {
        "id": "news_003",
        "title": "柳州楼市回暖 11月成交量环比上涨15%",
        "summary": "据柳州市房产交易中心数据，2025年11月柳州市商品住宅成交3200套，环比上涨15%，同比上涨8%。市场信心逐步恢复。",
        "source": "柳州日报",
        "url": "https://example.com/news/003",
        "publish_date": "2025-12-10",
        "city": "柳州",
        "keywords": ["成交量", "楼市", "回暖"]
    },
    {
        "id": "news_004",
        "title": "南宁青秀区新盘入市 均价约1.5万/㎡",
        "summary": "位于青秀区凤岭北的某品牌楼盘正式开盘，首推500套房源，均价约15000元/㎡，户型涵盖89-143㎡三至四房。",
        "source": "南宁晚报",
        "url": "https://example.com/news/004",
        "publish_date": "2025-12-18",
        "city": "南宁",
        "keywords": ["新盘", "青秀区", "开盘"]
    },
    {
        "id": "news_005",
        "title": "2026年房贷利率或将继续下行",
        "summary": "多位业内专家预测，2026年LPR仍有下调空间，首套房贷利率有望降至3.5%以下，进一步降低购房成本。",
        "source": "经济观察报",
        "url": "https://example.com/news/005",
        "publish_date": "2025-12-22",
        "city": None,
        "keywords": ["利率", "LPR", "房贷"]
    },
    {
        "id": "news_006",
        "title": "柳州城中区旧改项目启动 涉及3000户",
        "summary": "柳州市城中区老旧小区改造项目正式启动，涉及15个小区约3000户居民，计划投资2亿元，预计2027年完工。",
        "source": "柳州市住建局",
        "url": "https://example.com/news/006",
        "publish_date": "2025-12-08",
        "city": "柳州",
        "keywords": ["旧改", "城中区", "老旧小区"]
    },
    {
        "id": "news_007",
        "title": "南宁地铁6号线规划公示 沿线房价受关注",
        "summary": "南宁市轨道交通6号线一期工程规划公示，线路全长约25公里，设站18座，预计2028年通车。沿线楼盘关注度上升。",
        "source": "南宁市发改委",
        "url": "https://example.com/news/007",
        "publish_date": "2025-12-25",
        "city": "南宁",
        "keywords": ["地铁", "规划", "交通"]
    },
    {
        "id": "news_008",
        "title": "广西契税优惠政策延续至2026年底",
        "summary": "广西财政厅发布通知，个人购买家庭唯一住房契税优惠政策延续至2026年12月31日，90㎡以下按1%征收。",
        "source": "广西财政厅",
        "url": "https://example.com/news/008",
        "publish_date": "2025-12-28",
        "city": None,
        "keywords": ["契税", "优惠", "税费"]
    }
]


@register_tool
class SearchNewsTool(BaseTool):
    """新闻搜索工具"""
    
    name = "search_news"
    description = "搜索最新的房产政策新闻和市场动态"
    parameters = [
        ToolParameter(
            name="query",
            type="string",
            description="搜索关键词，如：限购政策、公积金、房价走势"
        ),
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，用于过滤特定城市的新闻",
            required=False,
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="days",
            type="integer",
            description="最近几天的新闻，默认30天",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行新闻搜索
        
        Args:
            query: 搜索关键词
            city: 城市过滤（可选）
            days: 最近几天（可选，默认30）
            
        Returns:
            新闻搜索结果
        """
        self.validate_params(**kwargs)
        
        query = kwargs["query"]
        city = kwargs.get("city")
        days = kwargs.get("days", 30)
        
        # 尝试从缓存获取
        cached = await KnowledgeCache.get("search_news", query, city, days=days)
        if cached:
            logger.debug(f"search_news 缓存命中: {query[:20]}...")
            return cached
        
        # 使用模拟数据搜索
        results = self._search_mock_news(query, city, days)
        
        if not results:
            return {
                "success": True,
                "query": query,
                "city": city,
                "days": days,
                "results": [],
                "count": 0,
                "summary": f"未找到与「{query}」相关的新闻" + (f"（{city}）" if city else "")
            }
        
        # 格式化结果
        formatted_results = []
        for news in results:
            formatted_results.append({
                "title": news["title"],
                "summary": news["summary"],
                "source": news["source"],
                "publish_date": news["publish_date"],
                "city": news.get("city"),
                "url": news["url"]
            })
        
        # 生成摘要
        summary = f"找到 {len(results)} 条相关新闻。"
        if results:
            latest = results[0]
            summary += f"最新一条：「{latest['title'][:20]}...」（{latest['publish_date']}）"
        
        result = {
            "success": True,
            "query": query,
            "city": city,
            "days": days,
            "results": formatted_results,
            "count": len(results),
            "summary": summary
        }
        
        # 写入缓存（新闻缓存时间短一些，30分钟）
        await KnowledgeCache.set("search_news", query, result, city, days=days, ttl=1800)
        
        return result
    
    def _search_mock_news(
        self, 
        query: str, 
        city: str | None, 
        days: int
    ) -> list[dict]:
        """搜索模拟新闻数据"""
        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        # 计算日期范围
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for news in MOCK_NEWS_DATA:
            # 城市过滤
            if city and news.get("city") and news["city"] != city:
                continue
            
            # 日期过滤
            try:
                news_date = datetime.strptime(news["publish_date"], "%Y-%m-%d")
                if news_date < cutoff_date:
                    continue
            except ValueError:
                pass
            
            # 关键词匹配
            score = 0
            
            # 标题匹配
            title_lower = news["title"].lower()
            for term in query_terms:
                if term in title_lower:
                    score += 3
            
            # 摘要匹配
            summary_lower = news["summary"].lower()
            for term in query_terms:
                if term in summary_lower:
                    score += 1
            
            # 关键词匹配
            for kw in news.get("keywords", []):
                if kw.lower() in query_lower or query_lower in kw.lower():
                    score += 2
            
            if score > 0:
                results.append({**news, "_score": score})
        
        # 按分数和日期排序
        results.sort(key=lambda x: (x["_score"], x["publish_date"]), reverse=True)
        
        # 移除内部分数字段
        for r in results:
            r.pop("_score", None)
        
        return results[:5]  # 最多返回5条
