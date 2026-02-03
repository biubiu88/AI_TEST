"""
数据工厂路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.data_factory_service import DataFactoryService
from app.models import User
import traceback

data_factory_bp = Blueprint('data_factory', __name__)

@data_factory_bp.route('/', methods=['POST'])
def execute_tool():
    """
    执行数据工厂工具
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        tool_name = data.get('tool_name')
        tool_category = data.get('tool_category')
        input_data = data.get('input_data', {})
        tool_scenario = data.get('tool_scenario', 'other')

        if not tool_name or not tool_category:
            return jsonify({'error': '缺少必要参数: tool_name 或 tool_category'}), 400

        # 根据工具名称和类别执行相应工具
        service = DataFactoryService()
        
        # 根据工具类别映射到对应的方法
        if tool_category == 'test_data':
            method_map = {
                'generate_chinese_name': DataFactoryService.generate_chinese_name,
                'generate_chinese_phone': DataFactoryService.generate_chinese_phone,
                'generate_chinese_email': DataFactoryService.generate_chinese_email,
                'generate_chinese_address': DataFactoryService.generate_chinese_address,
                'generate_company_name': DataFactoryService.generate_company_name,
            }
        elif tool_category == 'string':
            method_map = {
                'remove_whitespace': DataFactoryService.remove_whitespace,
                'replace_string': DataFactoryService.replace_string,
                'escape_string': DataFactoryService.escape_string,
                'unescape_string': DataFactoryService.unescape_string,
                'word_count': DataFactoryService.word_count,
                'text_diff': DataFactoryService.text_diff,
                'regex_test': DataFactoryService.regex_test,
                'case_convert': DataFactoryService.case_convert,
                'string_format': DataFactoryService.string_format,
            }
        elif tool_category == 'random':
            method_map = {
                'random_int': DataFactoryService.random_int,
                'random_float': DataFactoryService.random_float,
                'random_string': DataFactoryService.random_string,
                'random_uuid': DataFactoryService.random_uuid,
                'random_mac_address': DataFactoryService.random_mac_address,
                'random_ip_address': DataFactoryService.random_ip_address,
                'random_date': DataFactoryService.random_date,
                'random_boolean': DataFactoryService.random_boolean,
                'random_color': DataFactoryService.random_color,
                'random_password': DataFactoryService.random_password,
                'random_sequence': DataFactoryService.random_sequence,
            }
        elif tool_category == 'encoding':
            method_map = {
                'timestamp_convert': DataFactoryService.timestamp_convert,
                'base_convert': DataFactoryService.base_convert,
                'base64_encode': DataFactoryService.base64_encode,
                'base64_decode': DataFactoryService.base64_decode,
            }
        elif tool_category == 'encryption':
            method_map = {
                'md5_hash': DataFactoryService.md5_hash,
                'sha1_hash': DataFactoryService.sha1_hash,
                'sha256_hash': DataFactoryService.sha256_hash,
                'sha512_hash': DataFactoryService.sha512_hash,
                'hash_comparison': DataFactoryService.hash_comparison,
                'password_strength': DataFactoryService.password_strength,
            }
        elif tool_category == 'json':
            method_map = {
                'format_json': DataFactoryService.format_json,
                'validate_json': DataFactoryService.validate_json,
                # 注意：其他JSON工具如json_to_xml等需要在服务类中实现
            }
        elif tool_category == 'mock':
            method_map = {
                'mock_string': DataFactoryService.random_string,
                'mock_number': DataFactoryService.random_int,
                'mock_boolean': DataFactoryService.random_boolean,
                'mock_date': DataFactoryService.random_date,
                'mock_datetime': DataFactoryService.random_date,
            }
        elif tool_category == 'crontab':
            method_map = {
                # 注意：Crontab工具需要在服务类中实现
            }
        else:
            return jsonify({'error': f'不支持的工具类别: {tool_category}'}), 400

        if tool_name not in method_map:
            return jsonify({'error': f'不支持的工具: {tool_name}'}), 400

        # 执行工具
        method = method_map[tool_name]
        
        # 处理输入参数
        if input_data:
            result = method(**input_data)
        else:
            # 对于某些工具，可能不需要参数
            if tool_name in ['random_uuid', 'random_boolean']:
                result = method()
            else:
                # 尝试使用默认参数
                result = method(**{})
        
        return jsonify({
            'result': result,
            'tool_name': tool_name,
            'tool_category': tool_category,
            'tool_scenario': tool_scenario
        }), 200

    except Exception as e:
        print(f"执行工具时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'执行工具时发生错误: {str(e)}'}), 500


@data_factory_bp.route('/categories', methods=['GET'])
@data_factory_bp.route('/categories/', methods=['GET'])
def get_categories():
    """
    获取所有工具分类
    """
    try:
        service = DataFactoryService()
        categories = service.get_categories()
        tool_list = service.get_tool_list()

        # 为每个分类添加工具列表
        for category in categories:
            category_name = category['category']
            category['tools'] = [tool for tool in tool_list if tool['category'] == category_name]

        return jsonify({
            'categories': categories,
            'total_tools': len(tool_list)
        }), 200

    except Exception as e:
        print(f"获取分类时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'获取分类时发生错误: {str(e)}'}), 500


@data_factory_bp.route('/tools', methods=['GET'])
def get_tools():
    """
    获取所有工具列表
    """
    try:
        service = DataFactoryService()
        tool_list = service.get_tool_list()
        
        return jsonify({
            'tools': tool_list,
            'count': len(tool_list)
        }), 200

    except Exception as e:
        print(f"获取工具列表时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'获取工具列表时发生错误: {str(e)}'}), 500