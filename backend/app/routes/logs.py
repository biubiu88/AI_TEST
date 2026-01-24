"""
日志审计路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import User

logs_bp = Blueprint('logs', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


@logs_bp.route('', methods=['GET'])
@jwt_required()
def get_logs():
    """获取日志列表"""
    page = request.args.get('page', 1, type=int)
    page_size = request.args.get('pageSize', 10, type=int)
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')
    module = request.args.get('module', '')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    
    # 查询日志（这里使用模拟数据，实际应该从日志表查询）
    # TODO: 创建日志表并实现真实的日志记录功能
    mock_logs = [
        {
            'id': 1,
            'user': 'admin',
            'action': 'login',
            'module': 'user',
            'description': '用户登录系统',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 14:30:25'
        },
        {
            'id': 2,
            'user': 'admin',
            'action': 'create',
            'module': 'requirement',
            'description': '创建需求"用户登录功能"',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 14:35:10'
        },
        {
            'id': 3,
            'user': 'admin',
            'action': 'update',
            'module': 'testcase',
            'description': '更新测试用例#123',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 14:40:05'
        },
        {
            'id': 4,
            'user': 'testuser',
            'action': 'login',
            'module': 'user',
            'description': '用户登录系统',
            'ip': '192.168.1.101',
            'browser': 'Firefox 121.0',
            'os': 'MacOS 14',
            'status': 'success',
            'created_at': '2024-01-24 14:45:30'
        },
        {
            'id': 5,
            'user': 'admin',
            'action': 'delete',
            'module': 'testcase',
            'description': '删除测试用例#456',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 14:50:15'
        },
        {
            'id': 6,
            'user': 'testuser',
            'action': 'create',
            'module': 'testcase',
            'description': '创建测试用例"密码验证"',
            'ip': '192.168.1.101',
            'browser': 'Firefox 121.0',
            'os': 'MacOS 14',
            'status': 'success',
            'created_at': '2024-01-24 14:55:20'
        },
        {
            'id': 7,
            'user': 'admin',
            'action': 'update',
            'module': 'menu',
            'description': '更新菜单结构',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 15:00:05'
        },
        {
            'id': 8,
            'user': 'testuser',
            'action': 'logout',
            'module': 'user',
            'description': '用户登出系统',
            'ip': '192.168.1.101',
            'browser': 'Firefox 121.0',
            'os': 'MacOS 14',
            'status': 'success',
            'created_at': '2024-01-24 15:05:30'
        }
    ]
    
    # 过滤日志
    filtered_logs = mock_logs
    
    if keyword:
        filtered_logs = [log for log in filtered_logs if keyword in log['user'] or keyword in log['description']]
    
    if action:
        filtered_logs = [log for log in filtered_logs if log['action'] == action]
    
    if module:
        filtered_logs = [log for log in filtered_logs if log['module'] == module]
    
    if start_time:
        filtered_logs = [log for log in filtered_logs if log['created_at'] >= start_time]
    
    if end_time:
        filtered_logs = [log for log in filtered_logs if log['created_at'] <= end_time]
    
    # 分页
    total = len(filtered_logs)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_logs = filtered_logs[start:end]
    
    return make_response(0, 'success', {
        'list': paginated_logs,
        'total': total,
        'page': page,
        'pageSize': page_size
    })


@logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """获取日志详情"""
    # TODO: 从日志表查询
    mock_logs = {
        1: {
            'id': 1,
            'user': 'admin',
            'action': 'login',
            'module': 'user',
            'description': '用户登录系统',
            'ip': '192.168.1.100',
            'browser': 'Chrome 120.0',
            'os': 'Windows 11',
            'status': 'success',
            'created_at': '2024-01-24 14:30:25'
        }
    }
    
    log = mock_logs.get(log_id)
    if not log:
        return make_response(404, '日志不存在')
    
    return make_response(0, 'success', log)


@logs_bp.route('/export', methods=['GET'])
@jwt_required()
def export_logs():
    """导出日志"""
    # TODO: 实现日志导出功能
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')
    module = request.args.get('module', '')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    
    # 模拟导出数据
    export_data = {
        'keyword': keyword,
        'action': action,
        'module': module,
        'start_time': start_time,
        'end_time': end_time,
        'export_time': datetime.utcnow().isoformat(),
        'total_count': 100
    }
    
    return make_response(0, '导出成功', export_data)
