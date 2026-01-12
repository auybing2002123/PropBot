# 市场查询工具
# 包含市场数据查询、房价走势、区域对比、购房时机判断

from app.agent.tools.base import BaseTool, ToolParameter
from app.agent.tools.registry import register_tool
from app.data.loader import get_data_loader


def get_city_districts(city: str) -> list[str]:
    """获取城市的所有区域"""
    return get_data_loader().get_city_districts(city)


def get_district_data(city: str, district: str) -> dict | None:
    """获取指定区域的市场数据"""
    return get_data_loader().get_district_data(city, district)


def get_city_overview(city: str) -> dict | None:
    """获取城市整体市场概况"""
    market_data = get_data_loader().get_market_data(city)
    if not market_data:
        return None
    
    districts = market_data.districts
    total_sales = sum(d.monthly_sales for d in districts.values())
    total_inventory = sum(d.inventory for d in districts.values())
    
    # 加权平均价格（按成交量加权）
    weighted_price = sum(
        d.avg_price * d.monthly_sales 
        for d in districts.values()
    ) / total_sales if total_sales > 0 else 0
    
    # 平均同比变化
    avg_yoy = sum(d.yoy_change for d in districts.values()) / len(districts)
    
    return {
        "city": city,
        "avg_price": round(weighted_price, 0),
        "total_monthly_sales": total_sales,
        "total_inventory": total_inventory,
        "avg_yoy_change": round(avg_yoy, 1),
        "district_count": len(districts)
    }


@register_tool
class QueryMarketTool(BaseTool):
    """市场数据查询工具"""
    
    name = "query_market"
    description = "查询指定城市和区域的房产市场数据，包括均价、成交量、库存量等信息"
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，如：南宁、柳州",
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="district",
            type="string",
            description="区域名称，如：青秀区、城中区。不填则返回城市整体数据",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行市场数据查询
        
        Args:
            city: 城市名称
            district: 区域名称（可选）
            
        Returns:
            市场数据查询结果
        """
        self.validate_params(**kwargs)
        
        city = kwargs["city"]
        district = kwargs.get("district")
        
        # 获取 DataLoader
        loader = get_data_loader()
        supported_cities = loader.get_supported_cities()
        
        # 检查城市是否支持
        if city not in supported_cities:
            return {
                "success": False,
                "error": f"暂不支持查询 {city} 的市场数据，目前支持：{', '.join(supported_cities)}"
            }
        
        # 如果指定了区域，返回区域数据
        if district:
            data = get_district_data(city, district)
            if not data:
                available = get_city_districts(city)
                return {
                    "success": False,
                    "error": f"{city}没有 {district} 的数据，可选区域：{', '.join(available)}"
                }
            
            return {
                "success": True,
                "city": city,
                "district": district,
                "avg_price": data["avg_price"],
                "price_range": data["price_range"],
                "monthly_sales": data["monthly_sales"],
                "inventory": data["inventory"],
                "inventory_months": data["inventory_months"],
                "yoy_change": data["yoy_change"],
                "mom_change": data["mom_change"],
                "hot_level": data["hot_level"],
                "description": data["description"],
                "summary": (
                    f"{city}{district}当前均价 {data['avg_price']} 元/㎡，"
                    f"月成交 {data['monthly_sales']} 套，"
                    f"同比{'上涨' if data['yoy_change'] > 0 else '下跌'} {abs(data['yoy_change'])}%，"
                    f"市场热度{data['hot_level']}。"
                )
            }
        
        # 返回城市整体数据
        overview = get_city_overview(city)
        market_data = loader.get_market_data(city)
        
        districts_data = []
        for dist_name, dist_data in market_data.districts.items():
            districts_data.append({
                "district": dist_name,
                "avg_price": dist_data.avg_price,
                "monthly_sales": dist_data.monthly_sales,
                "hot_level": dist_data.hot_level
            })
        
        # 按均价排序
        districts_data.sort(key=lambda x: x["avg_price"], reverse=True)
        
        return {
            "success": True,
            "city": city,
            "overview": overview,
            "districts": districts_data,
            "summary": (
                f"{city}全市均价约 {overview['avg_price']:.0f} 元/㎡，"
                f"月成交 {overview['total_monthly_sales']} 套，"
                f"同比{'上涨' if overview['avg_yoy_change'] > 0 else '下跌'} {abs(overview['avg_yoy_change'])}%。"
                f"共 {overview['district_count']} 个区域可查询。"
            )
        }



@register_tool
class QueryPriceTrendTool(BaseTool):
    """房价走势查询工具"""
    
    name = "query_price_trend"
    description = "查询指定城市和区域的历史房价走势数据"
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，如：南宁、柳州",
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="district",
            type="string",
            description="区域名称，如：青秀区、城中区"
        ),
        ToolParameter(
            name="months",
            type="integer",
            description="查询最近几个月的数据，默认12个月",
            required=False
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行房价走势查询
        
        Args:
            city: 城市名称
            district: 区域名称
            months: 查询月数（默认12）
            
        Returns:
            房价走势数据
        """
        self.validate_params(**kwargs)
        
        city = kwargs["city"]
        district = kwargs["district"]
        months = kwargs.get("months", 12)
        
        # 从 DataLoader 获取走势数据
        loader = get_data_loader()
        trend_data = loader.get_price_trend(city, district)
        
        # 检查数据是否存在
        if trend_data is None:
            market_data = loader.get_market_data(city)
            if market_data is None:
                return {
                    "success": False,
                    "error": f"暂无 {city} 的房价走势数据"
                }
            
            available = list(market_data.price_trends.keys())
            return {
                "success": False,
                "error": f"暂无 {city}{district} 的走势数据，可查询：{', '.join(available)}"
            }
        
        # 限制返回月数
        if months < len(trend_data):
            trend_data = trend_data[-months:]
        
        # 计算涨跌幅
        if len(trend_data) >= 2:
            start_price = trend_data[0]["price"]
            end_price = trend_data[-1]["price"]
            change = end_price - start_price
            change_pct = (change / start_price) * 100 if start_price > 0 else 0
        else:
            change = 0
            change_pct = 0
        
        # 计算最高最低价
        prices = [d["price"] for d in trend_data]
        max_price = max(prices)
        min_price = min(prices)
        max_month = next(d["month"] for d in trend_data if d["price"] == max_price)
        min_month = next(d["month"] for d in trend_data if d["price"] == min_price)
        
        return {
            "success": True,
            "city": city,
            "district": district,
            "period": f"近{len(trend_data)}个月",
            "trend": trend_data,
            "statistics": {
                "start_price": trend_data[0]["price"],
                "end_price": trend_data[-1]["price"],
                "change": round(change, 0),
                "change_pct": round(change_pct, 2),
                "max_price": max_price,
                "max_month": max_month,
                "min_price": min_price,
                "min_month": min_month,
                "avg_price": round(sum(prices) / len(prices), 0)
            },
            "summary": (
                f"{city}{district}近{len(trend_data)}个月房价"
                f"{'上涨' if change > 0 else '下跌'} {abs(change):.0f} 元/㎡，"
                f"跌幅 {abs(change_pct):.1f}%。"
                f"当前均价 {trend_data[-1]['price']} 元/㎡。"
            )
        }



@register_tool
class CompareDistrictsTool(BaseTool):
    """区域对比工具"""
    
    name = "compare_districts"
    description = "对比多个区域的房产市场数据，帮助用户选择合适的区域"
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，如：南宁、柳州",
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="districts",
            type="string",
            description="要对比的区域名称，用逗号分隔，如：青秀区,良庆区,江南区"
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行区域对比
        
        Args:
            city: 城市名称
            districts: 区域名称（逗号分隔）
            
        Returns:
            区域对比结果
        """
        self.validate_params(**kwargs)
        
        city = kwargs["city"]
        districts_str = kwargs["districts"]
        
        # 解析区域列表
        districts = [d.strip() for d in districts_str.split(",") if d.strip()]
        
        if len(districts) < 2:
            return {
                "success": False,
                "error": "请至少提供2个区域进行对比"
            }
        
        # 获取 DataLoader
        loader = get_data_loader()
        market_data = loader.get_market_data(city)
        
        if not market_data:
            return {
                "success": False,
                "error": f"暂不支持 {city} 的数据查询"
            }
        
        # 收集各区域数据
        comparison = []
        not_found = []
        
        for district in districts:
            data = get_district_data(city, district)
            if data:
                comparison.append({
                    "district": district,
                    "avg_price": data["avg_price"],
                    "price_range": data["price_range"],
                    "monthly_sales": data["monthly_sales"],
                    "inventory": data["inventory"],
                    "inventory_months": data["inventory_months"],
                    "yoy_change": data["yoy_change"],
                    "hot_level": data["hot_level"],
                    "description": data["description"]
                })
            else:
                not_found.append(district)
        
        if not comparison:
            available = get_city_districts(city)
            return {
                "success": False,
                "error": f"未找到有效区域数据，可选区域：{', '.join(available)}"
            }
        
        # 计算对比指标
        prices = [d["avg_price"] for d in comparison]
        cheapest = min(comparison, key=lambda x: x["avg_price"])
        most_expensive = max(comparison, key=lambda x: x["avg_price"])
        hottest = max(comparison, key=lambda x: x["monthly_sales"])
        
        # 生成推荐
        recommendations = []
        
        # 性价比推荐（价格低但成交活跃）
        for d in comparison:
            if d["avg_price"] <= sum(prices) / len(prices) and d["hot_level"] in ["中", "高"]:
                recommendations.append({
                    "district": d["district"],
                    "reason": "性价比高",
                    "detail": f"均价 {d['avg_price']} 元/㎡，低于对比区域平均价，市场热度{d['hot_level']}"
                })
        
        # 投资潜力推荐（跌幅小或上涨）
        stable = min(comparison, key=lambda x: abs(x["yoy_change"]))
        if stable["yoy_change"] > -2:
            recommendations.append({
                "district": stable["district"],
                "reason": "价格稳定",
                "detail": f"同比变化 {stable['yoy_change']}%，价格相对稳定"
            })
        
        return {
            "success": True,
            "city": city,
            "comparison": comparison,
            "not_found": not_found if not_found else None,
            "analysis": {
                "cheapest": {
                    "district": cheapest["district"],
                    "price": cheapest["avg_price"]
                },
                "most_expensive": {
                    "district": most_expensive["district"],
                    "price": most_expensive["avg_price"]
                },
                "price_diff": most_expensive["avg_price"] - cheapest["avg_price"],
                "hottest": {
                    "district": hottest["district"],
                    "monthly_sales": hottest["monthly_sales"]
                }
            },
            "recommendations": recommendations if recommendations else None,
            "summary": (
                f"对比 {len(comparison)} 个区域：\n"
                f"- 最贵：{most_expensive['district']}（{most_expensive['avg_price']} 元/㎡）\n"
                f"- 最便宜：{cheapest['district']}（{cheapest['avg_price']} 元/㎡）\n"
                f"- 价差：{most_expensive['avg_price'] - cheapest['avg_price']} 元/㎡\n"
                f"- 成交最活跃：{hottest['district']}（月成交 {hottest['monthly_sales']} 套）"
            )
        }



@register_tool
class JudgeTimingTool(BaseTool):
    """购房时机判断工具"""
    
    name = "judge_timing"
    description = "根据市场数据分析当前是否是购房的好时机，给出评分和建议"
    parameters = [
        ToolParameter(
            name="city",
            type="string",
            description="城市名称，如：南宁、柳州",
            enum=["南宁", "柳州"]
        ),
        ToolParameter(
            name="district",
            type="string",
            description="区域名称，如：青秀区、城中区",
            required=False
        ),
        ToolParameter(
            name="purpose",
            type="string",
            description="购房目的：自住、投资",
            required=False,
            enum=["自住", "投资"]
        )
    ]
    
    async def execute(self, **kwargs) -> dict:
        """
        执行购房时机判断
        
        Args:
            city: 城市名称
            district: 区域名称（可选）
            purpose: 购房目的（可选）
            
        Returns:
            时机判断结果
        """
        self.validate_params(**kwargs)
        
        city = kwargs["city"]
        district = kwargs.get("district")
        purpose = kwargs.get("purpose", "自住")
        
        # 获取 DataLoader
        loader = get_data_loader()
        market_data = loader.get_market_data(city)
        
        if not market_data:
            return {
                "success": False,
                "error": f"暂不支持 {city} 的市场分析"
            }
        
        # 获取分析数据
        if district:
            data = get_district_data(city, district)
            if not data:
                return {
                    "success": False,
                    "error": f"未找到 {city}{district} 的数据"
                }
            analysis_data = [{"district": district, **data}]
        else:
            # 分析整个城市
            analysis_data = [
                {"district": k, **v.model_dump()} 
                for k, v in market_data.districts.items()
            ]
        
        # 计算各项指标得分
        scores = self._calculate_scores(analysis_data, purpose)
        
        # 综合评分（满分100）
        total_score = scores["total"]
        
        # 判断时机等级
        if total_score >= 70:
            timing_level = "good"
            timing_name = "较好"
            timing_color = "green"
        elif total_score >= 50:
            timing_level = "neutral"
            timing_name = "一般"
            timing_color = "orange"
        else:
            timing_level = "wait"
            timing_name = "观望"
            timing_color = "red"
        
        # 生成建议
        suggestions = self._generate_suggestions(scores, purpose, timing_level)
        
        # 生成分析要点
        key_points = self._generate_key_points(analysis_data, scores)
        
        location = f"{city}{district}" if district else city
        
        return {
            "success": True,
            "city": city,
            "district": district,
            "purpose": purpose,
            "score": {
                "total": total_score,
                "price_trend": scores["price_trend"],
                "inventory": scores["inventory"],
                "market_activity": scores["market_activity"],
                "policy": scores["policy"]
            },
            "timing": {
                "level": timing_level,
                "name": timing_name,
                "color": timing_color
            },
            "key_points": key_points,
            "suggestions": suggestions,
            "summary": (
                f"{location}当前购房时机评分：{total_score}分（{timing_name}）。\n"
                f"{'建议可以考虑入手' if timing_level == 'good' else '建议继续观望' if timing_level == 'wait' else '可根据个人情况决定'}。"
            )
        }
    
    def _calculate_scores(self, data: list[dict], purpose: str) -> dict:
        """计算各项指标得分"""
        # 价格趋势得分（下跌对买家有利）
        avg_yoy = sum(d["yoy_change"] for d in data) / len(data)
        if avg_yoy <= -5:
            price_score = 90  # 大幅下跌，买入时机好
        elif avg_yoy <= -2:
            price_score = 75
        elif avg_yoy <= 0:
            price_score = 60
        elif avg_yoy <= 3:
            price_score = 45
        else:
            price_score = 30  # 上涨中，买入成本高
        
        # 库存得分（库存多对买家有利，选择多）
        avg_inventory_months = sum(d["inventory_months"] for d in data) / len(data)
        if avg_inventory_months >= 18:
            inventory_score = 85  # 库存充足，议价空间大
        elif avg_inventory_months >= 12:
            inventory_score = 70
        elif avg_inventory_months >= 8:
            inventory_score = 55
        else:
            inventory_score = 40  # 库存紧张
        
        # 市场活跃度得分
        avg_sales = sum(d["monthly_sales"] for d in data) / len(data)
        hot_count = sum(1 for d in data if d["hot_level"] == "高")
        
        if purpose == "投资":
            # 投资看重活跃度
            if hot_count > len(data) / 2:
                activity_score = 75
            elif avg_sales > 200:
                activity_score = 65
            else:
                activity_score = 50
        else:
            # 自住不太看重活跃度
            activity_score = 60
        
        # 政策得分（当前政策环境，固定值模拟）
        policy_score = 70  # 当前政策相对宽松
        
        # 根据购房目的调整权重
        if purpose == "投资":
            weights = {
                "price_trend": 0.35,
                "inventory": 0.25,
                "market_activity": 0.25,
                "policy": 0.15
            }
        else:  # 自住
            weights = {
                "price_trend": 0.30,
                "inventory": 0.30,
                "market_activity": 0.15,
                "policy": 0.25
            }
        
        total = (
            price_score * weights["price_trend"] +
            inventory_score * weights["inventory"] +
            activity_score * weights["market_activity"] +
            policy_score * weights["policy"]
        )
        
        return {
            "total": round(total),
            "price_trend": price_score,
            "inventory": inventory_score,
            "market_activity": activity_score,
            "policy": policy_score
        }
    
    def _generate_suggestions(self, scores: dict, purpose: str, timing_level: str) -> list[str]:
        """生成购房建议"""
        suggestions = []
        
        if timing_level == "good":
            suggestions.append("当前市场对买家较为有利，可以积极看房")
            if scores["price_trend"] >= 70:
                suggestions.append("房价处于下行通道，议价空间较大")
            if scores["inventory"] >= 70:
                suggestions.append("库存充足，可以多比较几个楼盘")
        elif timing_level == "wait":
            suggestions.append("建议继续观望，等待更好的入市时机")
            if scores["price_trend"] < 50:
                suggestions.append("房价仍有下行空间，不必急于入手")
        else:
            suggestions.append("市场处于调整期，可根据个人需求决定")
        
        if purpose == "自住":
            suggestions.append("自住需求可适当放宽时机考量，重点关注房源本身")
            suggestions.append("建议优先考虑交通、学区、配套等因素")
        else:
            suggestions.append("投资需谨慎，当前市场整体偏弱")
            suggestions.append("如需投资，建议选择核心区域优质房源")
        
        return suggestions
    
    def _generate_key_points(self, data: list[dict], scores: dict) -> list[str]:
        """生成分析要点"""
        points = []
        
        avg_yoy = sum(d["yoy_change"] for d in data) / len(data)
        points.append(f"房价同比变化：{avg_yoy:.1f}%")
        
        avg_inventory = sum(d["inventory_months"] for d in data) / len(data)
        points.append(f"平均去化周期：{avg_inventory:.1f}个月")
        
        if scores["price_trend"] >= 70:
            points.append("价格趋势：下行，买方市场")
        elif scores["price_trend"] >= 50:
            points.append("价格趋势：平稳")
        else:
            points.append("价格趋势：上行，卖方市场")
        
        if scores["inventory"] >= 70:
            points.append("库存状况：充足，选择空间大")
        elif scores["inventory"] >= 50:
            points.append("库存状况：适中")
        else:
            points.append("库存状况：偏紧")
        
        return points
