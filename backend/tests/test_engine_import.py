# 测试 engine 模块导入
import sys
sys.path.insert(0, '.')

try:
    from app.agent.engine import AgentEngine
    print("AgentEngine 导入成功")
except Exception as e:
    print(f"导入失败: {e}")
    import traceback
    traceback.print_exc()
