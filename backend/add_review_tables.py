"""
添加测试用例评审相关表
"""
import os
import sys
import pymysql
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', 'testcase_generator'),
    'charset': 'utf8mb4'
}


def add_review_tables():
    """添加评审相关表"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"\n=== 连接到数据库 {DB_CONFIG['database']} ===")
        
        # 创建测试用例评审表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS testcase_reviews (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评审ID',
                testcase_id INT NOT NULL COMMENT '测试用例ID',
                reviewer_id INT NOT NULL COMMENT '评审人ID',
                status VARCHAR(20) DEFAULT 'pending' COMMENT '评审状态: pending-待评审, approved-通过, rejected-拒绝, need_revision-需要修改',
                overall_rating INT COMMENT '整体评分: 1-5分',
                comments TEXT COMMENT '评审意见',
                improvement_suggestions TEXT COMMENT '改进建议',
                clarity_score INT COMMENT '清晰度评分: 1-5分',
                completeness_score INT COMMENT '完整性评分: 1-5分',
                feasibility_score INT COMMENT '可执行性评分: 1-5分',
                coverage_score INT COMMENT '覆盖度评分: 1-5分',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                reviewed_at DATETIME COMMENT '评审时间',
                FOREIGN KEY (testcase_id) REFERENCES testcases(id) ON DELETE CASCADE,
                FOREIGN KEY (reviewer_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_testcase_id (testcase_id),
                INDEX idx_reviewer_id (reviewer_id),
                INDEX idx_status (status),
                INDEX idx_created_at (created_at)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='测试用例评审表'
        """)
        print("创建表: testcase_reviews")
        
        # 创建评审评论表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_comments (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '评论ID',
                review_id INT NOT NULL COMMENT '评审ID',
                user_id INT NOT NULL COMMENT '评论人ID',
                content TEXT NOT NULL COMMENT '评论内容',
                is_reply BOOLEAN DEFAULT FALSE COMMENT '是否为回复',
                parent_id INT COMMENT '父评论ID（用于回复）',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                FOREIGN KEY (review_id) REFERENCES testcase_reviews(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                INDEX idx_review_id (review_id),
                INDEX idx_user_id (user_id),
                INDEX idx_parent_id (parent_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评审评论表'
        """)
        print("创建表: review_comments")
        
        # 创建评审模板表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS review_templates (
                id INT AUTO_INCREMENT PRIMARY KEY COMMENT '模板ID',
                name VARCHAR(100) NOT NULL COMMENT '模板名称',
                description VARCHAR(500) COMMENT '模板描述',
                category VARCHAR(50) DEFAULT 'general' COMMENT '分类: general/web/api/performance/security',
                checklist TEXT COMMENT '评审检查点JSON',
                scoring_criteria TEXT COMMENT '评分标准JSON',
                is_default BOOLEAN DEFAULT FALSE COMMENT '是否默认模板',
                is_active BOOLEAN DEFAULT TRUE COMMENT '是否启用',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
                INDEX idx_category (category),
                INDEX idx_is_default (is_default),
                INDEX idx_is_active (is_active)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='评审模板表'
        """)
        print("创建表: review_templates")
        
        # 插入默认评审模板
        cursor.execute("""
            INSERT INTO review_templates (name, description, category, checklist, scoring_criteria, is_default, is_active) VALUES
            ('通用测试用例评审模板', '适用于各类测试用例的通用评审模板', 'general',
             '[
                {"id": 1, "item": "用例标题是否清晰明确？", "required": true},
                {"id": 2, "item": "前置条件是否完整？", "required": true},
                {"id": 3, "item": "测试步骤是否清晰可执行？", "required": true},
                {"id": 4, "item": "预期结果是否明确可验证？", "required": true},
                {"id": 5, "item": "用例是否覆盖了需求的关键点？", "required": true},
                {"id": 6, "item": "用例优先级是否合理？", "required": false},
                {"id": 7, "item": "用例类型分类是否准确？", "required": false}
             ]',
             '{
                "clarity": {"name": "清晰度", "description": "用例描述是否清晰易懂", "max": 5},
                "completeness": {"name": "完整性", "description": "用例要素是否完整", "max": 5},
                "feasibility": {"name": "可执行性", "description": "用例是否可以被执行", "max": 5},
                "coverage": {"name": "覆盖度", "description": "用例覆盖范围是否充分", "max": 5}
             }',
             TRUE, TRUE),
            ('Web应用测试用例评审模板', '适用于Web应用的测试用例评审', 'web',
             '[
                {"id": 1, "item": "用例标题是否清晰明确？", "required": true},
                {"id": 2, "item": "前置条件是否完整？", "required": true},
                {"id": 3, "item": "测试步骤是否清晰可执行？", "required": true},
                {"id": 4, "item": "预期结果是否明确可验证？", "required": true},
                {"id": 5, "item": "是否考虑了浏览器兼容性？", "required": false},
                {"id": 6, "item": "是否考虑了响应式设计？", "required": false},
                {"id": 7, "item": "是否考虑了安全性测试？", "required": false},
                {"id": 8, "item": "是否考虑了性能测试？", "required": false}
             ]',
             '{
                "clarity": {"name": "清晰度", "description": "用例描述是否清晰易懂", "max": 5},
                "completeness": {"name": "完整性", "description": "用例要素是否完整", "max": 5},
                "feasibility": {"name": "可执行性", "description": "用例是否可以被执行", "max": 5},
                "coverage": {"name": "覆盖度", "description": "用例覆盖范围是否充分", "max": 5}
             }',
             FALSE, TRUE),
            ('API接口测试用例评审模板', '适用于API接口的测试用例评审', 'api',
             '[
                {"id": 1, "item": "用例标题是否清晰明确？", "required": true},
                {"id": 2, "item": "前置条件是否完整？", "required": true},
                {"id": 3, "item": "请求参数是否完整？", "required": true},
                {"id": 4, "item": "预期响应是否明确？", "required": true},
                {"id": 5, "item": "是否验证了响应状态码？", "required": true},
                {"id": 6, "item": "是否验证了响应数据结构？", "required": true},
                {"id": 7, "item": "是否考虑了异常场景？", "required": true},
                {"id": 8, "item": "是否考虑了权限验证？", "required": false}
             ]',
             '{
                "clarity": {"name": "清晰度", "description": "用例描述是否清晰易懂", "max": 5},
                "completeness": {"name": "完整性", "description": "用例要素是否完整", "max": 5},
                "feasibility": {"name": "可执行性", "description": "用例是否可以被执行", "max": 5},
                "coverage": {"name": "覆盖度", "description": "用例覆盖范围是否充分", "max": 5}
             }',
             FALSE, TRUE)
        """)
        print("插入默认评审模板")
        
        conn.commit()
        
        print("\n" + "="*50)
        print("评审相关表创建完成！")
        print("="*50)
        
    except Exception as e:
        print(f"\n错误: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    add_review_tables()
