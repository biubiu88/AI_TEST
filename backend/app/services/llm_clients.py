"""
LLM 客户端工厂模式实现

采用工厂模式管理不同的 LLM 服务商：
- OpenAI SDK: 用于 OpenAI 官方服务
- HTTPX: 用于其他兼容 OpenAI API 的服务（如通义千问、智谱、Moonshot、DeepSeek 等）
"""
import json
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    usage: Optional[Dict[str, int]] = None
    raw_response: Optional[Any] = None


class BaseLLMClient(ABC):
    """
    LLM 客户端抽象基类
    定义统一的调用接口
    """
    
    def __init__(self, api_key: str, api_base: str, model: str, **kwargs):
        """
        初始化客户端
        
        Args:
            api_key: API 密钥
            api_base: API 基础 URL
            model: 模型名称
            **kwargs: 其他参数
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.extra_params = kwargs
    
    @abstractmethod
    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> ChatResponse:
        """
        聊天补全接口
        
        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大 token 数
            **kwargs: 其他参数
        
        Returns:
            ChatResponse 对象
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """检查客户端是否可用"""
        pass


class OpenAIClient(BaseLLMClient):
    """
    OpenAI SDK 客户端
    用于 OpenAI 官方服务
    """
    
    def __init__(self, api_key: str, api_base: str, model: str, **kwargs):
        super().__init__(api_key, api_base, model, **kwargs)
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 OpenAI SDK 客户端"""
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.api_base
            )
        except ImportError:
            self.client = None
    
    def is_available(self) -> bool:
        """检查 OpenAI SDK 是否可用"""
        return self.client is not None and bool(self.api_key)
    
    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> ChatResponse:
        """使用 OpenAI SDK 进行聊天补全"""
        if not self.is_available():
            raise RuntimeError("OpenAI SDK 不可用或未配置 API Key")
        
        # 转换消息格式
        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=api_messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )
        
        # 提取响应内容
        content = response.choices[0].message.content.strip()
        usage = None
        if response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        
        return ChatResponse(
            content=content,
            model=response.model,
            usage=usage,
            raw_response=response
        )


class HTTPXClient(BaseLLMClient):
    """
    HTTPX 客户端
    用于其他兼容 OpenAI API 格式的服务
    如：通义千问、智谱AI、Moonshot、DeepSeek、Ollama 等
    """
    
    def __init__(self, api_key: str, api_base: str, model: str, **kwargs):
        super().__init__(api_key, api_base, model, **kwargs)
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """初始化 HTTPX 客户端"""
        try:
            import httpx
            # 设置较长的超时时间，因为 LLM 响应可能较慢
            timeout = self.extra_params.get('timeout', 120.0)
            self.client = httpx.Client(timeout=timeout)
        except ImportError:
            self.client = None
    
    def is_available(self) -> bool:
        """检查 HTTPX 是否可用"""
        return self.client is not None and bool(self.api_key)
    
    def _get_chat_endpoint(self) -> str:
        """获取聊天补全 API 端点"""
        base = self.api_base.rstrip('/')
        # 确保 URL 包含完整的路径
        if not base.endswith('/chat/completions'):
            if base.endswith('/v1'):
                return f"{base}/chat/completions"
            else:
                return f"{base}/v1/chat/completions"
        return base
    
    def chat(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        **kwargs
    ) -> ChatResponse:
        """使用 HTTPX 进行聊天补全"""
        if not self.is_available():
            raise RuntimeError("HTTPX 不可用或未配置 API Key")
        
        # 转换消息格式
        api_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
        
        # 构建请求
        endpoint = self._get_chat_endpoint()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        payload = {
            "model": self.model,
            "messages": api_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        # 合并额外参数
        for key, value in kwargs.items():
            if key not in payload:
                payload[key] = value
        
        # 发送请求
        response = self.client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()
        
        # 解析响应
        result = response.json()
        
        content = result["choices"][0]["message"]["content"].strip()
        usage = result.get("usage")
        
        return ChatResponse(
            content=content,
            model=result.get("model", self.model),
            usage=usage,
            raw_response=result
        )
    
    def __del__(self):
        """清理资源"""
        if self.client:
            try:
                self.client.close()
            except Exception:
                pass


class LLMClientFactory:
    """
    LLM 客户端工厂
    根据配置创建合适的客户端实例
    """
    
    # OpenAI 官方服务标识
    OPENAI_PROVIDERS = {'openai'}
    
    # 使用 HTTPX 的服务商（兼容 OpenAI API 格式）
    HTTPX_PROVIDERS = {
        'azure',      # Azure OpenAI
        'anthropic',  # Anthropic Claude
        'qwen',       # 通义千问
        'zhipu',      # 智谱 AI
        'moonshot',   # Moonshot AI
        'deepseek',   # DeepSeek
        'ollama',     # Ollama 本地部署
        'custom'      # 自定义兼容服务
    }
    
    @classmethod
    def create(
        cls,
        provider: str,
        api_key: str,
        api_base: str,
        model: str,
        **kwargs
    ) -> BaseLLMClient:
        """
        创建 LLM 客户端实例
        
        Args:
            provider: 服务商标识
            api_key: API 密钥
            api_base: API 基础 URL
            model: 模型名称
            **kwargs: 其他参数
        
        Returns:
            BaseLLMClient 实例
        """
        provider_lower = provider.lower() if provider else 'openai'
        
        if provider_lower in cls.OPENAI_PROVIDERS:
            # 使用 OpenAI SDK
            return OpenAIClient(api_key, api_base, model, **kwargs)
        else:
            # 使用 HTTPX 客户端
            return HTTPXClient(api_key, api_base, model, **kwargs)
    
    @classmethod
    def create_from_config(cls, llm_config) -> BaseLLMClient:
        """
        从 LLMConfig 对象创建客户端
        
        Args:
            llm_config: LLMConfig 数据库模型对象
        
        Returns:
            BaseLLMClient 实例
        """
        extra_params = {}
        if llm_config.extra_params:
            try:
                extra_params = json.loads(llm_config.extra_params)
            except (json.JSONDecodeError, TypeError):
                pass
        
        return cls.create(
            provider=llm_config.provider,
            api_key=llm_config.api_key,
            api_base=llm_config.api_base,
            model=llm_config.model or 'gpt-3.5-turbo',
            **extra_params
        )
    
    @classmethod
    def get_supported_providers(cls) -> Dict[str, str]:
        """获取支持的服务商列表"""
        return {
            'openai': 'OpenAI (使用官方 SDK)',
            'azure': 'Azure OpenAI',
            'qwen': '通义千问 (阿里云)',
            'zhipu': '智谱 AI (GLM)',
            'moonshot': 'Moonshot AI (Kimi)',
            'deepseek': 'DeepSeek',
            'ollama': 'Ollama (本地部署)',
            'anthropic': 'Anthropic (Claude)',
            'custom': '自定义兼容服务'
        }
