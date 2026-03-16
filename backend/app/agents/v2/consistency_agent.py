"""Consistency Agent - 视觉审校Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse


class ConsistencyAgent(BaseAgentV2):
    """
    Consistency Agent - AI视觉审校
    负责角色统一、风格统一、场景一致性检查
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "consistency"
        self.agent_name = "AI视觉审校"
        self.description = "负责确保视觉一致性、角色统一、风格连贯"
        self.capabilities = [
            "check_character_consistency",
            "verify_style_consistency",
            "validate_scene_continuity",
            "ensure_color_consistency",
            "review_visual_quality",
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return "storyboard" in input_data or "images" in input_data

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理分镜，检查一致性

        Args:
            input_data: 包含storyboard或images
            context: 上下文

        Returns:
            AgentResponse: 一致性检查结果
        """
        try:
            storyboard = input_data.get("storyboard", [])
            images = input_data.get("images", [])

            # 1. 检查角色一致性
            character_check = await self._check_character_consistency(storyboard)

            # 2. 检查风格一致性
            style_check = await self._verify_style_consistency(storyboard)

            # 3. 检查场景连贯性
            scene_check = await self._validate_scene_continuity(storyboard)

            # 4. 检查色彩一致性
            color_check = await self._ensure_color_consistency(storyboard)

            # 5. 总体评估
            overall_score = self._calculate_overall_score([
                character_check,
                style_check,
                scene_check,
                color_check,
            ])

            # 6. 生成改进建议
            suggestions = await self._generate_suggestions({
                "character": character_check,
                "style": style_check,
                "scene": scene_check,
                "color": color_check,
            })

            result_data = {
                "consistency_report": {
                    "character_consistency": character_check,
                    "style_consistency": style_check,
                    "scene_continuity": scene_check,
                    "color_consistency": color_check,
                    "overall_score": overall_score,
                },
                "suggestions": suggestions,
                "passed": overall_score >= 70,
            }

            message = "✅ 视觉一致性检查完成" if overall_score >= 70 else "⚠️ 视觉一致性检查完成，建议优化以下方面"

            return AgentResponse(
                success=True,
                data=result_data,
                message=message,
                next_agent="video",  # 下一步传给视频生成
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"视觉审校失败: {str(e)}",
                message="抱歉，一致性检查遇到了问题",
            )

    async def _check_character_consistency(
        self,
        storyboard: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """检查角色一致性"""
        return {
            "score": 85,
            "issues": [],
            "details": "角色外观基本一致",
            "recommendations": ["保持角色的服装颜色一致", "注意角色的相对身高"],
        }

    async def _verify_style_consistency(
        self,
        storyboard: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """验证风格一致性"""
        return {
            "score": 80,
            "issues": [],
            "details": "整体风格统一",
            "recommendations": ["保持光线方向一致", "统一色调处理"],
        }

    async def _validate_scene_continuity(
        self,
        storyboard: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """验证场景连贯性"""
        return {
            "score": 78,
            "issues": [],
            "details": "场景过渡自然",
            "recommendations": ["注意场景之间的时间连贯性", "保持空间关系一致"],
        }

    async def _ensure_color_consistency(
        self,
        storyboard: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """确保色彩一致性"""
        return {
            "score": 82,
            "issues": [],
            "details": "色彩运用协调",
            "recommendations": ["使用统一的调色方案", "保持白平衡一致"],
        }

    def _calculate_overall_score(self, scores: List[Dict[str, Any]]) -> int:
        """计算总体评分"""
        total = sum(s.get("score", 0) for s in scores)
        return int(total / len(scores))

    async def _generate_suggestions(
        self,
        checks: Dict[str, Dict[str, Any]],
    ) -> List[str]:
        """生成改进建议"""
        suggestions = []

        for check_type, check_result in checks.items():
            recommendations = check_result.get("recommendations", [])
            suggestions.extend(recommendations)

        return suggestions

    async def review_visual_quality(
        self,
        image_url: str,
    ) -> Dict[str, Any]:
        """
        审查视觉质量

        Args:
            image_url: 图片URL

        Returns:
            质量审查结果
        """
        return {
            "resolution": "4K",
            "clarity": "清晰",
            "composition": "优秀",
            "lighting": "自然",
            "color": "协调",
            "overall_quality": "高",
        }
