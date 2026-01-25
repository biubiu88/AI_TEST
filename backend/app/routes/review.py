"""
测试用例评审路由
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from app.models import TestCase, User, TestcaseReview, ReviewComment, ReviewTemplate, Prompt, Knowledge, LLMConfig
from app.services.ai_review_service import AIReviewServiceFactory
from app.middlewares import log_operation
import json

review_bp = Blueprint('review', __name__)


def make_response(code=0, message='success', data=None):
    """统一响应格式"""
    return jsonify({
        'code': code,
        'message': message,
        'data': data
    })


# ========== 评审管理接口 ==========

@review_bp.route('/list', methods=['GET'])
@jwt_required()
@log_operation
def get_reviews():
    """获取评审列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    testcase_id = request.args.get('testcase_id', type=int)
    reviewer_id = request.args.get('reviewer_id', type=int)
    status = request.args.get('status', '')
    keyword = request.args.get('keyword', '')
    
    query = TestcaseReview.query
    
    if testcase_id:
        query = query.filter(TestcaseReview.testcase_id == testcase_id)
    if reviewer_id:
        query = query.filter(TestcaseReview.reviewer_id == reviewer_id)
    if status:
        query = query.filter(TestcaseReview.status == status)
    if keyword:
        query = query.join(TestCase).filter(TestCase.title.contains(keyword))
    
    query = query.order_by(TestcaseReview.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return make_response(0, 'success', {
        'list': [item.to_dict() for item in pagination.items],
        'total': pagination.total,
        'page': page,
        'per_page': per_page
    })


@review_bp.route('/<int:review_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_review(review_id):
    """获取评审详情"""
    review = TestcaseReview.query.get_or_404(review_id)
    return make_response(0, 'success', review.to_dict())


@review_bp.route('/testcase/<int:testcase_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_testcase_reviews(testcase_id):
    """获取测试用例的所有评审"""
    reviews = TestcaseReview.query.filter_by(testcase_id=testcase_id).order_by(
        TestcaseReview.created_at.desc()
    ).all()
    
    return make_response(0, 'success', {
        'list': [item.to_dict() for item in reviews],
        'total': len(reviews)
    })


@review_bp.route('', methods=['POST'])
@jwt_required()
@log_operation
def create_review():
    """创建评审"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    testcase_id = data.get('testcase_id')
    if not testcase_id:
        return make_response(400, '测试用例ID不能为空')
    
    # 检查测试用例是否存在
    testcase = TestCase.query.get(testcase_id)
    if not testcase:
        return make_response(404, '测试用例不存在')
    
    # 检查是否已有待评审的记录
    existing_review = TestcaseReview.query.filter_by(
        testcase_id=testcase_id,
        reviewer_id=current_user_id,
        status='pending'
    ).first()
    
    if existing_review:
        return make_response(400, '该测试用例已有待评审记录')
    
    review = TestcaseReview(
        testcase_id=testcase_id,
        reviewer_id=current_user_id,
        status='pending'
    )
    
    db.session.add(review)
    db.session.commit()
    
    return make_response(0, '创建成功', review.to_dict())


@review_bp.route('/<int:review_id>', methods=['PUT'])
@jwt_required()
@log_operation
def update_review(review_id):
    """更新评审（提交评审结果）"""
    current_user_id = get_jwt_identity()
    review = TestcaseReview.query.get_or_404(review_id)
    
    # 检查权限：只有评审人可以更新
    if review.reviewer_id != current_user_id:
        return make_response(403, '无权限操作此评审')
    
    data = request.get_json()
    
    # 更新评审结果
    if 'status' in data:
        review.status = data['status']
        if data['status'] != 'pending':
            review.reviewed_at = datetime.utcnow()
    
    if 'overall_rating' in data:
        review.overall_rating = data['overall_rating']
    
    if 'comments' in data:
        review.comments = data['comments']
    
    if 'improvement_suggestions' in data:
        review.improvement_suggestions = data['improvement_suggestions']
    
    if 'clarity_score' in data:
        review.clarity_score = data['clarity_score']
    
    if 'completeness_score' in data:
        review.completeness_score = data['completeness_score']
    
    if 'feasibility_score' in data:
        review.feasibility_score = data['feasibility_score']
    
    if 'coverage_score' in data:
        review.coverage_score = data['coverage_score']
    
    db.session.commit()
    
    return make_response(0, '更新成功', review.to_dict())


@review_bp.route('/<int:review_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_review(review_id):
    """删除评审"""
    current_user_id = get_jwt_identity()
    review = TestcaseReview.query.get_or_404(review_id)
    
    # 检查权限：只有评审人可以删除
    if review.reviewer_id != current_user_id:
        return make_response(403, '无权限操作此评审')
    
    db.session.delete(review)
    db.session.commit()
    
    return make_response(0, '删除成功')


@review_bp.route('/batch', methods=['POST'])
@jwt_required()
@log_operation
def batch_create_reviews():
    """批量创建评审"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    testcase_ids = data.get('testcase_ids', [])
    
    if not testcase_ids:
        return make_response(400, '测试用例ID列表不能为空')
    
    created_reviews = []
    for testcase_id in testcase_ids:
        testcase = TestCase.query.get(testcase_id)
        if not testcase:
            continue
        
        # 检查是否已有待评审的记录
        existing_review = TestcaseReview.query.filter_by(
            testcase_id=testcase_id,
            reviewer_id=current_user_id,
            status='pending'
        ).first()
        
        if not existing_review:
            review = TestcaseReview(
                testcase_id=testcase_id,
                reviewer_id=current_user_id,
                status='pending'
            )
            db.session.add(review)
            created_reviews.append(review)
    
    db.session.commit()
    
    return make_response(0, f'成功创建 {len(created_reviews)} 条评审记录', {
        'count': len(created_reviews),
        'list': [r.to_dict() for r in created_reviews]
    })


# ========== 评审评论接口 ==========

@review_bp.route('/<int:review_id>/comments', methods=['GET'])
@jwt_required()
@log_operation
def get_comments(review_id):
    """获取评审的评论列表"""
    review = TestcaseReview.query.get_or_404(review_id)
    comments = ReviewComment.query.filter_by(review_id=review_id).order_by(
        ReviewComment.created_at.asc()
    ).all()
    
    return make_response(0, 'success', [c.to_dict() for c in comments])


@review_bp.route('/<int:review_id>/comments', methods=['POST'])
@jwt_required()
@log_operation
def add_comment(review_id):
    """添加评论"""
    current_user_id = get_jwt_identity()
    review = TestcaseReview.query.get_or_404(review_id)
    
    data = request.get_json()
    content = data.get('content', '').strip()
    
    if not content:
        return make_response(400, '评论内容不能为空')
    
    comment = ReviewComment(
        review_id=review_id,
        user_id=current_user_id,
        content=content,
        is_reply=data.get('is_reply', False),
        parent_id=data.get('parent_id')
    )
    
    db.session.add(comment)
    db.session.commit()
    
    return make_response(0, '添加成功', comment.to_dict())


@review_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_comment(comment_id):
    """删除评论"""
    current_user_id = get_jwt_identity()
    comment = ReviewComment.query.get_or_404(comment_id)
    
    # 检查权限：只有评论人可以删除
    if comment.user_id != current_user_id:
        return make_response(403, '无权限删除此评论')
    
    db.session.delete(comment)
    db.session.commit()
    
    return make_response(0, '删除成功')


# ========== 评审模板接口 ==========

@review_bp.route('/templates', methods=['GET'])
@jwt_required()
@log_operation
def get_templates():
    """获取评审模板列表"""
    templates = ReviewTemplate.query.filter_by(is_active=True).all()
    return make_response(0, 'success', [t.to_dict() for t in templates])


@review_bp.route('/templates/<int:template_id>', methods=['GET'])
@jwt_required()
@log_operation
def get_template(template_id):
    """获取评审模板详情"""
    template = ReviewTemplate.query.get_or_404(template_id)
    return make_response(0, 'success', template.to_dict())


@review_bp.route('/templates', methods=['POST'])
@jwt_required()
@log_operation
def create_template():
    """创建评审模板"""
    data = request.get_json()
    
    template = ReviewTemplate(
        name=data.get('name'),
        description=data.get('description', ''),
        category=data.get('category', 'general'),
        checklist=json.dumps(data.get('checklist', []), ensure_ascii=False),
        scoring_criteria=json.dumps(data.get('scoring_criteria', {}), ensure_ascii=False),
        is_default=data.get('is_default', False),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(template)
    db.session.commit()
    
    return make_response(0, '创建成功', template.to_dict())


@review_bp.route('/templates/<int:template_id>', methods=['PUT'])
@jwt_required()
@log_operation
def update_template(template_id):
    """更新评审模板"""
    template = ReviewTemplate.query.get_or_404(template_id)
    data = request.get_json()
    
    if 'name' in data:
        template.name = data['name']
    if 'description' in data:
        template.description = data['description']
    if 'category' in data:
        template.category = data['category']
    if 'checklist' in data:
        template.checklist = json.dumps(data['checklist'], ensure_ascii=False)
    if 'scoring_criteria' in data:
        template.scoring_criteria = json.dumps(data['scoring_criteria'], ensure_ascii=False)
    if 'is_default' in data:
        template.is_default = data['is_default']
    if 'is_active' in data:
        template.is_active = data['is_active']
    
    template.updated_at = datetime.utcnow()
    db.session.commit()
    
    return make_response(0, '更新成功', template.to_dict())


@review_bp.route('/templates/<int:template_id>', methods=['DELETE'])
@jwt_required()
@log_operation
def delete_template(template_id):
    """删除评审模板"""
    template = ReviewTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    
    return make_response(0, '删除成功')


# ========== 统计接口 ==========

@review_bp.route('/stats', methods=['GET'])
@jwt_required()
@log_operation
def get_stats():
    """获取评审统计"""
    total = TestcaseReview.query.count()
    pending = TestcaseReview.query.filter_by(status='pending').count()
    approved = TestcaseReview.query.filter_by(status='approved').count()
    rejected = TestcaseReview.query.filter_by(status='rejected').count()
    need_revision = TestcaseReview.query.filter_by(status='need_revision').count()
    
    # 计算平均评分
    avg_rating = db.session.query(
        db.func.avg(TestcaseReview.overall_rating)
    ).filter(TestcaseReview.overall_rating.isnot(None)).scalar()
    
    return make_response(0, 'success', {
        'total': total,
        'pending': pending,
        'approved': approved,
        'rejected': rejected,
        'need_revision': need_revision,
        'avg_rating': round(avg_rating, 2) if avg_rating else 0,
        'approval_rate': round(approved / total * 100, 2) if total > 0 else 0
    })


# ========== AI评审接口 ==========

@review_bp.route('/ai-review', methods=['POST'])
@jwt_required()
@log_operation
def ai_review():
    """AI自动评审测试用例"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    testcase_ids = data.get('testcase_ids', [])
    if not testcase_ids:
        return make_response(400, '请选择要评审的测试用例')
    
    # 获取测试用例
    testcases = TestCase.query.filter(TestCase.id.in_(testcase_ids)).all()
    if not testcases:
        return make_response(404, '未找到测试用例')
    
    # 转换为字典格式
    testcase_list = [tc.to_dict() for tc in testcases]
    
    # 获取提示词和知识库
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
    
    # 获取AI服务实例
    llm_config_id = data.get('llm_config_id')
    if llm_config_id:
        ai_service = AIReviewServiceFactory.create_from_config_id(llm_config_id)
    else:
        ai_service = AIReviewServiceFactory.get_default_service()
    
    # 评审选项
    options = {
        'review_dimensions': data.get('review_dimensions', ['clarity', 'completeness', 'feasibility', 'coverage']),
        'scoring_criteria': data.get('scoring_criteria', {}),
        'count': len(testcase_list)
    }
    
    try:
        # 调用AI评审
        reviews = ai_service.review_testcases(testcase_list, options, prompt_content, knowledge_contents)
        
        # 保存评审结果
        saved_reviews = []
        for review_data in reviews:
            # 查找对应的测试用例ID
            testcase_id = review_data.get('testcase_id')
            if not testcase_id:
                continue
            
            # 检查是否已有该用户的评审记录
            existing_review = TestcaseReview.query.filter_by(
                testcase_id=testcase_id,
                reviewer_id=current_user_id,
                status='pending'
            ).first()
            
            if existing_review:
                # 更新现有评审
                existing_review.status = review_data.get('status', 'approved')
                existing_review.overall_rating = review_data.get('overall_rating', 3)
                existing_review.comments = review_data.get('comments', '')
                existing_review.improvement_suggestions = review_data.get('improvement_suggestions', '')
                existing_review.clarity_score = review_data.get('clarity_score', 3)
                existing_review.completeness_score = review_data.get('completeness_score', 3)
                existing_review.feasibility_score = review_data.get('feasibility_score', 3)
                existing_review.coverage_score = review_data.get('coverage_score', 3)
                existing_review.reviewed_at = datetime.utcnow()
                saved_reviews.append(existing_review)
            else:
                # 创建新评审
                review = TestcaseReview(
                    testcase_id=testcase_id,
                    reviewer_id=current_user_id,
                    status=review_data.get('status', 'approved'),
                    overall_rating=review_data.get('overall_rating', 3),
                    comments=review_data.get('comments', ''),
                    improvement_suggestions=review_data.get('improvement_suggestions', ''),
                    clarity_score=review_data.get('clarity_score', 3),
                    completeness_score=review_data.get('completeness_score', 3),
                    feasibility_score=review_data.get('feasibility_score', 3),
                    coverage_score=review_data.get('coverage_score', 3),
                    reviewed_at=datetime.utcnow()
                )
                db.session.add(review)
                saved_reviews.append(review)
        
        db.session.commit()
        
        return make_response(0, f'AI评审完成，共评审 {len(saved_reviews)} 条用例', {
            'count': len(saved_reviews),
            'reviews': [r.to_dict() for r in saved_reviews]
        })
        
    except Exception as e:
        current_app.logger.error(f'AI评审失败: {str(e)}')
        return make_response(500, f'AI评审失败: {str(e)}'), 500


@review_bp.route('/ai-review-preview', methods=['POST'])
@jwt_required()
@log_operation
def ai_review_preview():
    """AI评审预览（不保存）"""
    data = request.get_json()
    
    testcase_ids = data.get('testcase_ids', [])
    if not testcase_ids:
        return make_response(400, '请选择要评审的测试用例')
    
    # 获取测试用例
    testcases = TestCase.query.filter(TestCase.id.in_(testcase_ids)).all()
    if not testcases:
        return make_response(404, '未找到测试用例')
    
    # 转换为字典格式
    testcase_list = [tc.to_dict() for tc in testcases]
    
    # 获取提示词和知识库
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
    
    # 获取AI服务实例
    llm_config_id = data.get('llm_config_id')
    if llm_config_id:
        ai_service = AIReviewServiceFactory.create_from_config_id(llm_config_id)
    else:
        ai_service = AIReviewServiceFactory.get_default_service()
    
    # 评审选项
    options = {
        'review_dimensions': data.get('review_dimensions', ['clarity', 'completeness', 'feasibility', 'coverage']),
        'scoring_criteria': data.get('scoring_criteria', {}),
        'count': len(testcase_list)
    }
    
    try:
        # 调用AI评审
        reviews = ai_service.review_testcases(testcase_list, options, prompt_content, knowledge_contents)
        
        return make_response(0, 'AI评审预览成功', {
            'reviews': reviews
        })
        
    except Exception as e:
        current_app.logger.error(f'AI评审预览失败: {str(e)}')
        return make_response(500, f'AI评审预览失败: {str(e)}'), 500
