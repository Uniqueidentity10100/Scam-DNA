"""
Main web page routes
"""

from flask import Blueprint, render_template, current_app
from app.models.database import get_db_connection, get_statistics
from app.services.prediction_service import PredictionService
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main dashboard page."""
    db_path = current_app.config['DATABASE']
    stats = get_statistics(db_path)
    return render_template('index.html', stats=stats)

@main_bp.route('/analyzer')
def analyzer():
    """Message analysis page."""
    return render_template('analyzer.html')

@main_bp.route('/timeline')
def timeline():
    """Evolution timeline page."""
    db_path = current_app.config['DATABASE']
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    # Get recent messages with family info
    cursor.execute('''
        SELECT m.*, f.name as family_name
        FROM messages m
        LEFT JOIN families f ON m.family_id = f.id
        ORDER BY m.analyzed_at DESC
        LIMIT 100
    ''')
    messages = [dict(row) for row in cursor.fetchall()]
    
    # Parse JSON fields for display
    for msg in messages:
        if msg['emotional_signals']:
            msg['emotional_signals'] = json.loads(msg['emotional_signals'])
        if msg['structural_markers']:
            msg['structural_markers'] = json.loads(msg['structural_markers'])
    
    conn.close()
    
    return render_template('timeline.html', messages=messages)

@main_bp.route('/families')
def families():
    """Scam families overview page."""
    db_path = current_app.config['DATABASE']
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT f.*, 
               COUNT(m.id) as total_messages,
               AVG(m.mutation_score) as avg_mutation
        FROM families f
        LEFT JOIN messages m ON f.id = m.family_id
        GROUP BY f.id
        ORDER BY f.last_seen DESC
    ''')
    families_list = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    
    return render_template('families.html', families=families_list)

@main_bp.route('/family/<int:family_id>')
def family_detail(family_id):
    """Detailed view of a specific scam family."""
    db_path = current_app.config['DATABASE']
    prediction_service = PredictionService(db_path)
    
    insights = prediction_service.generate_family_insights(family_id)
    
    return render_template('family_detail.html', insights=insights)

@main_bp.route('/insights')
def insights():
    """Global insights and predictions page."""
    db_path = current_app.config['DATABASE']
    prediction_service = PredictionService(db_path)
    
    global_insights = prediction_service.generate_global_insights()
    
    return render_template('insights.html', insights=global_insights)
