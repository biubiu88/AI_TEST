"""
AI 服务 - 测试用例生成
"""
import json
import os
from typing import List, Dict, Any
from flask import current_app

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class AIService:
    """AI 服务类，用于生成测试用例"""
    
    def __init__(self):
        self.api_key = os.getenv('AI_API_KEY', '')
        self.api_base = os.getenv('AI_API_BASE', 'https://api.openai.com/v1')
        self.model = os.getenv('AI_MODEL', 'gpt-3.5-turbo')
        
        if OPENAI_AVAILABLE and self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
        else:
            self.client = None
    
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
        """使用 AI API 生成测试用例"""
        prompt = self._build_prompt(requirement, options, knowledge_contents)
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(prompt_content)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            content = response.choices[0].message.content.strip()
            # 尝试解析 JSON
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            testcases = json.loads(content)
            return testcases
            
        except Exception as e:
            current_app.logger.error(f'AI API 调用失败: {str(e)}')
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
