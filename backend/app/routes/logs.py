"""
日志审计路由
"""
from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from sqlalchemy import or_, and_
import io
import csv
from app import db
from app.models import User, OperationLog
from app.middlewares import log_operation

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
    # 支持前端传来的 per_page 参数和 pageSize 参数
    page_size = request.args.get('per_page', None, type=int)
    if page_size is None:
        page_size = request.args.get('pageSize', 50, type=int)  # 默认值改为50，与前端一致
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')
    module = request.args.get('module', '')
    status = request.args.get('status', '')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    
    # 构建查询
    query = OperationLog.query
    
    # 关键词搜索
    if keyword:
        query = query.filter(
            or_(
                OperationLog.username.like(f'%{keyword}%'),
                OperationLog.description.like(f'%{keyword}%'),
                OperationLog.ip.like(f'%{keyword}%')
            )
        )
    
    # 操作类型过滤
    if action:
        query = query.filter(OperationLog.action == action)
    
    # 模块过滤
    if module:
        query = query.filter(OperationLog.module == module)
    
    # 状态过滤
    if status:
        query = query.filter(OperationLog.status == status)
    
    # 时间过滤
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(OperationLog.created_at >= start_dt)
        except:
            pass
    
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(OperationLog.created_at <= end_dt)
        except:
            pass
    
    # 按时间倒序排列
    query = query.order_by(OperationLog.created_at.desc())
    
    # 分页
    pagination = query.paginate(
        page=page,
        per_page=page_size,
        error_out=False
    )
    
    # 转换为字典列表
    logs = [log.to_dict() for log in pagination.items]
    
    return make_response(0, 'success', {
        'list': logs,
        'total': pagination.total,
        'page': page,
        'pageSize': page_size
    })


@logs_bp.route('/<int:log_id>', methods=['GET'])
@jwt_required()
def get_log(log_id):
    """获取日志详情"""
    log = OperationLog.query.get(log_id)
    
    if not log:
        return make_response(404, '日志不存在')
    
    return make_response(0, 'success', log.to_dict())


@logs_bp.route('/export', methods=['GET'])
@jwt_required()
def export_logs():
    """导出日志为CSV文件"""
    keyword = request.args.get('keyword', '')
    action = request.args.get('action', '')
    module = request.args.get('module', '')
    status = request.args.get('status', '')
    start_time = request.args.get('startTime', '')
    end_time = request.args.get('endTime', '')
    
    # 构建查询（与get_logs相同的过滤逻辑）
    query = OperationLog.query
    
    if keyword:
        query = query.filter(
            or_(
                OperationLog.username.like(f'%{keyword}%'),
                OperationLog.description.like(f'%{keyword}%'),
                OperationLog.ip.like(f'%{keyword}%')
            )
        )
    
    if action:
        query = query.filter(OperationLog.action == action)
    
    if module:
        query = query.filter(OperationLog.module == module)
    
    if status:
        query = query.filter(OperationLog.status == status)
    
    if start_time:
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            query = query.filter(OperationLog.created_at >= start_dt)
        except:
            pass
    
    if end_time:
        try:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            query = query.filter(OperationLog.created_at <= end_dt)
        except:
            pass
    
    query = query.order_by(OperationLog.created_at.desc())
    
    # 获取所有符合条件的日志（限制最多10000条）
    logs = query.limit(10000).all()
    
    # 创建CSV文件
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        'ID', '用户名', '操作类型', '模块', '描述',
        '请求方法', '请求路径', 'IP地址', '浏览器',
        '操作系统', '设备类型', '状态码', '响应时间(ms)',
        '状态', '创建时间'
    ])
    
    # 写入数据
    for log in logs:
        writer.writerow([
            log.id,
            log.username or '',
            log.action or '',
            log.module or '',
            log.description or '',
            log.method or '',
            log.path or '',
            log.ip or '',
            f"{log.browser} {log.browser_version}" if log.browser else '',
            f"{log.os} {log.os_version}" if log.os else '',
            log.device or '',
            log.status_code or '',
            log.response_time or '',
            log.status or '',
            log.created_at.strftime('%Y-%m-%d %H:%M:%S') if log.created_at else ''
        ])
    
    # 转换为字节流
    output.seek(0)
    bytes_output = io.BytesIO()
    bytes_output.write(output.getvalue().encode('utf-8-sig'))  # 使用utf-8-sig支持Excel打开
    bytes_output.seek(0)
    
    # 返回CSV文件
    filename = f"operation_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return send_file(
        bytes_output,
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )


@logs_bp.route('/statistics', methods=['GET'])
@jwt_required()
def get_statistics():
    """获取日志统计信息"""
    from sqlalchemy import func
    
    # 统计总数
    total = OperationLog.query.count()
    
    # 统计今日日志数
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_count = OperationLog.query.filter(OperationLog.created_at >= today_start).count()
    
    # 统计成功/失败数
    success_count = OperationLog.query.filter(OperationLog.status == 'success').count()
    fail_count = OperationLog.query.filter(OperationLog.status.in_(['fail', 'error'])).count()
    
    # 按操作类型统计
    action_stats = db.session.query(
        OperationLog.action,
        func.count(OperationLog.id).label('count')
    ).group_by(OperationLog.action).all()
    
    # 按模块统计
    module_stats = db.session.query(
        OperationLog.module,
        func.count(OperationLog.id).label('count')
    ).group_by(OperationLog.module).order_by(func.count(OperationLog.id).desc()).limit(10).all()
    
    return make_response(0, 'success', {
        'total': total,
        'today_count': today_count,
        'success_count': success_count,
        'fail_count': fail_count,
        'action_stats': [{'action': a, 'count': c} for a, c in action_stats],
        'module_stats': [{'module': m, 'count': c} for m, c in module_stats]
    })
