"""
API routes for AJAX requests
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.analysis_service import AnalysisService
from app.models.database import get_db_connection
import json

api_bp = Blueprint('api', __name__)

@api_bp.route('/analyze', methods=['POST'])
def analyze_message():
    """
    Analyze a scam message and return results.
    
    Expected JSON:
        {
            "text": "message content to analyze"
        }
    """
    try:
        data = request.get_json()
        
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        
        if len(text) < 10:
            return jsonify({'error': 'Message too short for analysis'}), 400
        
        # Perform analysis
        db_path = current_app.config['DATABASE']
        analysis_service = AnalysisService(db_path)
        
        result = analysis_service.analyze_message(text)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get current system statistics."""
    try:
        db_path = current_app.config['DATABASE']
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Overall stats
        cursor.execute('SELECT COUNT(*) as count FROM messages')
        total_messages = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM families')
        total_families = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM mutations')
        total_mutations = cursor.fetchone()['count']
        
        # Category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM messages
            GROUP BY category
            ORDER BY count DESC
        ''')
        categories = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'total_messages': total_messages,
            'total_families': total_families,
            'total_mutations': total_mutations,
            'categories': categories
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/family/<int:family_id>/messages', methods=['GET'])
def get_family_messages(family_id):
    """Get all messages belonging to a family."""
    try:
        db_path = current_app.config['DATABASE']
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM messages
            WHERE family_id = ?
            ORDER BY analyzed_at ASC
        ''', (family_id,))
        
        messages = []
        for row in cursor.fetchall():
            msg = dict(row)
            # Parse JSON fields
            if msg['emotional_signals']:
                msg['emotional_signals'] = json.loads(msg['emotional_signals'])
            if msg['structural_markers']:
                msg['structural_markers'] = json.loads(msg['structural_markers'])
            if msg['linguistic_patterns']:
                msg['linguistic_patterns'] = json.loads(msg['linguistic_patterns'])
            # Don't include embedding vector in response (too large)
            msg.pop('embedding_vector', None)
            messages.append(msg)
        
        conn.close()
        
        return jsonify({
            'success': True,
            'messages': messages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/timeline-data', methods=['GET'])
def get_timeline_data():
    """Get data for timeline visualization."""
    try:
        db_path = current_app.config['DATABASE']
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        
        # Get messages grouped by date and family
        cursor.execute('''
            SELECT 
                DATE(m.analyzed_at) as date,
                f.name as family_name,
                f.id as family_id,
                COUNT(*) as count
            FROM messages m
            LEFT JOIN families f ON m.family_id = f.id
            GROUP BY DATE(m.analyzed_at), f.id
            ORDER BY date ASC
        ''')
        
        timeline_data = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': timeline_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
