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
    import json
    from datetime import datetime
    from app.models import DataFactoryHistory
    from flask_jwt_extended import get_jwt_identity
    
    try:
        start_time = datetime.utcnow()
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        tool_name = data.get('tool_name')
        tool_category = data.get('tool_category')
        input_data = data.get('input_data', {})
        tool_scenario = data.get('tool_scenario', 'other')
        is_saved = bool(data.get('is_saved', False))
        tags = data.get('tags', '')
        # 处理 tags 参数：如果是数组，转换为逗号分隔的字符串
        if isinstance(tags, list):
            tags = ','.join(tags)

        if not tool_name or not tool_category:
            return jsonify({'error': '缺少必要参数: tool_name 或 tool_category'}), 400

        # 获取用户信息
        user_id = None
        username = None
        try:
            user_info = get_jwt_identity()
            if user_info:
                user_id = user_info.get('id')
                username = user_info.get('username')
        except Exception:
            pass

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
        
        # 计算执行时间
        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds() * 1000  # 转换为毫秒
        
        # 保存历史记录
        history = DataFactoryHistory(
            user_id=user_id,
            username=username,
            tool_name=tool_name,
            tool_category=tool_category,
            tool_scenario=tool_scenario,
            input_data=json.dumps(input_data, ensure_ascii=False),
            output_data=json.dumps(result, ensure_ascii=False),
            execution_time=execution_time,
            status='success',
            tags=tags,
            is_saved=is_saved
        )
        from app import db
        db.session.add(history)
        db.session.commit()
        
        return jsonify({
            'result': result,
            'tool_name': tool_name,
            'tool_category': tool_category,
            'tool_scenario': tool_scenario,
            'history_id': history.id
        }), 200

    except Exception as e:
        print(f"执行工具时发生错误: {str(e)}")
        traceback.print_exc()
        
        # 保存失败的历史记录
        try:
            from app import db
            end_time = datetime.utcnow()
            execution_time = (end_time - start_time).total_seconds() * 1000 if 'start_time' in locals() else None
            
            history = DataFactoryHistory(
                user_id=user_id if 'user_id' in locals() else None,
                username=username if 'username' in locals() else None,
                tool_name=tool_name if 'tool_name' in locals() else 'unknown',
                tool_category=tool_category if 'tool_category' in locals() else 'unknown',
                tool_scenario=tool_scenario if 'tool_scenario' in locals() else 'other',
                input_data=json.dumps(input_data, ensure_ascii=False) if 'input_data' in locals() else '{}',
                execution_time=execution_time,
                status='fail',
                error_message=str(e),
                tags=tags if 'tags' in locals() else ''
            )
            db.session.add(history)
            db.session.commit()
        except:
            pass
        
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


@data_factory_bp.route('/', methods=['GET'])
def get_history():
    """
    获取历史记录
    """
    try:
        from app.models import DataFactoryHistory
        from app import db
        
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        
        # 从数据库获取历史记录
        query = DataFactoryHistory.query.order_by(DataFactoryHistory.created_at.desc())
        pagination = query.paginate(page=page, per_page=page_size, error_out=False)
        
        history_records = [record.to_dict() for record in pagination.items]
        total_records = pagination.total
        
        return jsonify({
            'results': history_records,
            'count': total_records
        }), 200

    except Exception as e:
        print(f"获取历史记录时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'获取历史记录时发生错误: {str(e)}'}), 500


@data_factory_bp.route('/statistics', methods=['GET'])
@data_factory_bp.route('/statistics/', methods=['GET'])
def get_statistics():
    """
    获取统计信息
    """
    try:
        from app.models import DataFactoryHistory
        from app import db
        from sqlalchemy import func
        
        # 获取总记录数
        total_records = DataFactoryHistory.query.count()
        
        # 获取分类统计
        category_stats = db.session.query(
            DataFactoryHistory.tool_category,
            func.count(DataFactoryHistory.id)
        ).group_by(DataFactoryHistory.tool_category).all()
        
        # 获取场景统计
        scenario_stats = db.session.query(
            DataFactoryHistory.tool_scenario,
            func.count(DataFactoryHistory.id)
        ).group_by(DataFactoryHistory.tool_scenario).all()
        
        # 构建统计数据
        statistics = {
            'total_records': total_records,
            'category_stats': dict(category_stats),
            'scenario_stats': dict(scenario_stats)
        }
        
        return jsonify(statistics), 200

    except Exception as e:
        print(f"获取统计信息时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'获取统计信息时发生错误: {str(e)}'}), 500


@data_factory_bp.route('/<int:history_id>', methods=['DELETE'])
def delete_history(history_id):
    """
    删除历史记录
    """
    try:
        from app.models import DataFactoryHistory
        from app import db
        
        # 查找历史记录
        history = DataFactoryHistory.query.get(history_id)
        if not history:
            return jsonify({'error': '历史记录不存在'}), 404
        
        # 删除历史记录
        db.session.delete(history)
        db.session.commit()
        
        return jsonify({'message': '删除成功'}), 200

    except Exception as e:
        print(f"删除历史记录时发生错误: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'删除历史记录时发生错误: {str(e)}'}), 500