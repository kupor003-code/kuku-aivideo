"""
工作流端到端测试脚本

这个脚本用于测试整个工作流系统，包括：
1. Orchestrator 意图理解
2. 执行计划生成
3. Agent 调度
4. 工作流执行

使用方法：
    cd backend
    python test_workflow.py
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.v2.orchestrator_agent_v2 import OrchestratorAgentV2
from app.workflows.executor import workflow_executor


async def test_orchestrator():
    """测试 Orchestrator Agent"""
    print("=" * 50)
    print("测试 1: Orchestrator Agent 意图理解")
    print("=" * 50)

    orchestrator = OrchestratorAgentV2()

    # 测试用户输入
    user_input = "我想创作一个关于科幻主题的短剧，风格要像《银翼杀手》"

    print(f"\n用户输入: {user_input}")

    response = await orchestrator.process(
        input_data={
            "user_input": user_input,
            "project_id": "test_project_001",
        },
        context={
            "project_id": "test_project_001",
        },
    )

    print(f"\n✅ 响应成功: {response.success}")
    if response.success:
        print(f"📝 消息: {response.message}")
        print(f"🎯 意图: {response.data.get('intent')}")
        print(f"📋 执行计划:")
        plan = response.data.get('execution_plan')
        print(f"   - 概述: {plan.get('overview')}")
        print(f"   - 步骤数: {len(plan.get('steps', []))}")
        for i, step in enumerate(plan.get('steps', [])):
            print(f"     {i+1}. {step.get('description')} ({step.get('agent')})")
        print(f"⏱️  预计时长: {plan.get('estimated_duration')}")
        print(f"➡️  下一个 Agent: {response.next_agent}")
    else:
        print(f"❌ 错误: {response.error}")

    return response


async def test_workflow_executor(project_id="test_project_002"):
    """测试工作流执行"""
    print("\n" + "=" * 50)
    print("测试 2: 工作流执行")
    print("=" * 50)

    # 创建一个简单的执行计划
    execution_plan = {
        "task_type": "create_video",
        "overview": "测试工作流执行",
        "steps": [
            {
                "order": 1,
                "agent": "script",
                "action": "generate_script",
                "description": "生成剧本和分镜",
                "inputs": {
                    "creative_idea": "一个关于人工智能觉醒的故事",
                },
            },
            # 注意：由于 video-shot-agent 可能需要外部依赖，
            # 这里只测试 Script Agent
        ],
        "estimated_duration": "2-3分钟",
        "requirements": [],
    }

    print(f"\n📋 执行计划: {execution_plan.get('overview')}")
    print(f"🔧 项目ID: {project_id}")

    result = await workflow_executor.execute_plan(
        project_id=project_id,
        execution_plan=execution_plan,
        initial_context={"user_input": "测试输入"},
    )

    print(f"\n✅ 执行成功: {result.get('success')}")

    if result.get('success'):
        execution_state = result.get('execution_state', {})
        print(f"📊 进度: {execution_state.get('progress'):.1f}%")
        print(f"✅ 完成步骤: {len(execution_state.get('completed_steps', []))}")
        print(f"❌ 失败步骤: {len(execution_state.get('failed_steps', []))}")

        # 打印完成步骤的结果
        for step_result in execution_state.get('completed_steps', []):
            step = step_result.get('step')
            result_data = step_result.get('result')
            print(f"\n   ✓ {step.get('description')}")
            if result_data.get('data'):
                data = result_data['data']
                if 'fragments' in data:
                    print(f"     生成了 {len(data['fragments'])} 个片段")
    else:
        print(f"❌ 错误: {result.get('error')}")
        if 'execution_state' in result:
            failed_steps = result['execution_state'].get('failed_steps', [])
            for failed_step in failed_steps:
                print(f"   失败步骤: {failed_step.get('step').get('description')}")
                print(f"   错误: {failed_step.get('error')}")

    return result


async def test_get_status(project_id="test_project_002"):
    """测试获取执行状态"""
    print("\n" + "=" * 50)
    print("测试 3: 获取执行状态")
    print("=" * 50)

    execution_state = workflow_executor.get_execution_state(project_id)

    if execution_state:
        print(f"\n🔧 项目ID: {execution_state.project_id}")
        print(f"📊 进度: {execution_state.progress:.1f}%")
        print(f"✅ 完成: {execution_state.is_completed}")
        print(f"❌ 失败: {execution_state.is_failed}")
        print(f"📈 当前步骤: {execution_state.current_step}")
        print(f"✓ 完成步骤数: {len(execution_state.completed_steps)}")
        print(f"✗ 失败步骤数: {len(execution_state.failed_steps)}")
    else:
        print(f"\n❌ 未找到执行记录: {project_id}")


async def main():
    """主测试函数"""
    print("\n🚀 开始工作流端到端测试\n")

    try:
        # 测试 1: Orchestrator Agent
        orchestrator_result = await test_orchestrator()

        # 测试 2: 工作流执行
        workflow_result = await test_workflow_executor()

        # 测试 3: 获取状态
        await test_get_status()

        print("\n" + "=" * 50)
        print("✅ 测试完成")
        print("=" * 50)

        # 总结
        print("\n📊 测试总结:")
        print(f"  - Orchestrator: {'✅ 通过' if orchestrator_result.success else '❌ 失败'}")
        print(f"  - Workflow 执行: {'✅ 通过' if workflow_result.get('success') else '❌ 失败'}")

    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
