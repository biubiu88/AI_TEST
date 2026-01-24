"""
测试日志记录功能
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

# 1. 测试登录(会记录日志)
print("1. 测试登录...")
login_response = requests.post(
    f'{BASE_URL}/auth/login',
    json={
        'account': 'admin',
        'password': 'admin123'
    }
)
print(f"登录响应: {login_response.status_code}")
if login_response.status_code == 200:
    token = login_response.json().get('data', {}).get('access_token')
    print(f"获取到token: {token[:20]}...")
    
    # 2. 查询日志列表
    print("\n2. 查询日志列表...")
    headers = {'Authorization': f'Bearer {token}'}
    logs_response = requests.get(
        f'{BASE_URL}/logs?page=1&pageSize=10',
        headers=headers
    )
    print(f"日志查询响应: {logs_response.status_code}")
    if logs_response.status_code == 200:
        data = logs_response.json().get('data', {})
        print(f"日志总数: {data.get('total')}")
        print(f"返回日志数: {len(data.get('list', []))}")
        
        # 打印最新的日志
        logs = data.get('list', [])
        if logs:
            print("\n最新日志:")
            latest_log = logs[0]
            print(json.dumps(latest_log, indent=2, ensure_ascii=False))
    
    # 3. 测试日志统计
    print("\n3. 测试日志统计...")
    stats_response = requests.get(
        f'{BASE_URL}/logs/statistics',
        headers=headers
    )
    print(f"统计响应: {stats_response.status_code}")
    if stats_response.status_code == 200:
        stats = stats_response.json().get('data', {})
        print(f"统计数据: {json.dumps(stats, indent=2, ensure_ascii=False)}")
else:
    print(f"登录失败: {login_response.text}")
