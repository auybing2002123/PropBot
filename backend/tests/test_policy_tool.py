# 政策检索工具测试脚本
import asyncio
import sys
import pytest
sys.path.insert(0, '.')

from app.agent.tools.policy import get_knowledge_base, SearchPolicyTool, SearchFAQTool

def test_knowledge_base():
    """测试知识库加载"""
    print("=" * 50)
    print("测试知识库加载")
    print("=" * 50)
    
    kb = get_knowledge_base()
    print(f"知识库加载成功")
    print(f"政策文档数量: {len(kb._policies)}")
    print(f"FAQ 数量: {len(kb._faqs)}")
    print(f"指南数量: {len(kb._guides)}")
    print(f"使用向量检索: {kb._use_vector_search}")
    
    # 打印政策文档信息
    print("\n政策文档列表:")
    for p in kb._policies:
        print(f"  - {p['title']} ({p['city']})")
    
    # 验证知识库加载成功
    assert len(kb._policies) > 0, "政策文档未加载"
    assert len(kb._faqs) > 0, "FAQ 未加载"

@pytest.mark.asyncio
async def test_policy_search():
    """测试政策搜索"""
    print("\n" + "=" * 50)
    print("测试政策搜索")
    print("=" * 50)
    
    tool = SearchPolicyTool()
    
    # 测试1: 搜索南宁限购政策
    print("\n测试1: 搜索南宁限购政策")
    result = await tool.execute(query="限购政策", city="南宁")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关: {result['results'][0]['title']}")
        print(f"相关度: {result['results'][0]['relevance']}%")
    
    assert result['success'] is True
    
    # 测试2: 搜索首付比例
    print("\n测试2: 搜索首付比例")
    result = await tool.execute(query="首付比例")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关: {result['results'][0]['title']}")
    
    assert result['success'] is True
    
    # 测试3: 搜索柳州公积金
    print("\n测试3: 搜索柳州公积金")
    result = await tool.execute(query="公积金贷款", city="柳州")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关: {result['results'][0]['title']}")
    
    assert result['success'] is True

@pytest.mark.asyncio
async def test_faq_search():
    """测试 FAQ 搜索"""
    print("\n" + "=" * 50)
    print("测试 FAQ 搜索")
    print("=" * 50)
    
    tool = SearchFAQTool()
    
    # 测试1: 搜索公积金贷款额度
    print("\n测试1: 搜索公积金贷款额度")
    result = await tool.execute(query="公积金贷款额度")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关问题: {result['results'][0]['question']}")
        print(f"答案: {result['results'][0]['answer'][:100]}...")
    
    assert result['success'] is True
    
    # 测试2: 搜索首付
    print("\n测试2: 搜索首付")
    result = await tool.execute(query="首套房首付多少")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关问题: {result['results'][0]['question']}")
    
    assert result['success'] is True
    
    # 测试3: 按城市搜索
    print("\n测试3: 搜索南宁购房资格")
    result = await tool.execute(query="外地人买房", city="南宁")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关问题: {result['results'][0]['question']}")
    
    assert result['success'] is True
    
    # 测试4: 按分类搜索
    print("\n测试4: 按分类搜索贷款问题")
    result = await tool.execute(query="还款", category="贷款")
    print(f"结果数量: {result['count']}")
    if result['results']:
        print(f"最相关问题: {result['results'][0]['question']}")
    
    assert result['success'] is True

async def main():
    """主测试函数"""
    # 测试知识库
    test_knowledge_base()
    
    # 测试政策搜索
    await test_policy_search()
    
    # 测试 FAQ 搜索
    await test_faq_search()
    
    print("\n" + "=" * 50)
    print("所有测试完成!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
