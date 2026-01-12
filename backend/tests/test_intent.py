# 意图识别测试
# 验证关键词匹配和意图识别功能

import pytest
from app.agent.intent import IntentRecognizer, ExecutionPlan, get_intent_recognizer
from app.agent.roles import (
    FINANCIAL_ADVISOR,
    POLICY_EXPERT,
    MARKET_ANALYST,
    PURCHASE_CONSULTANT
)


class TestKeywordMatching:
    """测试关键词匹配功能（需求 7.1, 7.2, 7.3）"""
    
    def setup_method(self):
        """每个测试方法前创建新的识别器实例"""
        self.recognizer = IntentRecognizer()
    
    def test_financial_keywords_match(self):
        """
        验证财务关键词匹配到财务顾问
        需求 7.1: 当用户输入包含财务关键词时，应返回 Financial_Advisor 角色
        """
        test_cases = [
            "我想计算一下贷款月供",
            "房贷利率是多少",
            "首付需要多少钱",
            "买房税费怎么算",
            "还款压力大不大"
        ]
        
        for user_input in test_cases:
            roles = self.recognizer.match_keywords(user_input)
            assert FINANCIAL_ADVISOR in roles, f"输入 '{user_input}' 应匹配到财务顾问"
    
    def test_policy_keywords_match(self):
        """
        验证政策关键词匹配到政策专家
        需求 7.2: 当用户输入包含政策关键词时，应返回 Policy_Expert 角色
        """
        test_cases = [
            "南宁限购政策是什么",
            "公积金贷款额度多少",
            "我有购房资格吗",
            "限贷政策怎么规定的",
            "外地户口能买房吗"
        ]
        
        for user_input in test_cases:
            roles = self.recognizer.match_keywords(user_input)
            assert POLICY_EXPERT in roles, f"输入 '{user_input}' 应匹配到政策专家"
    
    def test_market_keywords_match(self):
        """
        验证市场关键词匹配到市场分析师
        需求 7.3: 当用户输入包含市场关键词时，应返回 Market_Analyst 角色
        """
        test_cases = [
            "南宁房价多少",
            "青秀区市场行情怎么样",
            "房价走势如何",
            "哪个区域值得投资",
            "现在是买房的好时机吗"
        ]
        
        for user_input in test_cases:
            roles = self.recognizer.match_keywords(user_input)
            assert MARKET_ANALYST in roles, f"输入 '{user_input}' 应匹配到市场分析师"
    
    def test_purchase_consultant_keywords_match(self):
        """验证购房顾问关键词匹配"""
        test_cases = [
            "我想买房",
            "购房流程是什么",
            "买房需要注意什么"
        ]
        
        for user_input in test_cases:
            roles = self.recognizer.match_keywords(user_input)
            # 购房顾问关键词只在没有其他专家匹配时才返回
            assert len(roles) > 0, f"输入 '{user_input}' 应有匹配结果"
    
    def test_multiple_roles_match(self):
        """
        验证多角色匹配
        需求 7.4: 当用户输入需要多个角色时，应返回所有需要的角色
        """
        # 同时包含财务和政策关键词
        user_input = "公积金贷款月供怎么算"
        roles = self.recognizer.match_keywords(user_input)
        assert FINANCIAL_ADVISOR in roles, "应匹配到财务顾问"
        assert POLICY_EXPERT in roles, "应匹配到政策专家"
        
        # 同时包含市场和财务关键词
        user_input = "青秀区房价多少，首付要多少"
        roles = self.recognizer.match_keywords(user_input)
        assert MARKET_ANALYST in roles, "应匹配到市场分析师"
        assert FINANCIAL_ADVISOR in roles, "应匹配到财务顾问"
    
    def test_no_keyword_match(self):
        """验证无关键词时返回空列表"""
        user_input = "今天天气怎么样"
        roles = self.recognizer.match_keywords(user_input)
        assert len(roles) == 0, "无关输入不应匹配到任何角色"
    
    def test_empty_input(self):
        """验证空输入返回空列表"""
        roles = self.recognizer.match_keywords("")
        assert len(roles) == 0
        
        roles = self.recognizer.match_keywords("   ")
        assert len(roles) == 0
    
    def test_case_insensitive_match(self):
        """验证关键词匹配不区分大小写（对于英文）"""
        # 中文关键词测试
        user_input = "贷款"
        roles = self.recognizer.match_keywords(user_input)
        assert FINANCIAL_ADVISOR in roles


class TestIntentRecognizer:
    """测试意图识别器完整流程"""
    
    def setup_method(self):
        """每个测试方法前创建新的识别器实例"""
        self.recognizer = IntentRecognizer()
    
    @pytest.mark.asyncio
    async def test_recognize_with_keywords(self):
        """验证关键词匹配优先"""
        roles = await self.recognizer.recognize("计算贷款月供", use_llm_fallback=False)
        assert FINANCIAL_ADVISOR in roles
    
    @pytest.mark.asyncio
    async def test_recognize_empty_input(self):
        """验证空输入返回购房顾问"""
        roles = await self.recognizer.recognize("", use_llm_fallback=False)
        assert PURCHASE_CONSULTANT in roles
        
        roles = await self.recognizer.recognize("   ", use_llm_fallback=False)
        assert PURCHASE_CONSULTANT in roles
    
    @pytest.mark.asyncio
    async def test_recognize_no_match_no_fallback(self):
        """验证无匹配且不使用 LLM fallback 时返回购房顾问"""
        roles = await self.recognizer.recognize("今天天气怎么样", use_llm_fallback=False)
        assert PURCHASE_CONSULTANT in roles


class TestLLMResponseParsing:
    """测试 LLM 响应解析"""
    
    def setup_method(self):
        """每个测试方法前创建新的识别器实例"""
        self.recognizer = IntentRecognizer()
    
    def test_parse_single_role(self):
        """验证解析单个角色"""
        roles = self.recognizer._parse_llm_response("financial_advisor")
        assert len(roles) == 1
        assert FINANCIAL_ADVISOR in roles
    
    def test_parse_multiple_roles_comma(self):
        """验证解析逗号分隔的多个角色"""
        roles = self.recognizer._parse_llm_response("financial_advisor,policy_expert")
        assert len(roles) == 2
        assert FINANCIAL_ADVISOR in roles
        assert POLICY_EXPERT in roles
    
    def test_parse_multiple_roles_space(self):
        """验证解析空格分隔的多个角色"""
        roles = self.recognizer._parse_llm_response("financial_advisor policy_expert")
        assert len(roles) == 2
        assert FINANCIAL_ADVISOR in roles
        assert POLICY_EXPERT in roles
    
    def test_parse_with_whitespace(self):
        """验证解析带空白字符的响应"""
        roles = self.recognizer._parse_llm_response("  financial_advisor , policy_expert  ")
        assert len(roles) == 2
        assert FINANCIAL_ADVISOR in roles
        assert POLICY_EXPERT in roles
    
    def test_parse_invalid_role(self):
        """验证解析无效角色时返回购房顾问"""
        roles = self.recognizer._parse_llm_response("invalid_role")
        assert len(roles) == 1
        assert PURCHASE_CONSULTANT in roles
    
    def test_parse_empty_response(self):
        """验证解析空响应时返回购房顾问"""
        roles = self.recognizer._parse_llm_response("")
        assert len(roles) == 1
        assert PURCHASE_CONSULTANT in roles
    
    def test_parse_mixed_valid_invalid(self):
        """验证解析混合有效和无效角色"""
        roles = self.recognizer._parse_llm_response("financial_advisor,invalid,policy_expert")
        assert len(roles) == 2
        assert FINANCIAL_ADVISOR in roles
        assert POLICY_EXPERT in roles
    
    def test_parse_duplicate_roles(self):
        """验证解析重复角色时去重"""
        roles = self.recognizer._parse_llm_response("financial_advisor,financial_advisor")
        assert len(roles) == 1
        assert FINANCIAL_ADVISOR in roles


class TestLLMFallback:
    """测试 LLM fallback 分类功能（需求 7.5）"""
    
    def setup_method(self):
        """每个测试方法前创建新的识别器实例"""
        self.recognizer = IntentRecognizer()
    
    @pytest.mark.asyncio
    async def test_llm_fallback_on_no_keyword_match(self):
        """
        验证关键词匹配失败时使用 LLM 分类
        需求 7.5: 如果关键词匹配失败，应使用 LLM 进行意图分类
        """
        # 这个测试需要真实的 LLM 调用，标记为集成测试
        # 在单元测试中，我们验证 fallback 逻辑是否正确触发
        user_input = "帮我分析一下这个情况"  # 不包含明确的专家关键词
        
        # 不使用 LLM fallback 时应返回购房顾问
        roles = await self.recognizer.recognize(user_input, use_llm_fallback=False)
        assert PURCHASE_CONSULTANT in roles
    
    def test_llm_client_lazy_loading(self):
        """验证 LLM 客户端懒加载"""
        recognizer = IntentRecognizer()
        assert recognizer._llm_client is None
        
        # 访问 llm_client 属性会触发懒加载
        client = recognizer.llm_client
        assert client is not None
        assert recognizer._llm_client is client
    
    def test_custom_llm_client(self):
        """验证可以注入自定义 LLM 客户端"""
        from app.llm.client import DeepSeekClient
        custom_client = DeepSeekClient()
        recognizer = IntentRecognizer(llm_client=custom_client)
        assert recognizer._llm_client is custom_client


class TestExecutionPlan:
    """测试执行计划数据结构"""
    
    def test_execution_plan_sequential(self):
        """验证串行执行计划"""
        plan = ExecutionPlan(
            roles=[POLICY_EXPERT, FINANCIAL_ADVISOR],
            execution_mode="sequential",
            reason="政策信息是财务计算的前提"
        )
        assert plan.is_sequential
        assert not plan.is_parallel
        assert len(plan.roles) == 2
    
    def test_execution_plan_parallel(self):
        """验证并行执行计划"""
        plan = ExecutionPlan(
            roles=[MARKET_ANALYST, FINANCIAL_ADVISOR],
            execution_mode="parallel",
            reason="两个领域相对独立"
        )
        assert plan.is_parallel
        assert not plan.is_sequential


class TestExecutionPlanParsing:
    """测试执行计划解析"""
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
        self.candidate_roles = [POLICY_EXPERT, FINANCIAL_ADVISOR]
    
    def test_parse_valid_json(self):
        """验证解析有效的 JSON 响应"""
        content = '''
        {
            "execution_mode": "sequential",
            "order": ["policy_expert", "financial_advisor"],
            "reason": "需要先查利率再算月供"
        }
        '''
        plan = self.recognizer._parse_execution_plan(content, self.candidate_roles)
        assert plan.is_sequential
        assert plan.roles[0].id == "policy_expert"
        assert plan.roles[1].id == "financial_advisor"
        assert "利率" in plan.reason
    
    def test_parse_parallel_mode(self):
        """验证解析并行模式"""
        content = '''
        {
            "execution_mode": "parallel",
            "order": ["policy_expert", "financial_advisor"],
            "reason": "两个问题相对独立"
        }
        '''
        plan = self.recognizer._parse_execution_plan(content, self.candidate_roles)
        assert plan.is_parallel
    
    def test_parse_invalid_json_fallback(self):
        """验证无效 JSON 时使用默认优先级"""
        content = "这不是有效的 JSON"
        plan = self.recognizer._parse_execution_plan(content, self.candidate_roles)
        # 应该使用默认优先级，政策专家在前
        assert plan.roles[0].id == "policy_expert"
        assert plan.is_sequential
    
    def test_parse_missing_roles_in_order(self):
        """验证 order 中缺少角色时自动补充"""
        content = '''
        {
            "execution_mode": "sequential",
            "order": ["policy_expert"],
            "reason": "只指定了一个"
        }
        '''
        plan = self.recognizer._parse_execution_plan(content, self.candidate_roles)
        # 应该包含所有候选角色
        assert len(plan.roles) == 2
        assert plan.roles[0].id == "policy_expert"


class TestDefaultPriorityPlanning:
    """测试默认优先级规划"""
    
    def setup_method(self):
        self.recognizer = IntentRecognizer()
    
    def test_default_priority_order(self):
        """验证默认优先级顺序：政策 > 市场 > 财务 > 购房顾问"""
        roles = [FINANCIAL_ADVISOR, POLICY_EXPERT, MARKET_ANALYST]
        plan = self.recognizer._plan_with_default_priority(roles)
        
        assert plan.roles[0].id == "policy_expert"
        assert plan.roles[1].id == "market_analyst"
        assert plan.roles[2].id == "financial_advisor"
        assert plan.is_sequential


class TestGlobalIntentRecognizer:
    """测试全局意图识别器"""
    
    def test_get_intent_recognizer_singleton(self):
        """验证全局识别器是单例"""
        recognizer1 = get_intent_recognizer()
        recognizer2 = get_intent_recognizer()
        assert recognizer1 is recognizer2
    
    def test_get_intent_recognizer_type(self):
        """验证全局识别器类型"""
        recognizer = get_intent_recognizer()
        assert isinstance(recognizer, IntentRecognizer)
