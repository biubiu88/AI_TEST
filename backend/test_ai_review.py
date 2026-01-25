"""
测试AI评审功能
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_ai_review():
    """测试AI评审API"""
    print("="*50)
    print("测试AI评审功能")
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
        params={'per_page': 3}
    )
    
    if testcase_response.status_code == 200:
        testcases = testcase_response.json()['data']['list']
        print(f"✓ 获取到 {len(testcases)} 条测试用例")
        
        if testcases:
            testcase_ids = [tc['id'] for tc in testcases]
            print(f"  - 将评审用例ID: {testcase_ids}")
        else:
            print("✗ 没有测试用例，请先创建测试用例")
            return
    else:
        print(f"✗ 获取测试用例失败: {testcase_response.text}")
        return
    
    # 3. 获取大模型配置
    print("\n3. 获取大模型配置...")
    llm_response = requests.get(
        f'{BASE_URL}/llm-configs/all',
        headers=headers
    )
    
    if llm_response.status_code == 200:
        llm_configs = llm_response.json()
        print(f"✓ 获取到 {len(llm_configs)} 个大模型配置")
        
        if llm_configs:
            llm_config_id = llm_configs[0]['id']
            print(f"  - 使用模型: {llm_configs[0]['name']} (ID: {llm_config_id})")
        else:
            print("✗ 没有大模型配置，请先配置")
            return
    else:
        print(f"✗ 获取大模型配置失败: {llm_response.text}")
        return
    
    # 4. AI评审预览
    print("\n4. AI评审预览...")
    preview_data = {
        'testcase_ids': testcase_ids,
        'llm_config_id': llm_config_id
    }
    
    preview_response = requests.post(
        f'{BASE_URL}/reviews/ai-review-preview',
        headers=headers,
        json=preview_data
    )
    
    if preview_response.status_code == 200:
        preview_result = preview_response.json()
        print(f"✓ AI评审预览成功")
        reviews = preview_result['data']['reviews']
        print(f"  - 预览数量: {len(reviews)}")
        
        if reviews:
            print(f"  - 示例评审: 用例ID={reviews[0]['testcase_id']}, 状态={reviews[0]['status']}, 评分={reviews[0]['overall_rating']}")
    else:
        print(f"✗ AI评审预览失败: {preview_response.text}")
        return
    
    # 5. AI评审并保存
    print("\n5. AI评审并保存...")
    review_data = {
        'testcase_ids': testcase_ids,
        'llm_config_id': llm_config_id
    }
    
    review_response = requests.post(
        f'{BASE_URL}/reviews/ai-review',
        headers=headers,
        json=review_data
    )
    
    if review_response.status_code == 200:
        review_result = review_response.json()
        print(f"✓ AI评审完成")
        print(f"  - 评审数量: {review_result['data']['count']}")
        
        # 6. 验证评审结果
        print("\n6. 验证评审结果...")
        list_response = requests.get(
            f'{BASE_URL}/reviews/list',
            headers=headers,
            params={'per_page': 10}
        )
        
        if list_response.status_code == 200:
            reviews = list_response.json()['data']['list']
            print(f"✓ 获取评审列表成功，共 {reviews['total']} 条记录")
            
            # 显示最新的评审
            if reviews:
                latest_review = reviews[0]
                print(f"  - 最新评审: 用例={latest_review['testcase_title']}, 状态={latest_review['status']}, 评分={latest_review['overall_rating']}")
    else:
        print(f"✗ AI评审失败: {review_response.text}")
        return
    
    print("\n" + "="*50)
    print("✓ AI评审功能测试通过！")
    print("="*50)


if __name__ == '__main__':
    try:
        test_ai_review()
    except Exception as e:
        print(f"\n✗ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
