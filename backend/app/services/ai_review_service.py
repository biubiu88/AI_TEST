"""
AI 评审服务 - 测试用例AI评审

基于 AIService 扩展，提供测试用例的AI自动评审功能
"""
import json
import os
from typing import List, Dict, Any, Optional
from flask import current_app

from app.services.ai_service import AIService
from app.services.llm_clients import (
    ChatMessage,
    ChatResponse
)


class AIReviewService(AIService):
    """
    AI 评审服务类，基于 AIService 扩展
    用于对测试用例进行AI自动评审
    """
    
    def review_testcases(
        self,
        testcases: List[Dict],
        options: Dict[str, Any],
        prompt_content: str = None,
        knowledge_contents: List[str] = None
    ) -> List[Dict]:
        """
        使用AI对测试用例进行评审
        
        Args:
            testcases: 测试用例列表
            options: 评审选项
                - review_dimensions: 评审维度列表
                - scoring_criteria: 评分标准
                - count: 评审数量限制
            prompt_content: 自定义提示词内容
            knowledge_contents: 知识库内容列表
        
        Returns:
            评审结果列表
        """
        if self.client:
            return self._review_with_ai(testcases, options, prompt_content, knowledge_contents)
        else:
            # 如果没有配置AI，使用模板评审
            return self._review_with_template(testcases, options)
    
    def _review_with_ai(
        self,
        testcases: List[Dict],
        options: Dict[str, Any],
        prompt_content: str = None,
        knowledge_contents: List[str] = None
    ) -> List[Dict]:
        """使用AI对测试用例进行评审"""
        prompt = self._build_review_prompt(testcases, options, knowledge_contents)
        
        # 构建系统提示词
        system_prompt = self._build_system_prompt(prompt_content, options)
        
        try:
            # 使用统一的客户端接口
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=prompt)
            ]
            
            response = self.client.chat(
                messages=messages,
                temperature=0.3,  # 评审需要较低的温度，保证稳定性
                max_tokens=8000
            )
            
            content = response.content
            
            # 尝试解析JSON
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            
            reviews = json.loads(content)
            
            # 确保返回的是列表
            if not isinstance(reviews, list):
                reviews = [reviews]
            
            return reviews
            
        except Exception as e:
            current_app.logger.error(f'AI评审失败 (provider={self.provider}): {str(e)}')
            # 降级使用模板评审
            return self._review_with_template(testcases, options)
    
    def _review_with_template(
        self,
        testcases: List[Dict],
        options: Dict[str, Any]
    ) -> List[Dict]:
        """使用模板对测试用例进行评审（无AI时的降级方案）"""
        reviews = []
        
        for tc in testcases:
            review = {
                'testcase_id': tc.get('id'),
                'testcase_title': tc.get('title'),
                'status': 'approved',
                'overall_rating': 3,
                'comments': '模板评审：用例结构完整，建议人工复核。',
                'improvement_suggestions': '',
                'clarity_score': 3,
                'completeness_score': 3,
                'feasibility_score': 3,
                'coverage_score': 3
            }
            
            # 简单规则检查
            issues = []
            
            # 检查标题
            if not tc.get('title') or len(tc.get('title', '')) < 5:
                issues.append('标题过短或不明确')
                review['clarity_score'] = 2
            
            # 检查步骤
            steps = tc.get('steps', '')
            if not steps or len(steps) < 10:
                issues.append('测试步骤过于简单')
                review['completeness_score'] = 2
            
            # 检查预期结果
            expected = tc.get('expected_result', '')
            if not expected or len(expected) < 5:
                issues.append('预期结果不明确')
                review['feasibility_score'] = 2
            
            # 根据问题调整评分和状态
            if issues:
                review['comments'] = f'发现以下问题：{"; ".join(issues)}'
                review['status'] = 'need_revision'
                review['overall_rating'] = 2
            
            reviews.append(review)
        
        return reviews
    
    def _build_review_prompt(
        self,
        testcases: List[Dict],
        options: Dict[str, Any],
        knowledge_contents: List[str] = None
    ) -> str:
        """构建评审提示词"""
        # 构建测试用例列表文本
        testcase_list = []
        for i, tc in enumerate(testcases[:10], 1):  # 限制最多评审10个
            testcase_list.append(f"""
用例 {i}:
- ID: {tc.get('id')}
- 标题: {tc.get('title')}
- 前置条件: {tc.get('precondition', '无')}
- 测试步骤: {tc.get('steps')}
- 预期结果: {tc.get('expected_result')}
- 类型: {tc.get('case_type')}
- 优先级: {tc.get('priority')}
""")
        
        # 构建知识库上下文
        knowledge_context = ""
        if knowledge_contents:
            knowledge_context = "\n\n**参考知识库**:\n"
            for i, content in enumerate(knowledge_contents, 1):
                knowledge_context += f"\n--- 知识库 {i} ---\n{content}\n"
        
        # 构建评分标准说明
        scoring_desc = """
评分标准（1-5分）：
- 1分：质量很差，需要完全重写
- 2分：质量较差，需要大量修改
- 3分：质量一般，需要部分修改
- 4分：质量较好，需要小幅改进
- 5分：质量优秀，无需修改
"""
        
        prompt = f"""请对以下测试用例进行专业评审，给出详细的质量评估和改进建议：

**测试用例列表**:
{''.join(testcase_list)}{knowledge_context}

**评审要求**:
1. 对每个测试用例进行独立评审
2. 从以下维度进行评分（1-5分）：
   - 清晰度：用例描述是否清晰易懂
   - 完整性：用例要素是否完整（标题、步骤、预期结果等）
   - 可执行性：用例是否可以被执行
   - 覆盖度：用例覆盖范围是否充分
3. 给出整体评分和评审状态
4. 提供具体的评审意见和改进建议
5. 评审状态包括：approved（通过）、rejected（拒绝）、need_revision（需要修改）

{scoring_desc}

请直接返回JSON数组格式的评审结果，每个评审包含以下字段:
- testcase_id: 测试用例ID
- testcase_title: 测试用例标题
- status: 评审状态
- overall_rating: 整体评分（1-5）
- comments: 评审意见
- improvement_suggestions: 改进建议
- clarity_score: 清晰度评分（1-5）
- completeness_score: 完整性评分（1-5）
- feasibility_score: 可执行性评分（1-5）
- coverage_score: 覆盖度评分（1-5）

只返回JSON数组，不要包含任何其他内容。"""
        
        return prompt
    
    def _build_system_prompt(
        self,
        custom_prompt: str = None,
        options: Dict[str, Any] = None
    ) -> str:
        """构建系统提示词"""
        default_prompt = """你是一位资深的软件测试专家和QA工程师，拥有10年以上的测试用例设计和评审经验。你擅长：

1. 评估测试用例的质量和完整性
2. 识别测试用例中的潜在问题
3. 提供专业的改进建议
4. 从多个维度（清晰度、完整性、可执行性、覆盖度）进行客观评分

你的评审标准：
- 清晰度：用例标题、步骤、预期结果的描述是否清晰易懂
- 完整性：是否包含所有必要的要素（标题、前置条件、步骤、预期结果）
- 可执行性：测试步骤是否明确、可操作，预期结果是否可验证
- 覆盖度：是否覆盖了正常流程、异常场景、边界条件

评审原则：
- 客观公正，基于事实进行评价
- 建设性批评，提供可操作的改进建议
- 关注实际可执行性，避免理论化
- 考虑业务价值和技术可行性的平衡

请以JSON数组格式返回评审结果，不要包含任何其他内容。"""
        
        if custom_prompt:
            # 将自定义提示词与默认输出格式要求合并
            return f"""{custom_prompt}

**输出格式要求**:
请以JSON数组格式返回评审结果，每个评审包含以下字段:
- testcase_id: 测试用例ID
- testcase_title: 测试用例标题
- status: 评审状态 (approved/rejected/need_revision)
- overall_rating: 整体评分 (1-5)
- comments: 评审意见
- improvement_suggestions: 改进建议
- clarity_score: 清晰度评分 (1-5)
- completeness_score: 完整性评分 (1-5)
- feasibility_score: 可执行性评分 (1-5)
- coverage_score: 覆盖度评分 (1-5)

只返回JSON数组，不要包含任何其他内容。"""
        
        return default_prompt


class AIReviewServiceFactory:
    """AI评审服务工厂"""
    
    @classmethod
    def create_from_config_id(cls, config_id: int):
        """根据配置ID创建AI评审服务"""
        return AIReviewService.from_config_id(config_id)
    
    @classmethod
    def get_default_service(cls):
        """获取默认配置的AI评审服务"""
        return AIReviewService.get_default_service()
