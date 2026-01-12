# 测试工具注册表
import sys
sys.path.insert(0, '.')

from app.agent.tools import tool_registry

print("已注册的工具:")
for tool in tool_registry.get_all():
    print(f"  - {tool.name}: {tool.description[:50]}...")

print(f"\n总计: {len(tool_registry.get_all())} 个工具")

# 检查政策工具是否注册
if tool_registry.exists("search_policy"):
    print("\n✓ search_policy 工具已注册")
else:
    print("\n✗ search_policy 工具未注册")

if tool_registry.exists("search_faq"):
    print("✓ search_faq 工具已注册")
else:
    print("✗ search_faq 工具未注册")
