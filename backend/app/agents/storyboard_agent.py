"""分镜生成Agent"""
from typing import Dict, List, Optional
from app.agents.base import BaseAgent
from app.services.alibaba_image_service import get_alibaba_image_service
from app.services.mock_image_service import get_mock_image_service
from app.core.config import settings


class StoryboardAgent(BaseAgent):
    """
    分镜生成Agent

    职责：
    - 文生图
    - 图片管理
    - 多风格生成
    - 图片重新生成
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "storyboard"
        self.name = "分镜摄影师"
        self.description = "生成和管理分镜照片"

        # 系统提示词（可以随时修改）
        self.SYSTEM_PROMPT = """# 角色定义
你是一位专业的分镜摄影师，精通AI图片生成。你的职责是根据用户的创意需求，生成高质量的静态分镜照片。

# 核心能力
1. **理解创意** - 准确理解用户的视频创意
2. **构图建议** - 提供专业的构图建议
3. **提示词生成** - 生成适合AI图片生成的提示词
4. **风格优化** - 根据需求调整风格

# 分镜照片提示词要点
- 强调画面构图、光线、色彩、氛围
- 描述静态场景和人物姿态
- 突出视觉细节和质感
- 控制在100字以内
- 避免描述动态和动作（这是静态图片）

# 回复风格
- 专业但友好
- 直接给出建议
- 提供具体可操作的提示词

请根据用户需求，提供专业的分镜照片提示词。"""

        # 根据API Key配置选择服务
        # 如果没有配置DashScope API Key，使用模拟服务
        if settings.DASHSCOPE_API_KEY and settings.DASHSCOPE_API_KEY != "your-dashscope-api-key":
            self.image_service = get_alibaba_image_service()
            self.mock_mode = False
        else:
            self.image_service = get_mock_image_service()
            self.mock_mode = True
            print("⚠️  使用模拟图片服务（需配置DASHSCOPE_API_KEY以使用真实AI生成）")

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
        if "生成" in message or "提示词" in message:
            return """我可以帮你生成分镜照片！请告诉我：

1. **场景描述** - 什么样的场景？（咖啡厅/海滩/办公室等）
2. **光线氛围** - 想要什么样的光线？（清晨阳光/夕阳/室内灯光）
3. **色彩风格** - 暖色调/冷色调/黑白？
4. **构图角度** - 正面/侧面/俯视？

或者你可以直接描述你的想法，我来帮你优化成提示词！"""

        elif "建议" in message or "怎么" in message:
            return """分镜照片是视频创作的重要参考！我的建议：

**构图建议**：
- 使用三分法则让画面更有平衡感
- 选择合适的光线方向（侧光/逆光/顶光）
- 留白不要太多，也不要太满

**风格建议**：
- 咖啡厅：暖色调、柔和光线
- 科技产品：冷色调、简洁构图
- 情感故事：自然光、真实感

**提示词结构**：
主体 + 环境 + 光线 + 色彩 + 氛围

有什么具体需求吗？"""

        else:
            return """你好！我是分镜摄影师Agent。我可以帮你：

1. 📸 **生成图片** - 根据你的创意生成分镜照片
2. 🎨 **优化提示词** - 让图片效果更好
3. 🔄 **重新生成** - 调整参数重新生成
4. 💡 **提供建议** - 构图、光线、风格建议

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
            "📸 生成单张图片",
            "🖼️ 批量生成多张",
            "🎨 调整风格重新生成",
            "💡 获取构图建议",
        ]

    async def generate_images(
        self,
        prompt: str,
        size: str = "1024*1024",
        n: int = 1,
        seed: Optional[int] = None,
    ) -> Dict:
        """
        生成图片

        Args:
            prompt: 提示词
            size: 图片尺寸
            n: 生成数量
            seed: 随机种子

        Returns:
            任务信息
        """
        try:
            result = await self.image_service.generate_image(
                prompt=prompt,
                size=size,
                n=n,
                seed=seed,
            )
            return result
        except Exception as e:
            raise Exception(f"生成图片失败: {str(e)}")

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
            style_change: 风格变化程度 (slight/medium/heavy)

        Returns:
            多个任务信息
        """
        # 根据风格变化调整提示词
        style_modifiers = {
            "slight": ["色调更温暖", "光线更柔和", "构图稍作调整"],
            "medium": ["不同的构图角度", "改变光线方向", "调整色彩饱和度"],
            "heavy": ["完全不同的风格", "改变场景氛围", "重新构图"],
        }

        modifiers = style_modifiers.get(style_change, style_modifiers["slight"])

        tasks = []
        for i in range(variations):
            # 添加风格修饰
            modified_prompt = f"{original_prompt}，{modifiers[i % len(modifiers)]}"

            try:
                task = await self.generate_images(
                    prompt=modified_prompt,
                    n=1,
                )
                tasks.append(task)
            except Exception as e:
                print(f"生成变体{i+1}失败: {str(e)}")

        return tasks

    async def optimize_prompt(self, original_prompt: str, focus: str = "quality") -> str:
        """
        优化提示词

        Args:
            original_prompt: 原始提示词
            focus: 优化重点 (quality/style/composition)

        Returns:
            优化后的提示词
        """
        enhancements = {
            "quality": [
                "高清画质",
                "细节丰富",
                "专业摄影",
                "8K分辨率",
            ],
            "style": [
                "电影级调色",
                "艺术风格",
                "精心构图",
                "视觉冲击力",
            ],
            "composition": [
                "黄金分割构图",
                "景深效果",
                "完美光线",
                "平衡布局",
            ],
        }

        selected = enhancements.get(focus, enhancements["quality"])

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
