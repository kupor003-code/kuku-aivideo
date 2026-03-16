"""
Provider 管理器 - 统一管理所有 Provider 实例

这个模块负责：
1. Provider 的注册和初始化
2. Provider 的获取和切换
3. Provider 的健康检查
4. Provider 的错误处理和重试
"""

from typing import Dict, Type, Optional, List
from app.providers.base import (
    BaseProvider,
    LLMProvider,
    ImageProvider,
    VideoProvider,
    FileParserProvider,
    ProviderConfig,
    ProviderType,
    ProviderStatus,
)


class ProviderManager:
    """
    Provider 管理器

    单例模式，统一管理所有 Provider 实例
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # Provider 注册表 {provider_name: provider_class}
        self._provider_registry: Dict[str, Type[BaseProvider]] = {}

        # Provider 实例 {provider_name: provider_instance}
        self._providers: Dict[str, BaseProvider] = {}

        # 按类型分类的 Provider {provider_type: [provider_names]}
        self._providers_by_type: Dict[ProviderType, List[str]] = {
            ProviderType.LLM: [],
            ProviderType.IMAGE: [],
            ProviderType.VIDEO: [],
            ProviderType.FILE_PARSER: [],
        }

        # 默认 Provider {provider_type: provider_name}
        self._default_providers: Dict[ProviderType, Optional[str]] = {
            ProviderType.LLM: None,
            ProviderType.IMAGE: None,
            ProviderType.VIDEO: None,
            ProviderType.FILE_PARSER: None,
        }

    def register_provider(
        self,
        provider_name: str,
        provider_class: Type[BaseProvider],
        provider_type: ProviderType,
        is_default: bool = False,
    ):
        """
        注册 Provider

        Args:
            provider_name: Provider 名称
            provider_class: Provider 类
            provider_type: Provider 类型
            is_default: 是否设为默认
        """
        self._provider_registry[provider_name] = provider_class
        self._providers_by_type[provider_type].append(provider_name)

        if is_default or self._default_providers[provider_type] is None:
            self._default_providers[provider_type] = provider_name

    async def initialize_provider(
        self,
        provider_name: str,
        config: ProviderConfig,
    ) -> BaseProvider:
        """
        初始化 Provider

        Args:
            provider_name: Provider 名称
            config: Provider 配置

        Returns:
            BaseProvider: Provider 实例
        """
        if provider_name not in self._provider_registry:
            raise ValueError(f"Provider {provider_name} not registered")

        provider_class = self._provider_registry[provider_name]
        provider = provider_class(config)

        await provider.initialize()
        self._providers[provider_name] = provider

        return provider

    def get_provider(self, provider_name: str) -> Optional[BaseProvider]:
        """
        获取 Provider 实例

        Args:
            provider_name: Provider 名称

        Returns:
            BaseProvider: Provider 实例，如果不存在返回 None
        """
        return self._providers.get(provider_name)

    def get_provider_by_type(
        self,
        provider_type: ProviderType,
        provider_name: Optional[str] = None,
    ) -> Optional[BaseProvider]:
        """
        根据类型获取 Provider

        Args:
            provider_type: Provider 类型
            provider_name: Provider 名称（可选，不指定则使用默认）

        Returns:
            BaseProvider: Provider 实例
        """
        if provider_name:
            return self.get_provider(provider_name)

        # 使用默认 Provider
        default_name = self._default_providers.get(provider_type)
        if default_name:
            return self.get_provider(default_name)

        # 如果没有默认，返回该类型的第一个
        providers = self._providers_by_type.get(provider_type, [])
        if providers:
            return self.get_provider(providers[0])

        return None

    def set_default_provider(self, provider_type: ProviderType, provider_name: str):
        """
        设置默认 Provider

        Args:
            provider_type: Provider 类型
            provider_name: Provider 名称
        """
        if provider_name not in self._provider_registry:
            raise ValueError(f"Provider {provider_name} not registered")

        if provider_name not in self._providers_by_type.get(provider_type, []):
            raise ValueError(f"Provider {provider_name} is not of type {provider_type}")

        self._default_providers[provider_type] = provider_name

    async def health_check(self, provider_name: str) -> bool:
        """
        健康检查

        Args:
            provider_name: Provider 名称

        Returns:
            bool: 是否健康
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return False

        return await provider.health_check()

    async def health_check_all(self) -> Dict[str, bool]:
        """
        检查所有 Provider 的健康状态

        Returns:
            Dict[str, bool]: {provider_name: is_healthy}
        """
        results = {}
        for provider_name in self._providers:
            results[provider_name] = await self.health_check(provider_name)
        return results

    def list_providers(self, provider_type: Optional[ProviderType] = None) -> List[str]:
        """
        列出所有 Provider

        Args:
            provider_type: Provider 类型（可选）

        Returns:
            List[str]: Provider 名称列表
        """
        if provider_type:
            return self._providers_by_type.get(provider_type, [])

        return list(self._providers.keys())

    def get_provider_status(self, provider_name: str) -> Optional[ProviderStatus]:
        """
        获取 Provider 状态

        Args:
            provider_name: Provider 名称

        Returns:
            ProviderStatus: Provider 状态
        """
        provider = self.get_provider(provider_name)
        if provider:
            return provider.status
        return None


# 全局单例
provider_manager = ProviderManager()
