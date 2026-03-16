"""
Provider 基础接口 - 统一的 Provider 抽象层

这个模块定义了所有 Provider 的基础接口，包括：
- LLM Provider（大语言模型）
- Image Provider（图片生成）
- Video Provider（视频生成）
- File Parser Provider（文件解析）

所有具体 Provider 实现都必须继承这些基类。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ProviderType(str, Enum):
    """Provider 类型"""
    LLM = "llm"
    IMAGE = "image"
    VIDEO = "video"
    FILE_PARSER = "file_parser"


class ProviderStatus(str, Enum):
    """Provider 状态"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


@dataclass
class ProviderConfig:
    """Provider 配置"""
    provider_name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    extra_params: Dict[str, Any] = None

    def __post_init__(self):
        if self.extra_params is None:
            self.extra_params = {}


@dataclass
class ProviderResponse:
    """Provider 响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    provider: Optional[str] = None
    status_code: Optional[int] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseProvider(ABC):
    """Provider 基类"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.provider_name = config.provider_name
        self.status = ProviderStatus.AVAILABLE

    @abstractmethod
    async def initialize(self):
        """初始化 Provider"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass

    @abstractmethod
    async def call(self, *args, **kwargs) -> ProviderResponse:
        """调用 Provider"""
        pass

    def get_config(self) -> ProviderConfig:
        """获取配置"""
        return self.config

    def update_status(self, status: ProviderStatus):
        """更新状态"""
        self.status = status


class LLMProvider(BaseProvider):
    """LLM Provider 基类"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ProviderResponse:
        """
        生成文本

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含生成结果的响应
        """
        pass

    @abstractmethod
    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ProviderResponse:
        """
        基于对话历史生成文本

        Args:
            messages: 对话历史 [{"role": "user", "content": "..."}]
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含生成结果的响应
        """
        pass


class ImageProvider(BaseProvider):
    """Image Provider 基类"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        negative_prompt: Optional[str] = None,
        width: int = 1024,
        height: int = 1024,
        num_images: int = 1,
        **kwargs
    ) -> ProviderResponse:
        """
        生成图片

        Args:
            prompt: 提示词
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度
            num_images: 生成数量
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含图片 URL 的响应
        """
        pass

    @abstractmethod
    async def edit(
        self,
        image_url: str,
        prompt: str,
        mask_url: Optional[str] = None,
        **kwargs
    ) -> ProviderResponse:
        """
        编辑图片

        Args:
            image_url: 原图片 URL
            prompt: 编辑提示词
            mask_url: 蒙版图片 URL
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含编辑后图片 URL 的响应
        """
        pass


class VideoProvider(BaseProvider):
    """Video Provider 基类"""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        image_url: Optional[str] = None,
        duration: float = 3.0,
        aspect_ratio: str = "16:9",
        **kwargs
    ) -> ProviderResponse:
        """
        生成视频

        Args:
            prompt: 提示词
            image_url: 首帧图片 URL（可选）
            duration: 视频时长（秒）
            aspect_ratio: 宽高比
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含视频 URL 的响应
        """
        pass

    @abstractmethod
    async def generate_from_frames(
        self,
        start_frame_url: str,
        end_frame_url: str,
        prompt: str,
        duration: float = 3.0,
        **kwargs
    ) -> ProviderResponse:
        """
        从首尾帧生成视频

        Args:
            start_frame_url: 首帧图片 URL
            end_frame_url: 尾帧图片 URL
            prompt: 提示词
            duration: 视频时长（秒）
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含视频 URL 的响应
        """
        pass


class FileParserProvider(BaseProvider):
    """File Parser Provider 基类"""

    @abstractmethod
    async def parse(
        self,
        file_path: str,
        **kwargs
    ) -> ProviderResponse:
        """
        解析文件

        Args:
            file_path: 文件路径
            **kwargs: 其他参数

        Returns:
            ProviderResponse: 包含解析结果的响应
        """
        pass

    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        返回支持的文件格式列表

        Returns:
            List[str]: 支持的文件格式，如 [".pdf", ".docx", ".txt"]
        """
        pass
