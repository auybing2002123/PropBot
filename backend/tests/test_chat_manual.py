"""
手动测试对话 API
使用 httpx 处理 SSE 流式响应
"""
import httpx
import json
import asyncio
import sys

BASE_URL = "http://localhost:8080/api/v1"


async def test_chat(message: str, session_id: str = "test-session"):
    """测试对话接口"""
    print(f"\n{'='*60}")
    print(f"测试消息: {message}")
    print(f"{'='*60}")
    
    payload = {
        "session_id": session_id,
        "message": message,
        "mode": "standard"
    }
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            async with client.stream(
                "POST",
                f"{BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                print(f"状态码: {response.status_code}")
                print(f"响应头: {dict(response.headers)}")
                print("\n--- 流式响应 ---\n")
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # 去掉 "data: " 前缀
                        try:
                            event = json.loads(data)
                            event_type = event.get("type", "unknown")
                            
                            if event_type == "conversation_created":
                                print(f"[对话创建] ID: {event.get('conversation_id')}")
                            elif event_type == "role_start":
                                print(f"\n[角色开始] {event.get('icon', '')} {event.get('name', '')} ({event.get('role', '')})")
                            elif event_type == "role_result":
                                print(f"\n[角色结果] {event.get('role', '')}:")
                                content = event.get("content", "")
                                # 只打印前500字符
                                if len(content) > 500:
                                    print(content[:500] + "...(截断)")
                                else:
                                    print(content)
                            elif event_type == "tool_call":
                                print(f"[工具调用] {event.get('tool', '')} - {event.get('args', {})}")
                            elif event_type == "tool_result":
                                print(f"[工具结果] {event.get('tool', '')} - 成功")
                            elif event_type == "error":
                                print(f"[错误] {event.get('code', '')}: {event.get('message', '')}")
                            elif event_type == "done":
                                print("\n[完成]")
                            else:
                                print(f"[{event_type}] {event}")
                        except json.JSONDecodeError:
                            print(f"无法解析: {data}")
                            
        print("\n✅ 测试通过")
        return True
        
    except httpx.TimeoutException:
        print("\n❌ 请求超时")
        return False
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False


async def main():
    """运行测试"""
    # 测试用例
    test_cases = [
        ("南宁现在还限购吗？", "test-policy"),
        ("我想在南宁买一套150万的房子，首套房，月收入1.5万，能负担得起吗？", "test-finance"),
        ("青秀区和良庆区哪个更值得买？", "test-market"),
    ]
    
    # 如果有命令行参数，只测试指定的消息
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
        await test_chat(message)
    else:
        # 运行所有测试
        results = []
        for message, session_id in test_cases:
            result = await test_chat(message, session_id)
            results.append((message[:20], result))
            await asyncio.sleep(1)  # 避免请求过快
        
        # 打印汇总
        print("\n" + "="*60)
        print("测试汇总:")
        print("="*60)
        for msg, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  {msg}... {status}")


if __name__ == "__main__":
    asyncio.run(main())
