"""
AI 服务 - 测试用例生成

采用工厂模式管理 LLM 客户端：
- OpenAI SDK: 用于 OpenAI 官方服务
- HTTPX: 用于其他兼容 OpenAI API 的服务
"""
import json
import os
from typing import List, Dict, Any, Optional
from flask import current_app

from app.services.llm_clients import (
    LLMClientFactory,
    BaseLLMClient,
    ChatMessage,
    ChatResponse
)


class AIService:
    """
    AI 服务类，用于生成测试用例
    采用工厂模式支持多种 LLM 服务商
    """
    
    def __init__(self, llm_config=None):
        """
        初始化 AI 服务
        
        Args:
            llm_config: LLMConfig 对象，如果为 None 则使用默认配置或环境变量
        """
        self.llm_config = llm_config
        self.client: Optional[BaseLLMClient] = None
        
        if llm_config:
            # 使用传入的配置，通过工厂创建客户端
            self.api_key = llm_config.api_key
            self.api_base = llm_config.api_base
            self.model = llm_config.model or 'gpt-3.5-turbo'
            self.provider = llm_config.provider
            
            if self.api_key:
                self.client = LLMClientFactory.create_from_config(llm_config)
        else:
            # 使用环境变量配置（兼容旧版本）
            self.api_key = os.getenv('AI_API_KEY', '')
            self.api_base = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
            self.model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
            self.provider = os.getenv('AI_PROVIDER', 'openai')
            
            if self.api_key:
                self.client = LLMClientFactory.create(
                    provider=self.provider,
                    api_key=self.api_key,
                    api_base=self.api_base,
                    model=self.model
                )
    
    @classmethod
    def from_config_id(cls, config_id: int):
        """
        根据配置ID创建AI服务实例
        
        Args:
            config_id: 大模型配置ID
        
        Returns:
            AIService 实例
        """
        from app.models import LLMConfig
        config = LLMConfig.query.filter(
            LLMConfig.id == config_id,
            LLMConfig.is_active == True
        ).first()
        return cls(config)
    
    @classmethod
    def get_default_service(cls):
        """
        获取默认配置的AI服务实例
        
        Returns:
            AIService 实例
        """
        from app.models import LLMConfig
        # 先尝试获取默认配置
        config = LLMConfig.query.filter(
            LLMConfig.is_default == True,
            LLMConfig.is_active == True
        ).first()
        
        # 如果没有默认配置，获取任一启用的配置
        if not config:
            config = LLMConfig.query.filter(
                LLMConfig.is_active == True
            ).first()
        
        return cls(config)
    
    def generate_testcases(self, requirement, options: Dict[str, Any], prompt_content: str = None, knowledge_contents: List[str] = None) -> List[Dict]:
        """
        根据需求生成测试用例
        
        Args:
            requirement: 需求对象
            options: 生成选项
                - include_boundary: 是否包含边界测试
                - include_exception: 是否包含异常测试
                - include_performance: 是否包含性能测试
                - count: 生成数量
            prompt_content: 自定义提示词内容
            knowledge_contents: 知识库内容列表
        
        Returns:
            测试用例列表
        """
        if self.client:
            return self._generate_with_ai(requirement, options, prompt_content, knowledge_contents)
        else:
            # 如果没有配置 AI，使用模板生成
            return self._generate_with_template(requirement, options)
    
    def _generate_with_ai(self, requirement, options: Dict[str, Any], prompt_content: str = None, knowledge_contents: List[str] = None) -> List[Dict]:
        """使用 AI API 生成测试用例（通过工厂模式创建的客户端）"""
        prompt = self._build_prompt(requirement, options, knowledge_contents)
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(prompt_content)
        
        try:
            # 使用统一的客户端接口
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                messages=messages,
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.content
            # 尝试解析 JSON
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            testcases = json.loads(content)
            return testcases
            
        except Exception as e:
            current_app.logger.error(f'AI API 调用失败 (provider={self.provider}): {str(e)}')
            # 降级使用模板生成
            return self._generate_with_template(requirement, options)
    
    def _generate_with_template(self, requirement, options: Dict[str, Any]) -> List[Dict]:
        """使用模板生成测试用例（无 AI 时的降级方案）"""
        testcases = []
        count = options.get('count', 5)
        
        # 基本功能测试
        testcases.append({
            'title': f'验证{requirement.title}的基本功能',
            'precondition': '系统正常运行，用户已登录',
            'steps': f'1. 进入{requirement.title}相关功能页面\n2. 按照需求文档描述执行操作\n3. 检查系统响应',
            'expected_result': '系统按照需求文档描述正常响应，功能正常',
            'case_type': 'functional',
            'priority': 'high'
        })
        
        # 边界测试
        if options.get('include_boundary', True) and len(testcases) < count:
            testcases.append({
                'title': f'{requirement.title}的边界值测试',
                'precondition': '系统正常运行',
                'steps': '1. 输入边界值数据\n2. 提交操作\n3. 检查系统处理',
                'expected_result': '系统正确处理边界值，无异常',
                'case_type': 'boundary',
                'priority': 'medium'
            })
        
        # 异常测试
        if options.get('include_exception', True) and len(testcases) < count:
            testcases.append({
                'title': f'{requirement.title}的异常输入测试',
                'precondition': '系统正常运行',
                'steps': '1. 输入无效/异常数据\n2. 提交操作\n3. 检查错误处理',
                'expected_result': '系统给出合适的错误提示，不崩溃',
                'case_type': 'exception',
                'priority': 'medium'
            })
            
            testcases.append({
                'title': f'{requirement.title}的空值测试',
                'precondition': '系统正常运行',
                'steps': '1. 必填项留空\n2. 提交操作\n3. 检查验证提示',
                'expected_result': '系统提示必填项不能为空',
                'case_type': 'exception',
                'priority': 'medium'
            })
        
        # 性能测试
        if options.get('include_performance', False) and len(testcases) < count:
            testcases.append({
                'title': f'{requirement.title}的响应时间测试',
                'precondition': '系统正常运行，网络正常',
                'steps': '1. 执行功能操作\n2. 记录响应时间',
                'expected_result': '响应时间在可接受范围内（如 < 3秒）',
                'case_type': 'performance',
                'priority': 'low'
            })
        
        # 补充更多功能测试
        while len(testcases) < count:
            idx = len(testcases)
            testcases.append({
                'title': f'{requirement.title}的功能验证{idx}',
                'precondition': '系统正常运行，用户已登录',
                'steps': f'1. 执行{requirement.title}相关操作\n2. 验证功能点{idx}',
                'expected_result': '功能正常，符合需求预期',
                'case_type': 'functional',
                'priority': 'medium'
            })
        
        return testcases[:count]
    
    def _build_prompt(self, requirement, options: Dict[str, Any], knowledge_contents: List[str] = None) -> str:
        """构建用户提示词"""
        case_types = ['功能测试']
        if options.get('include_boundary', True):
            case_types.append('边界值测试')
        if options.get('include_exception', True):
            case_types.append('异常测试')
        if options.get('include_performance', False):
            case_types.append('性能测试')
        
        # 构建知识库上下文
        knowledge_context = ""
        if knowledge_contents:
            knowledge_context = "\n\n**参考知识库**:\n"
            for i, content in enumerate(knowledge_contents, 1):
                knowledge_context += f"\n--- 知识库 {i} ---\n{content}\n"
        
        prompt = f"""请根据以下需求文档生成 {options.get('count', 5)} 条测试用例：

**需求标题**: {requirement.title}

**需求内容**:
{requirement.content}

**所属模块**: {requirement.module or '未指定'}{knowledge_context}

**要求**:
1. 生成的测试用例类型应包括: {', '.join(case_types)}
2. 测试步骤要具体、可执行
3. 预期结果要明确、可验证
4. 注意覆盖正常流程和异常场景

请直接返回 JSON 数组格式的测试用例。"""
        
        return prompt
    
    def _build_system_prompt(self, custom_prompt: str = None) -> str:
        """构建系统提示词"""
        default_prompt = """你是一位专业的软件测试工程师，擅长根据需求文档编写高质量的测试用例。
请以 JSON 数组格式返回测试用例，每个测试用例包含以下字段:
- title: 用例标题
- precondition: 前置条件
- steps: 测试步骤
- expected_result: 预期结果
- case_type: 用例类型 (functional/boundary/exception/performance)
- priority: 优先级 (high/medium/low)

只返回 JSON 数组，不要包含任何其他内容。"""
        
        if custom_prompt:
            # 将自定义提示词与默认输出格式要求合并
            return f"""{custom_prompt}

**输出格式要求**:
请以 JSON 数组格式返回测试用例，每个测试用例包含以下字段:
- title: 用例标题
- precondition: 前置条件
- steps: 测试步骤
- expected_result: 预期结果
- case_type: 用例类型 (functional/boundary/exception/performance)
- priority: 优先级 (high/medium/low)

只返回 JSON 数组，不要包含任何其他内容。"""
        
        return default_prompt
