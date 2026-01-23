"""
AI 相关路由
"""
import os
import uuid
import tempfile
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Requirement, TestCase, Prompt, Knowledge, LLMConfig
from app.services.ai_service import AIService

ai_bp = Blueprint('ai', __name__)

# 支持的文档格式
ALLOWED_EXTENSIONS = {'txt', 'doc', 'docx', 'pdf'}


def ensure_string(value, separator='\n'):
    """
    确保值为字符串格式
    如果是列表则使用分隔符连接为字符串
    
    Args:
        value: 输入值，可能是字符串、列表或其他类型
        separator: 列表连接分隔符，默认为换行符
    
    Returns:
        字符串格式的值
    """
    if value is None:
        return ''
    if isinstance(value, list):
        return separator.join(str(item) for item in value)
    return str(value)


def get_prompt_and_knowledge(data):
    """获取提示词和知识库内容"""
    prompt_content = None
    knowledge_contents = None
    
    # 获取提示词内容
    prompt_id = data.get('prompt_id')
    if prompt_id:
        prompt = Prompt.query.filter(
            Prompt.id == prompt_id,
            Prompt.is_active == True
        ).first()
        if prompt:
            prompt_content = prompt.content
    elif not prompt_id:
        # 如果没有指定，使用默认提示词
        default_prompt = Prompt.query.filter(
            Prompt.is_default == True,
            Prompt.is_active == True
        ).first()
        if default_prompt:
            prompt_content = default_prompt.content
    
    # 获取知识库内容
    knowledge_ids = data.get('knowledge_ids', [])
    if knowledge_ids:
        knowledges = Knowledge.query.filter(
            Knowledge.id.in_(knowledge_ids),
            Knowledge.is_active == True
        ).all()
        if knowledges:
            knowledge_contents = [k.content for k in knowledges]
    
    return prompt_content, knowledge_contents


def allowed_file(filename):
    """检查文件格式是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def parse_document_content(file_path, filename):
    """解析文档内容"""
    ext = filename.rsplit('.', 1)[1].lower()
    content = ''
    
    try:
        if ext == 'txt':
            # 读取纯文本文件
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        elif ext in ['doc', 'docx']:
            # 读取 Word 文档
            try:
                import docx
                doc = docx.Document(file_path)
                content = '\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
            except ImportError:
                raise Exception('python-docx 未安装，无法解析 Word 文档')
        elif ext == 'pdf':
            # 读取 PDF 文档
            try:
                import PyPDF2
                with open(file_path, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    content = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
            except ImportError:
                raise Exception('PyPDF2 未安装，无法解析 PDF 文档')
    except UnicodeDecodeError:
        # 尝试其他编码
        with open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
    
    return content.strip()


@ai_bp.route('/generate', methods=['POST'])
def generate_testcases():
    """根据需求生成测试用例"""
    data = request.get_json()
    requirement_id = data.get('requirement_id')
    requirement_content = data.get('requirement_content')
    requirement_title = data.get('requirement_title', '手动输入需求')
    
    # 支持两种方式：通过ID选择需求 或 直接传入需求内容
    requirement = None
    if requirement_id:
        requirement = Requirement.query.get(requirement_id)
        if not requirement:
            return jsonify({'code': 404, 'message': '需求不存在'}), 404
    elif requirement_content:
        # 创建临时需求对象（不保存到数据库）
        class TempRequirement:
            def __init__(self, title, content):
                self.id = None
                self.title = title
                self.content = content
                self.module = '临时需求'
        requirement = TempRequirement(requirement_title, requirement_content)
    else:
        return jsonify({'code': 400, 'message': '请选择需求或输入需求内容'}), 400
    
    # 获取生成选项
    options = {
        'include_boundary': data.get('include_boundary', True),
        'include_exception': data.get('include_exception', True),
        'include_performance': data.get('include_performance', False),
        'count': data.get('count', 5)
    }
    
    try:
        # 获取提示词和知识库
        prompt_content, knowledge_contents = get_prompt_and_knowledge(data)
        
        # 获取AI服务实例
        llm_config_id = data.get('llm_config_id')
        if llm_config_id:
            ai_service = AIService.from_config_id(llm_config_id)
        else:
            ai_service = AIService.get_default_service()
        
        testcases = ai_service.generate_testcases(requirement, options, prompt_content, knowledge_contents)
        
        # 保存生成的测试用例
        saved_testcases = []
        for tc_data in testcases:
            # 处理 steps 和 expected_result 字段 - 如果是列表则转换为字符串
            steps = ensure_string(tc_data.get('steps', ''))
            expected_result = ensure_string(tc_data.get('expected_result', ''))
            testcase = TestCase(
                requirement_id=requirement_id,  # 如果是文本输入，则为 None
                title=tc_data['title'],
                precondition=tc_data.get('precondition', ''),
                steps=steps,
                expected_result=expected_result,
                case_type=tc_data.get('case_type', 'functional'),
                priority=tc_data.get('priority', 'medium'),
                status='pending',
                is_ai_generated=True
            )
            db.session.add(testcase)
            saved_testcases.append(testcase)
        
        db.session.commit()
        
        return jsonify({
            'code': 0,
            'message': f'成功生成 {len(saved_testcases)} 条测试用例',
            'data': [tc.to_dict() for tc in saved_testcases]
        })
    except Exception as e:
        current_app.logger.error(f'AI生成测试用例失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@ai_bp.route('/preview', methods=['POST'])
def preview_testcases():
    """预览AI生成的测试用例（不保存）"""
    data = request.get_json()
    requirement_id = data.get('requirement_id')
    requirement_content = data.get('requirement_content')
    requirement_title = data.get('requirement_title', '手动输入需求')
    
    # 支持两种方式：通过ID选择需求 或 直接传入需求内容
    requirement = None
    if requirement_id:
        requirement = Requirement.query.get(requirement_id)
        if not requirement:
            return jsonify({'code': 404, 'message': '需求不存在'}), 404
    elif requirement_content:
        # 创建临时需求对象（不保存到数据库）
        class TempRequirement:
            def __init__(self, title, content):
                self.id = None
                self.title = title
                self.content = content
                self.module = '临时需求'
        requirement = TempRequirement(requirement_title, requirement_content)
    else:
        return jsonify({'code': 400, 'message': '请选择需求或输入需求内容'}), 400
    
    options = {
        'include_boundary': data.get('include_boundary', True),
        'include_exception': data.get('include_exception', True),
        'include_performance': data.get('include_performance', False),
        'count': data.get('count', 5)
    }
    
    try:
        # 获取提示词和知识库
        prompt_content, knowledge_contents = get_prompt_and_knowledge(data)
        
        # 获取AI服务实例
        llm_config_id = data.get('llm_config_id')
        if llm_config_id:
            ai_service = AIService.from_config_id(llm_config_id)
        else:
            ai_service = AIService.get_default_service()
        
        testcases = ai_service.generate_testcases(requirement, options, prompt_content, knowledge_contents)
        
        return jsonify({
            'code': 0,
            'message': 'success',
            'data': testcases
        })
    except Exception as e:
        current_app.logger.error(f'AI预览测试用例失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'生成失败: {str(e)}'}), 500


@ai_bp.route('/parse-document', methods=['POST'])
def parse_document():
    """解析上传的文档"""
    if 'file' not in request.files:
        return jsonify({'code': 400, 'message': '请上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'code': 400, 'message': '请选择文件'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'code': 400, 'message': '不支持的文件格式，请上传 .txt, .doc, .docx, .pdf 格式的文件'}), 400
    
    try:
        # 保存到临时文件，使用原始文件名的扩展名
        original_filename = file.filename
        ext = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else ''
        # 生成安全的临时文件名
        safe_filename = f"{uuid.uuid4().hex}.{ext}"
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, safe_filename)
        file.save(temp_path)
        
        # 解析文档内容，使用原始文件名的扩展名
        content = parse_document_content(temp_path, original_filename)
        
        # 删除临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if not content:
            return jsonify({'code': 400, 'message': '文档内容为空或无法解析'}), 400
        
        return jsonify({
            'code': 0,
            'message': '解析成功',
            'data': {
                'content': content,
                'filename': file.filename
            }
        })
    except Exception as e:
        current_app.logger.error(f'文档解析失败: {str(e)}')
        return jsonify({'code': 500, 'message': f'文档解析失败: {str(e)}'}), 500
