"""
Feedback API for collecting migration feedback and training the system
"""
import os
from flask import Blueprint, request, jsonify
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

# Create Blueprint
feedback_bp = Blueprint('feedback', __name__, url_prefix='/api/feedback')

# Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    logger.warning("Supabase credentials not found - feedback collection disabled")
    supabase = None

@feedback_bp.route('/submit', methods=['POST'])
def submit_feedback():
    """
    Submit migration feedback
    
    Expected JSON structure:
    {
        "job_id": "uuid",
        "source_platform": "boomi|mulesoft|sterling",
        "overall_rating": 1-5,
        "documentation_quality_rating": 1-5,
        "iflow_quality_rating": 1-5,
        "what_worked_well": ["item1", "item2"],
        "what_needs_improvement": ["issue1", "issue2"],
        "manual_fixes_required": {...},
        "business_logic_preserved": true/false,
        "deployment_successful": true/false,
        "comments": "Free text feedback",
        ...
    }
    """
    if not supabase:
        return jsonify({
            'status': 'error',
            'message': 'Feedback system not configured'
        }), 500
    
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('job_id'):
            return jsonify({'status': 'error', 'message': 'job_id is required'}), 400
        
        if not data.get('source_platform'):
            return jsonify({'status': 'error', 'message': 'source_platform is required'}), 400
        
        # Insert feedback
        result = supabase.table('migration_feedback').insert(data).execute()
        
        logger.info(f"Feedback submitted for job {data['job_id']}, platform: {data['source_platform']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully',
            'feedback_id': result.data[0]['id'] if result.data else None
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@feedback_bp.route('/documentation', methods=['POST'])
def submit_documentation_feedback():
    """
    Submit documentation-specific feedback
    """
    if not supabase:
        return jsonify({'status': 'error', 'message': 'Feedback system not configured'}), 500
    
    try:
        data = request.json
        
        if not data.get('job_id'):
            return jsonify({'status': 'error', 'message': 'job_id is required'}), 400
        
        result = supabase.table('documentation_feedback').insert(data).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Documentation feedback submitted',
            'feedback_id': result.data[0]['id'] if result.data else None
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting documentation feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@feedback_bp.route('/component-mapping', methods=['POST'])
def submit_component_mapping_feedback():
    """
    Submit component mapping feedback
    
    Used when user corrects component mappings
    """
    if not supabase:
        return jsonify({'status': 'error', 'message': 'Feedback system not configured'}), 500
    
    try:
        data = request.json
        
        # Validate
        required = ['source_platform', 'source_component_type', 'mapping_correct']
        for field in required:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'{field} is required'}), 400
        
        result = supabase.table('component_mapping_feedback').insert(data).execute()
        
        return jsonify({
            'status': 'success',
            'message': 'Component mapping feedback submitted',
            'feedback_id': result.data[0]['id'] if result.data else None
        }), 201
        
    except Exception as e:
        logger.error(f"Error submitting component mapping feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@feedback_bp.route('/job/<job_id>', methods=['GET'])
def get_job_feedback(job_id):
    """
    Get all feedback for a specific job
    """
    if not supabase:
        return jsonify({'status': 'error', 'message': 'Feedback system not configured'}), 500
    
    try:
        # Get main feedback
        feedback = supabase.table('migration_feedback')\
            .select('*')\
            .eq('job_id', job_id)\
            .execute()
        
        # Get documentation feedback
        doc_feedback = supabase.table('documentation_feedback')\
            .select('*')\
            .eq('job_id', job_id)\
            .execute()
        
        # Get component mapping feedback
        component_feedback = supabase.table('component_mapping_feedback')\
            .select('*')\
            .eq('job_id', job_id)\
            .execute()
        
        return jsonify({
            'status': 'success',
            'feedback': feedback.data,
            'documentation_feedback': doc_feedback.data,
            'component_mapping_feedback': component_feedback.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving feedback: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@feedback_bp.route('/analytics/<source_platform>', methods=['GET'])
def get_platform_analytics(source_platform):
    """
    Get analytics for a specific platform
    """
    if not supabase:
        return jsonify({'status': 'error', 'message': 'Feedback system not configured'}), 500
    
    try:
        # Get recent feedback
        feedback = supabase.table('migration_feedback')\
            .select('overall_rating, documentation_quality_rating, iflow_quality_rating, deployment_successful')\
            .eq('source_platform', source_platform)\
            .order('created_at', desc=True)\
            .limit(100)\
            .execute()
        
        if not feedback.data:
            return jsonify({
                'status': 'success',
                'analytics': {
                    'total_count': 0,
                    'message': 'No feedback data available yet'
                }
            }), 200
        
        # Calculate metrics
        total = len(feedback.data)
        avg_overall = sum(f.get('overall_rating', 0) for f in feedback.data if f.get('overall_rating')) / total
        avg_doc = sum(f.get('documentation_quality_rating', 0) for f in feedback.data if f.get('documentation_quality_rating')) / total
        avg_iflow = sum(f.get('iflow_quality_rating', 0) for f in feedback.data if f.get('iflow_quality_rating')) / total
        success_rate = sum(1 for f in feedback.data if f.get('deployment_successful')) / total * 100
        
        return jsonify({
            'status': 'success',
            'analytics': {
                'platform': source_platform,
                'total_feedback_count': total,
                'avg_overall_rating': round(avg_overall, 2),
                'avg_documentation_rating': round(avg_doc, 2),
                'avg_iflow_rating': round(avg_iflow, 2),
                'success_rate_percent': round(success_rate, 1)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving analytics: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@feedback_bp.route('/learned-patterns', methods=['GET'])
def get_learned_patterns():
    """
    Get learned patterns ready for production use
    """
    if not supabase:
        return jsonify({'status': 'error', 'message': 'Feedback system not configured'}), 500
    
    try:
        platform = request.args.get('platform', 'boomi')
        
        patterns = supabase.table('learned_migration_patterns')\
            .select('*')\
            .eq('source_platform', platform)\
            .gte('confidence_score', 0.7)\
            .eq('status', 'validated')\
            .order('confidence_score', desc=True)\
            .limit(50)\
            .execute()
        
        return jsonify({
            'status': 'success',
            'patterns': patterns.data
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving learned patterns: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


