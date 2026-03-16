"""
Script Agent V2 - 剧本创作 Agent

这个 Agent 负责剧本创作和分镜生成，通过整合 video-shot-agent 实现：
1. 文档解析（如果有文档）
2. 剧本创作
3. 镜头拆分
4. 视频分割
5. 提示词生成
6. 质量审计

video-shot-agent 作为一个完整的服务，可以：
- 作为独立服务运行（HTTP API）
- 作为 Python 库导入
- 作为 LangGraph 节点集成

这里我们采用方案二：作为 Python 库导入。
"""

import sys
import os
from typing import Dict, Any, Optional
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse

# 添加 video-shot-agent 到 Python 路径
VIDEO_SHOT_AGENT_PATH = "/Users/kupor/Desktop/ai-video-platform/脚本创作工具/video-shot-agent-main/src"
if VIDEO_SHOT_AGENT_PATH not in sys.path:
    sys.path.insert(0, VIDEO_SHOT_AGENT_PATH)

try:
    from penshot.neopen import generate_storyboard
    from penshot.neopen.shot_config import ShotConfig
    VIDEO_SHOT_AGENT_AVAILABLE = True
except ImportError as e:
    print(f"Warning: video-shot-agent not available: {e}")
    VIDEO_SHOT_AGENT_AVAILABLE = False


class ScriptAgentV2(BaseAgentV2):
    """
    Script Agent V2 - 剧本创作和分镜生成 Agent

    职责：
    - 生成剧本
    - 拆分镜头
    - 生成分镜 prompt
    - 质量审计
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "script"
        self.agent_name = "AI剧本创作"
        self.description = "负责剧本创作、镜头拆分和分镜prompt生成"
        self.capabilities = [
            "generate_script",
            "parse_document",
            "split_shots",
            "generate_prompts",
            "audit_quality",
        ]
        self.video_shot_agent_available = VIDEO_SHOT_AGENT_AVAILABLE

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        action = input_data.get("action")
        inputs = input_data.get("inputs", {})

        if action == "generate_script":
            return "creative_idea" in inputs or "script" in inputs
        elif action == "parse_document":
            return "document" in inputs or "document_path" in inputs
        elif action == "modify_script":
            return "feedback" in inputs

        return False

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理剧本创作任务

        Args:
            input_data: 输入数据
            context: 上下文

        Returns:
            AgentResponse: 处理结果
        """
        try:
            action = input_data.get("action")
            inputs = input_data.get("inputs", {})

            if action == "generate_script":
                if not self.video_shot_agent_available:
                    # video-shot-agent 不可用时，生成脚本后使用模拟分镜
                    return await self._generate_storyboard_mock(inputs, context)
                return await self._generate_script(inputs, context)
            elif action == "generate_storyboard":
                # 当没有 video-shot-agent 时，使用模拟模式
                return await self._generate_storyboard_mock(inputs, context)
            elif action == "parse_document":
                return await self._parse_document(inputs, context)
            elif action == "modify_script":
                return await self._modify_script(inputs, context)
            else:
                return AgentResponse(
                    success=False,
                    error=f"未知的 action: {action}",
                    message="不支持的操作",
                )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"剧本创作失败: {str(e)}",
                message="抱歉，剧本创作过程中出现了问题",
            )

    async def _generate_script(
        self,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        生成剧本和分镜

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            AgentResponse: 生成结果
        """
        creative_idea = inputs.get("creative_idea", "")
        script_text = inputs.get("script", "")

        # 如果没有剧本文本，使用创意 idea
        if not script_text and creative_idea:
            # TODO: 可以先调用 LLM 将创意扩展为剧本
            script_text = creative_idea

        if not script_text:
            return AgentResponse(
                success=False,
                error="缺少剧本输入",
                message="请提供剧本或创意描述",
            )

        # 调用 video-shot-agent 生成分镜
        try:
            result = await generate_storyboard(
                script_text=script_text,
                task_id=context.get("task_id") if context else None,
                config=self._create_shot_config(inputs, context),
            )

            if result.get("success"):
                data = result.get("data", {})
                instructions = data.get("instructions")
                fragments = instructions.fragments if instructions else []

                return AgentResponse(
                    success=True,
                    data={
                        "script": script_text,
                        "fragments": [
                            {
                                "fragment_id": f.fragment_id,
                                "prompt": f.prompt,
                                "negative_prompt": f.negative_prompt,
                                "duration": f.duration,
                                "shot_id": f.shot_id,
                            }
                            for f in fragments
                        ],
                        "metadata": instructions.metadata if instructions else {},
                        "audit_report": data.get("audit_report"),
                        "processing_stats": result.get("processing_stats"),
                    },
                    message=f"成功生成剧本和分镜，共 {len(fragments)} 个片段",
                )
            else:
                return AgentResponse(
                    success=False,
                    error=result.get("error", "Unknown error"),
                    message="剧本生成失败",
                )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"video-shot-agent 调用失败: {str(e)}",
                message="剧本生成过程中出现错误",
            )

    async def _parse_document(
        self,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        解析文档

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            AgentResponse: 解析结果
        """
        # TODO: 实现文档解析
        return AgentResponse(
            success=False,
            error="文档解析功能尚未实现",
            message="请直接提供剧本文本",
        )

    async def _modify_script(
        self,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        修改剧本

        Args:
            inputs: 输入数据（包含反馈）
            context: 上下文

        Returns:
            AgentResponse: 修改结果
        """
        # TODO: 实现剧本修改
        return AgentResponse(
            success=False,
            error="剧本修改功能尚未实现",
            message="请重新生成剧本",
        )

    async def _generate_storyboard_mock(
        self,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> AgentResponse:
        """
        模拟生成分镜脚本（当 video-shot-agent 不可用时使用）

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            AgentResponse: 模拟的分镜数据
        """
        script_text = inputs.get("script", context.get("execution_context", {}).get("script", "")) if context else inputs.get("script", "")

        # 生成模拟的分镜数据
        mock_fragments = [
            {
                "fragment_id": "frag_001",
                "shot_id": "shot_001",
                "prompt": "赛博朋克城市夜景，霓虹灯闪烁，雨中的街道",
                "negative_prompt": "白天，晴天，低质量",
                "duration": 3.0,
            },
            {
                "fragment_id": "frag_002",
                "shot_id": "shot_002",
                "prompt": "主角特写，人工智能眼中的光芒，未来感面容",
                "negative_prompt": "模糊，低分辨率",
                "duration": 2.5,
            },
            {
                "fragment_id": "frag_003",
                "shot_id": "shot_003",
                "prompt": "高科技实验室，全息屏幕显示数据流",
                "negative_prompt": "复古风格，暗淡",
                "duration": 4.0,
            },
        ]

        return AgentResponse(
            success=True,
            data={
                "script": script_text or "模拟剧本内容",
                "fragments": mock_fragments,
                "metadata": {
                    "total_duration": sum(f["duration"] for f in mock_fragments),
                    "shot_count": len(mock_fragments),
                },
                "processing_stats": {
                    "shots_processed": len(mock_fragments),
                    "fragments_generated": len(mock_fragments),
                },
            },
            message=f"✨ 模拟模式：成功生成 {len(mock_fragments)} 个分镜片段（video-shot-agent 未安装）",
        )

    def _create_shot_config(
        self,
        inputs: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Any:
        """
        创建 ShotConfig

        Args:
            inputs: 输入数据
            context: 上下文

        Returns:
            ShotConfig: 配置对象
        """
        # 从 inputs 或 context 中获取配置
        config = ShotConfig()

        # 视频模型
        if "video_model" in inputs:
            config.video_model = inputs["video_model"]

        # 时长配置
        if "max_shot_duration" in inputs:
            config.max_shot_duration = inputs["max_shot_duration"]
        if "min_shot_duration" in inputs:
            config.min_shot_duration = inputs["min_shot_duration"]
        if "max_fragment_duration" in inputs:
            config.max_fragment_duration = inputs["max_fragment_duration"]

        # 连续性检查
        if "enable_continuity_check" in inputs:
            config.enable_continuity_check = inputs["enable_continuity_check"]

        return config
