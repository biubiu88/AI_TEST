"""
中间件和装饰器
"""
import time
import json
import re
from functools import wraps
from flask import request, g
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app import db
from app.models import OperationLog, User


def parse_user_agent(user_agent_string):
    """解析User-Agent字符串"""
    if not user_agent_string:
        return {
            'browser': 'Unknown',
            'browser_version': '',
            'os': 'Unknown',
            'os_version': '',
            'device': 'desktop'
        }
    
    ua = user_agent_string.lower()
    result = {
        'browser': 'Unknown',
        'browser_version': '',
        'os': 'Unknown',
        'os_version': '',
        'device': 'desktop'
    }
    
    # 检测设备类型
    if 'mobile' in ua or 'android' in ua or 'iphone' in ua:
        result['device'] = 'mobile'
    elif 'tablet' in ua or 'ipad' in ua:
        result['device'] = 'tablet'
    
    # 检测浏览器
    if 'edg/' in ua or 'edge' in ua:
        result['browser'] = 'Edge'
        match = re.search(r'edg[e]?/(\d+\.?\d*)', ua)
        if match:
            result['browser_version'] = match.group(1)
    elif 'chrome' in ua and 'safari' in ua:
        result['browser'] = 'Chrome'
        match = re.search(r'chrome/(\d+\.?\d*)', ua)
        if match:
            result['browser_version'] = match.group(1)
    elif 'firefox' in ua:
        result['browser'] = 'Firefox'
        match = re.search(r'firefox/(\d+\.?\d*)', ua)
        if match:
            result['browser_version'] = match.group(1)
    elif 'safari' in ua and 'chrome' not in ua:
        result['browser'] = 'Safari'
        match = re.search(r'version/(\d+\.?\d*)', ua)
        if match:
            result['browser_version'] = match.group(1)
    elif 'msie' in ua or 'trident' in ua:
        result['browser'] = 'IE'
        match = re.search(r'(?:msie |rv:)(\d+\.?\d*)', ua)
        if match:
            result['browser_version'] = match.group(1)
    
    # 检测操作系统
    if 'windows nt 10' in ua:
        result['os'] = 'Windows'
        result['os_version'] = '10/11'
    elif 'windows nt 6.3' in ua:
        result['os'] = 'Windows'
        result['os_version'] = '8.1'
    elif 'windows nt 6.2' in ua:
        result['os'] = 'Windows'
        result['os_version'] = '8'
    elif 'windows nt 6.1' in ua:
        result['os'] = 'Windows'
        result['os_version'] = '7'
    elif 'windows' in ua:
        result['os'] = 'Windows'
    elif 'mac os x' in ua or 'macos' in ua:
        result['os'] = 'MacOS'
        match = re.search(r'mac os x (\d+[._]\d+)', ua)
        if match:
            result['os_version'] = match.group(1).replace('_', '.')
    elif 'linux' in ua:
        result['os'] = 'Linux'
    elif 'android' in ua:
        result['os'] = 'Android'
        match = re.search(r'android (\d+\.?\d*)', ua)
        if match:
            result['os_version'] = match.group(1)
    elif 'iphone' in ua or 'ipad' in ua:
        result['os'] = 'iOS'
        match = re.search(r'os (\d+[._]\d+)', ua)
        if match:
            result['os_version'] = match.group(1).replace('_', '.')
    
    return result


def get_client_ip():
    """获取客户端IP地址"""
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def get_action_from_request():
    """从请求中推断操作类型"""
    method = request.method
    path = request.path
    
    # 登录登出
    if 'login' in path:
        return 'login'
    elif 'logout' in path:
        return 'logout'
    
    # CRUD操作
    if method == 'POST':
        if 'export' in path:
            return 'export'
        elif 'import' in path:
            return 'import'
        return 'create'
    elif method == 'PUT' or method == 'PATCH':
        return 'update'
    elif method == 'DELETE':
        return 'delete'
    elif method == 'GET':
        return 'query'
    
    return 'unknown'


def get_module_from_path(path):
    """从路径中提取模块名称"""
    # 移除 /api/ 前缀
    path = path.replace('/api/', '')
    
    # 提取第一段路径作为模块名
    parts = path.split('/')
    if parts:
        module = parts[0].replace('-', '_')
        # 移除复数形式的s
        if module.endswith('s') and module not in ['logs', 'menus']:
            module = module[:-1]
        return module
    
    return 'unknown'


def get_description_from_request():
    """生成操作描述"""
    action = get_action_from_request()
    module = get_module_from_path(request.path)
    
    action_map = {
        'login': '登录',
        'logout': '登出',
        'create': '创建',
        'update': '更新',
        'delete': '删除',
        'query': '查询',
        'export': '导出',
        'import': '导入'
    }
    
    module_map = {
        'user': '用户',
        'role': '角色',
        'menu': '菜单',
        'permission': '权限',
        'requirement': '需求',
        'testcase': '测试用例',
        'prompt': '提示词',
        'knowledge': '知识库',
        'llm_config': '模型配置',
        'mcp_config': 'MCP配置',
        'ai_assistant': 'AI助手',
        'log': '日志'
    }
    
    action_text = action_map.get(action, action)
    module_text = module_map.get(module, module)
    
    return f"{action_text}{module_text}"


def log_operation(f):
    """
    日志记录装饰器
    自动记录API操作日志
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 记录请求开始时间
        start_time = time.time()
        
        # 初始化日志数据
        log_data = {
            'method': request.method,
            'path': request.path,
            'action': get_action_from_request(),
            'module': get_module_from_path(request.path),
            'description': get_description_from_request(),
            'ip': get_client_ip(),
            'user_agent': request.headers.get('User-Agent', ''),
        }
        
        # 解析User-Agent
        ua_info = parse_user_agent(log_data['user_agent'])
        log_data.update(ua_info)
        
        # 尝试获取用户信息
        try:
            verify_jwt_in_request(optional=True)
            user_id = get_jwt_identity()
            if user_id:
                user = User.query.get(user_id)
                if user:
                    log_data['user_id'] = user.id
                    log_data['username'] = user.username
        except:
            pass
        
        # 获取请求参数
        try:
            if request.method in ['POST', 'PUT', 'PATCH']:
                # 获取请求体
                if request.is_json:
                    params = request.get_json() or {}
                    # 过滤敏感信息
                    filtered_params = {k: v for k, v in params.items() 
                                      if k not in ['password', 'confirmPassword', 'api_key', 'token']}
                    log_data['params'] = json.dumps(filtered_params, ensure_ascii=False)[:2000]  # 限制长度
            elif request.method == 'GET':
                params = dict(request.args)
                log_data['params'] = json.dumps(params, ensure_ascii=False)[:2000]
        except:
            log_data['params'] = None
        
        # 执行原函数
        try:
            response = f(*args, **kwargs)
            
            # 记录响应信息
            if hasattr(response, 'status_code'):
                log_data['status_code'] = response.status_code
            else:
                log_data['status_code'] = 200
            
            # 判断状态
            if log_data['status_code'] >= 200 and log_data['status_code'] < 300:
                log_data['status'] = 'success'
            elif log_data['status_code'] >= 400:
                log_data['status'] = 'fail'
            
            return response
            
        except Exception as e:
            # 记录错误
            log_data['status'] = 'error'
            log_data['status_code'] = 500
            log_data['error_msg'] = str(e)[:500]
            raise
            
        finally:
            # 计算响应时间
            end_time = time.time()
            log_data['response_time'] = round((end_time - start_time) * 1000, 2)  # 转换为毫秒
            
            # 保存日志到数据库（异步或后台任务更佳）
            try:
                operation_log = OperationLog(**log_data)
                db.session.add(operation_log)
                db.session.commit()
            except Exception as e:
                # 日志保存失败不应影响主流程
                print(f"保存操作日志失败: {e}")
                db.session.rollback()
    
    return decorated_function
