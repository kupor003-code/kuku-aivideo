"""Video Agent - 视频执行Agent"""
from typing import Dict, Any, Optional, List
from app.agents.v2.base_agent import BaseAgentV2, AgentResponse
from app.services.alibaba_video_service import get_alibaba_video_service


class VideoAgent(BaseAgentV2):
    """
    Video Agent - AI视频执行
    负责图生视频、视频生成任务
    """

    def __init__(self):
        super().__init__()
        self.agent_type = "video"
        self.agent_name = "AI视频执行"
        self.description = "负责图生视频、视频生成任务执行"
        self.capabilities = [
            "generate_video_from_image",
            "text_to_video",
            "image_to_video",
            "optimize_video_parameters",
            "track_video_progress",
        ]
        self.video_service = get_alibaba_video_service()

    async def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """验证输入"""
        return "storyboard" in input_data or "image_url" in input_data

    async def process(
        self,
        input_data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> AgentResponse:
        """
        处理分镜，生成视频

        Args:
            input_data: 包含storyboard或image_url
            context: 上下文

        Returns:
            AgentResponse: 视频生成结果
        """
        try:
            # 获取一致性检查结果
            consistency_report = context.get("consistency_report") if context else None

            # 如果一致性检查未通过，给出警告
            if consistency_report and not consistency_report.get("passed", True):
                return AgentResponse(
                    success=False,
                    error="视觉一致性检查未通过，建议先优化分镜",
                    message="⚠️ 为了生成高质量视频，建议先优化分镜的一致性",
                )

            storyboard = input_data.get("storyboard", [])

            # 为每个场景的视频生成任务
            video_tasks = []

            for scene in storyboard:
                shots = scene.get("shots", [])
                scene_number = scene.get("scene_number", 1)

                # 为每个镜头生成视频（这里简化为每个场景生成一个视频）
                for shot in shots:
                    task = await self._create_video_task(shot, scene_number)
                    video_tasks.append(task)

            return AgentResponse(
                success=True,
                data={
                    "video_tasks": video_tasks,
                    "total_videos": len(video_tasks),
                    "estimated_time": f"{len(video_tasks) * 2}分钟",
                },
                message=f"🎬 开始生成{len(video_tasks)}个视频片段",
                next_agent=None,  # 最后一个Agent
            )

        except Exception as e:
            return AgentResponse(
                success=False,
                error=f"视频生成失败: {str(e)}",
                message="抱歉，视频生成遇到了问题",
            )

    async def _create_video_task(
        self,
        shot: Dict[str, Any],
        scene_number: int,
    ) -> Dict[str, Any]:
        """
        创建视频生成任务

        Args:
            shot: 镜头信息
            scene_number: 场景编号

        Returns:
            视频任务信息
        """
        # 获取图片URL（实际应该从分镜图片服务获取）
        image_url = shot.get("image_url", "")

        # 生成提示词
        prompt = shot.get("image_prompt", shot.get("description", ""))

        # 视频参数
        duration = self._parse_duration(shot.get("duration", "3s"))
        fps = shot.get("fps", 30)

        # 调用视频生成服务
        result = await self.video_service.generate_video(
            prompt=prompt,
            image_url=image_url,
            duration=duration,
            fps=fps,
        )

        return {
            "task_id": result.get("task_id"),
            "scene_number": scene_number,
            "shot_number": shot.get("shot_number"),
            "prompt": prompt,
            "duration": duration,
            "fps": fps,
            "status": "generating",
        }

    def _parse_duration(self, duration_str: str) -> int:
        """
        解析时长字符串

        Args:
            duration_str: 时长字符串，如"3s"

        Returns:
            时长（秒）
        """
        try:
            return int(duration_str.replace("s", ""))
        except:
            return 3  # 默认3秒

    async def text_to_video(
        self,
        prompt: str,
        duration: int = 5,
        fps: int = 30,
    ) -> Dict[str, Any]:
        """
        文生视频

        Args:
            prompt: 提示词
            duration: 时长
            fps: 帧率

        Returns:
            视频生成任务
        """
        result = await self.video_service.generate_video(
            prompt=prompt,
            duration=duration,
            fps=fps,
        )

        return {
            "task_id": result.get("task_id"),
            "status": "generating",
            "prompt": prompt,
        }

    async def optimize_video_parameters(
        self,
        video_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        优化视频参数

        Args:
            video_data: 视频数据

        Returns:
            优化后的参数
        """
        return {
            "duration": video_data.get("duration", 5),
            "fps": 30,
            "resolution": "1080p",
            "bitrate": "5Mbps",
            "codec": "H.264",
            "format": "MP4",
        }

    async def track_video_progress(
        self,
        task_id: str,
    ) -> Dict[str, Any]:
        """
        跟踪视频生成进度

        Args:
            task_id: 任务ID

        Returns:
            进度信息
        """
        result = await self.video_service.query_task(task_id)
        return {
            "task_id": task_id,
            "status": result.get("output", {}).get("task_status"),
            "progress": 50,  # 简化实现
            "video_url": result.get("output", {}).get("results", [{}])[0].get("url"),
        }
