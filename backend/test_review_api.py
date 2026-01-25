"""
测试用例评审功能
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_review_api():
    """测试评审API"""
    print("="*50)
    print("测试用例评审功能")
    print("="*50)
    
    # 1. 登录获取token
    print("\n1. 登录...")
    login_response = requests.post(f'{BASE_URL}/auth/login', json={
        'username': 'admin',
        'password': 'admin123'
    })
    
    if login_response.status_code == 200:
        data = login_response.json()
        token = data['data']['access_token']
        print(f"✓ 登录成功, Token: {token[:20]}...")
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
    else:
        print(f"✗ 登录失败: {login_response.text}")
        return
    
    # 2. 获取测试用例列表
    print("\n2. 获取测试用例列表...")
    testcase_response = requests.get(
        f'{BASE_URL}/testcases',
        headers=headers,
        params={'per_page': 5}
    )
    
    if testcase_response.status_code == 200:
        testcases = testcase_response.json()['data']['list']
        print(f"✓ 获取到 {len(testcases)} 条测试用例")
        
        if testcases:
            testcase_id = testcases[0]['id']
            print(f"  - 选择测试用例: {testcases[0]['title']} (ID: {testcase_id})")
        else:
            print("✗ 没有测试用例，请先创建测试用例")
            return
    else:
        print(f"✗ 获取测试用例失败: {testcase_response.text}")
        return
    
    # 3. 创建评审
    print("\n3. 创建评审...")
    create_review_response = requests.post(
        f'{BASE_URL}/reviews',
        headers=headers,
        json={
            'testcase_id': testcase_id
        }
    )
    
    if create_review_response.status_code == 200:
        review = create_review_response.json()['data']
        print(f"✓ 创建评审成功 (ID: {review['id']})")
        review_id = review['id']
    else:
        print(f"✗ 创建评审失败: {create_review_response.text}")
        return
    
    # 4. 提交评审结果
    print("\n4. 提交评审结果...")
    update_review_response = requests.put(
        f'{BASE_URL}/reviews/{review_id}',
        headers=headers,
        json={
            'status': 'approved',
            'overall_rating': 4,
            'comments': '测试用例结构清晰，步骤完整，预期结果明确。',
            'improvement_suggestions': '建议增加边界值测试场景',
            'clarity_score': 4,
            'completeness_score': 4,
            'feasibility_score': 5,
            'coverage_score': 3
        }
    )
    
    if update_review_response.status_code == 200:
        print("✓ 提交评审结果成功")
    else:
        print(f"✗ 提交评审结果失败: {update_review_response.text}")
        return
    
    # 5. 获取评审列表
    print("\n5. 获取评审列表...")
    list_response = requests.get(
        f'{BASE_URL}/reviews/list',
        headers=headers,
        params={'per_page': 10}
    )
    
    if list_response.status_code == 200:
        reviews = list_response.json()['data']['list']
        print(f"✓ 获取评审列表成功，共 {reviews['total']} 条记录")
    else:
        print(f"✗ 获取评审列表失败: {list_response.text}")
        return
    
    # 6. 获取评审详情
    print("\n6. 获取评审详情...")
    detail_response = requests.get(
        f'{BASE_URL}/reviews/{review_id}',
        headers=headers
    )
    
    if detail_response.status_code == 200:
        review_detail = detail_response.json()['data']
        print(f"✓ 获取评审详情成功")
        print(f"  - 状态: {review_detail['status']}")
        print(f"  - 整体评分: {review_detail['overall_rating']}")
        print(f"  - 评审意见: {review_detail['comments'][:50]}...")
    else:
        print(f"✗ 获取评审详情失败: {detail_response.text}")
        return
    
    # 7. 添加评论
    print("\n7. 添加评论...")
    add_comment_response = requests.post(
        f'{BASE_URL}/reviews/{review_id}/comments',
        headers=headers,
        json={
            'content': '同意评审意见，会尽快改进测试用例。'
        }
    )
    
    if add_comment_response.status_code == 200:
        print("✓ 添加评论成功")
    else:
        print(f"✗ 添加评论失败: {add_comment_response.text}")
        return
    
    # 8. 获取评论列表
    print("\n8. 获取评论列表...")
    comments_response = requests.get(
        f'{BASE_URL}/reviews/{review_id}/comments',
        headers=headers
    )
    
    if comments_response.status_code == 200:
        comments = comments_response.json()
        print(f"✓ 获取评论列表成功，共 {len(comments)} 条评论")
    else:
        print(f"✗ 获取评论列表失败: {comments_response.text}")
        return
    
    # 9. 获取评审统计
    print("\n9. 获取评审统计...")
    stats_response = requests.get(
        f'{BASE_URL}/reviews/stats',
        headers=headers
    )
    
    if stats_response.status_code == 200:
        stats = stats_response.json()['data']
        print("✓ 获取评审统计成功")
        print(f"  - 总评审数: {stats['total']}")
        print(f"  - 待评审: {stats['pending']}")
        print(f"  - 已通过: {stats['approved']}")
        print(f"  - 已拒绝: {stats['rejected']}")
        print(f"  - 需要修改: {stats['need_revision']}")
        print(f"  - 平均评分: {stats['avg_rating']}")
        print(f"  - 通过率: {stats['approval_rate']}%")
    else:
        print(f"✗ 获取评审统计失败: {stats_response.text}")
        return
    
    # 10. 获取评审模板
    print("\n10. 获取评审模板...")
    templates_response = requests.get(
        f'{BASE_URL}/reviews/templates',
        headers=headers
    )
    
    if templates_response.status_code == 200:
        templates = templates_response.json()
        print(f"✓ 获取评审模板成功，共 {len(templates)} 个模板")
        if templates:
            print(f"  - 默认模板: {templates[0]['name']}")
    else:
        print(f"✗ 获取评审模板失败: {templates_response.text}")
        return
    
    print("\n" + "="*50)
    print("✓ 所有测试通过！")
    print("="*50)


if __name__ == '__main__':
    try:
        test_review_api()
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
