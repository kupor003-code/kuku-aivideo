"""视频生成Agent"""
from typing import Dict, List, Optional
from app.agents.base import BaseAgent
from app.services.alibaba_video_service import get_alibaba_video_service


class VideoAgent(BaseAgent):
    """
    视频生成Agent

    职责：
    - 文生视频
    - 图生视频
    - 视频管理
    - 多风格生成
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "video"
        self.name = "视频制作师"
        self.description = "生成和管理AI视频"

        # 系统提示词
        self.SYSTEM_PROMPT = """# 角色定义
你是一位专业的视频制作师，精通AI视频生成。你的职责是根据用户的需求和分镜照片，生成高质量的AI视频。

# 核心能力
1. **理解创意** - 准确理解用户的视频创意和情感表达
2. **画面分析** - 分析分镜照片的构图、光线、色彩
3. **视频策划** - 提供专业的视频制作建议
4. **提示词优化** - 生成适合AI视频生成的提示词

# 视频生成要点
- 描述画面运动轨迹（平移/缩放/旋转）
- 控制运动速度和节奏
- 保持画面连贯性和流畅度
- 突出情感和氛围
- 控制在100字以内

# 回复风格
- 专业但友好
- 直接给出建议
- 提供具体可操作的提示词

请根据用户需求，提供专业的视频制作建议。"""

        self.video_service = get_alibaba_video_service()

    async def chat(self, message: str, context: Dict) -> str:
        """
        处理对话消息

        Args:
            message: 用户消息
            context: 对话上下文

        Returns:
            Agent回复
        """
        # 简单的关键词匹配回复
        if "生成" in message or "视频" in message:
            return """我可以帮你生成AI视频！请告诉我：

1. **视频风格** - 想要什么风格？（电影感/动漫/写实/艺术）
2. **画面运动** - 画面如何运动？（推拉摇移/静止/旋转）
3. **时长需求** - 需要多长？（5秒/10秒/更长）
4. **参考图片** - 有分镜照片作为参考吗？

或者直接描述你的想法，我来帮你优化成视频提示词！"""

        elif "建议" in message or "怎么" in message:
            return """视频生成的关键建议：

**画面运动**：
- 平移：展现广阔场景
- 推近：突出细节情感
- 旋转：增强戏剧效果
- 缩放：引导视觉焦点

**节奏控制**：
- 缓慢运动：优雅、宁静
- 快速运动：紧张、刺激
- 静止画面：专注、稳定

**提示词结构**：
主体 + 场景 + 运动方式 + 风格 + 情感

有什么具体需求吗？"""

        else:
            return """你好！我是视频制作师Agent。我可以帮你：

1. 🎬 **生成视频** - 根据创意生成AI视频
2. 🖼️ **图生视频** - 将分镜照片转为动态视频
3. 🎨 **优化效果** - 调整视频风格和参数
4. 💡 **提供建议** - 视频制作专业建议

你想做什么？"""

    async def suggest(self, context: Dict) -> List[str]:
        """
        基于上下文提供建议

        Args:
            context: 对话上下文

        Returns:
            建议列表
        """
        return [
            "🎬 文生视频",
            "🖼️ 图生视频",
            "🎨 调整视频风格",
            "💡 获取制作建议",
        ]

    async def generate_video(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: int = 5,
        fps: int = 30,
    ) -> Dict:
        """
        生成视频

        Args:
            prompt: 提示词
            image_url: 起始图片URL（可选）
            duration: 视频时长
            fps: 帧率

        Returns:
            任务信息
        """
        try:
            result = await self.video_service.generate_video(
                prompt=prompt,
                image_url=image_url,
                duration=duration,
                fps=fps,
            )
            return result
        except Exception as e:
            raise Exception(f"生成视频失败: {str(e)}")

    async def regenerate(
        self,
        original_prompt: str,
        variations: int = 3,
        style_change: str = "slight",
    ) -> List[Dict]:
        """
        重新生成变体

        Args:
            original_prompt: 原始提示词
            variations: 变体数量
            style_change: 风格变化程度

        Returns:
            多个任务信息
        """
        # 根据风格变化调整提示词
        style_modifiers = {
            "slight": ["运动更缓慢", "节奏更柔和", "镜头稍作调整"],
            "medium": ["不同的运动方式", "改变镜头角度", "调整运动速度"],
            "heavy": ["完全不同的风格", "改变运动轨迹", "重新设计镜头"],
        }

        modifiers = style_modifiers.get(style_change, style_modifiers["slight"])

        tasks = []
        for i in range(variations):
            # 添加风格修饰
            modified_prompt = f"{original_prompt}，{modifiers[i % len(modifiers)]}"

            try:
                task = await self.generate_video(
                    prompt=modified_prompt,
                    duration=5,
                )
                tasks.append(task)
            except Exception as e:
                print(f"生成变体{i+1}失败: {str(e)}")

        return tasks

    async def optimize_prompt(self, original_prompt: str, focus: str = "motion") -> str:
        """
        优化提示词

        Args:
            original_prompt: 原始提示词
            focus: 优化重点

        Returns:
            优化后的提示词
        """
        enhancements = {
            "motion": [
                "平滑运动",
                "专业镜头语言",
                "电影质感",
                "流畅过渡",
            ],
            "style": [
                "艺术风格",
                "视觉冲击力",
                "精美画面",
                "专业调色",
            ],
            "emotion": [
                "情感丰富",
                "氛围营造",
                "细腻表达",
                "感染力强",
            ],
        }

        selected = enhancements.get(focus, enhancements["motion"])

        # 添加修饰词
        optimized = f"{original_prompt}，{', '.join(selected[:2])}"

        return optimized

    def update_system_prompt(self, new_prompt: str):
        """
        更新系统提示词

        Args:
            new_prompt: 新的系统提示词
        """
        self.SYSTEM_PROMPT = new_prompt
