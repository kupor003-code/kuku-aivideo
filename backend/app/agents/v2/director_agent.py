"""Director Agent - 导演Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse
from app.services.zhipuai_service import get_zhipuai_service


class DirectorAgent(BaseAgentV2):
    """
    Director Agent - AI导演
    负责创意理解、剧情建议、镜头风格
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "director"
        self.agent_name = "AI导演"
        self.description = "负责创意理解、剧情设计、镜头风格指导"
        self.capabilities = [
            "analyze_creative_concept",
            "develop_storyline",
            "suggest_camera_angles",
            "define_visual_style",
            "create_mood_board",
        ]

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return "topic" in input_data or "creative_concept" in input_data

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理创意输入，生成创意概念

        Args:
            input_data: 包含topic或creative_concept
            context: 上下文

        Returns:
            AgentResponse: 创意概念
        """
        try:
            # 获取主题或创意概念
            topic = input_data.get("topic") or input_data.get("creative_concept", "")

            # 使用LLM生成完整的创意概念
            creative_concept = await self._develop_creative_concept_with_llm(topic)

            # 从LLM返回中提取各个部分
            result_data = {
                "creative_concept": creative_concept.get("concept", {}),
                "storyline": creative_concept.get("storyline", {}),
                "visual_style": creative_concept.get("visual_style", {}),
                "camera_suggestions": creative_concept.get("camera_suggestions", []),
            }

            return AgentResponse(
                success=True,
                data=result_data,
                message=f"✨ 我为你设计了一个创意概念：{creative_concept.get('concept', {}).get('title', topic[:20])}",
                next_agent="producer",  # 下一步传给制片
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"导演处理失败: {str(e)}",
                message="抱歉，创意开发遇到了问题",
            )

    async def _develop_creative_concept_with_llm(self, topic: str) -> Dict[str, Any]:
        """
        使用LLM开发创意概念

        Args:
            topic: 用户提供的主题

        Returns:
            完整的创意概念（包含concept, storyline, visual_style等）
        """
        try:
            llm_service = get_zhipuai_service()

            system_prompt = """你是一位经验丰富的AI导演，擅长将用户的简单创意转化为专业的影视制作方案。

你的任务：
1. 理解用户的创意主题
2. 开发完整的创意概念（标题、类型、主题、基调、目标受众）
3. 设计剧情结构（三幕式，包含关键场景）
4. 定义视觉风格（摄影、光线、构图、色调）
5. 建议镜头运用

输出格式（必须是JSON格式）：
{
  "concept": {
    "title": "作品标题",
    "genre": "类型",
    "theme": "主题",
    "mood": "基调",
    "target_audience": "目标受众"
  },
  "storyline": {
    "structure": "结构类型",
    "key_scenes": [
      {"scene": 1, "description": "场景1描述", "duration": "时长"}
    ]
  },
  "visual_style": {
    "cinematography": "摄影风格",
    "lighting": "光线设计",
    "composition": "构图方式",
    "color_grading": "色调风格"
  },
  "camera_suggestions": [
    {"angle": "镜头角度", "purpose": "用途", "example": "示例"}
  ]
}

请只输出JSON，不要有任何其他文字。"""

            user_message = f"""请为以下创意主题设计一个专业的影视制作方案：

主题：{topic}

请提供完整的创意概念、剧情设计、视觉风格建议。"""

            response = await llm_service.chat_with_system_prompt(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8
            )

            # 尝试解析JSON
            import json
            try:
                # 清理可能的markdown标记
                clean_response = response.strip()
                if clean_response.startswith("```json"):
                    clean_response = clean_response[7:]
                if clean_response.startswith("```"):
                    clean_response = clean_response[3:]
                if clean_response.endswith("```"):
                    clean_response = clean_response[:-3]

                result = json.loads(clean_response)
                return result
            except json.JSONDecodeError:
                print(f"LLM返回的不是有效JSON，使用模板方式: {response}")
                # 如果JSON解析失败，使用模板方式
                return await self._fallback_development(topic)

        except Exception as e:
            print(f"LLM调用失败，使用模板方式: {str(e)}")
            # 回退到模板方式
            concept = await self._develop_creative_concept(topic)
            storyline = await self._create_storyline(concept)
            visual_style = await self._define_visual_style(concept)
            camera_suggestions = await self._suggest_camera_angles(concept)

            return {
                "concept": concept,
                "storyline": storyline,
                "visual_style": visual_style,
                "camera_suggestions": camera_suggestions,
            }

    async def _develop_creative_concept(self, topic: str) -> Dict[str, Any]:
        """开发创意概念（模板方式）"""
        concept = {
            "title": f"《{topic[:20]}》",
            "genre": "短片",
            "theme": topic,
            "tone": "温暖治愈",
            "target_audience": "大众",
            "key_elements": self._extract_key_elements(topic),
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1"],
            "mood": "宁静美好",
        }
        return concept

    def _extract_key_elements(self, topic: str) -> List[str]:
        """提取关键元素"""
        # 简化实现
        elements = ["场景", "人物", "情感", "氛围"]
        return elements

    async def _create_storyline(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """创建剧情"""
        storyline = {
            "structure": "三幕式",
            "acts": [
                {
                    "act": 1,
                    "name": "开端",
                    "description": "引入主题，建立氛围",
                    "duration": "20%",
                },
                {
                    "act": 2,
                    "name": "发展",
                    "description": "深入探索，情感递进",
                    "duration": "60%",
                },
                {
                    "act": 3,
                    "name": "结尾",
                    "description": "收束情感，留下余韵",
                    "duration": "20%",
                },
            ],
            "key_scenes": [
                {"scene": 1, "description": "开场镜头", "duration": "5s"},
                {"scene": 2, "description": "主体内容", "duration": "20s"},
                {"scene": 3, "description": "结尾镜头", "duration": "5s"},
            ],
        }
        return storyline

    async def _define_visual_style(self, concept: Dict[str, Any]) -> Dict[str, Any]:
        """定义视觉风格"""
        visual_style = {
            "cinematography": "电影质感",
            "lighting": "自然光 + 柔光",
            "composition": "黄金分割",
            "color_grading": "温暖色调",
            "camera_movement": "缓慢推拉",
            "depth_of_field": "浅景深",
            "aspect_ratio": "16:9",
        }
        return visual_style

    async def _suggest_camera_angles(self, concept: Dict[str, Any]) -> List[Dict[str, Any]]:
        """建议镜头角度"""
        angles = [
            {"angle": "特写", "purpose": "突出情感", "example": "人物表情/物体细节"},
            {"angle": "中景", "purpose": "展示关系", "example": "人物互动/场景关系"},
            {"angle": "远景", "purpose": "营造氛围", "example": "环境全景/空间关系"},
            {"angle": "俯拍", "purpose": "展示全局", "example": "场景布局/人物位置"},
            {"angle": "仰拍", "purpose": "突出主体", "example": "人物威严/物体高大"},
        ]
        return angles
