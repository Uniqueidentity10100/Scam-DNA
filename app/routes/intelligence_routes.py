"""
Intelligence routes for Version 2.0 features
"""
from flask import Blueprint, render_template, request, jsonify, current_app
from ..intelligence.intelligence_controller import IntelligenceController
import os

bp = Blueprint('intelligence', __name__, url_prefix='/intelligence')

# Initialize controller lazily to use app config
def get_controller():
    """Get or create intelligence controller with correct database path."""
    if not hasattr(bp, '_controller'):
        bp._controller = IntelligenceController()
    return bp._controller


# Behavioral Analysis Routes
@bp.route('/playbook/<int:family_id>')
def playbook(family_id):
    """Display attack playbook for a family."""
    playbook_data = get_controller().behavior.get_family_playbook(family_id)
    return render_template('intelligence/playbook_view.html', 
                         family_id=family_id,
                         playbook=playbook_data)


@bp.route('/api/behavior/stage/<int:message_id>')
def analyze_stage(message_id):
    """API: Get behavioral stage classification."""
    result = get_controller().behavior.classify_stage(message_id)
    return jsonify(result)


# Network Analysis Routes
@bp.route('/network')
def network_graph():
    """Display scam network visualization."""
    controller = get_controller()
    graph_data = controller.network.get_network_graph()
    
    # Check if there's any data
    if not graph_data.get('nodes'):
        return render_template('intelligence/network_empty.html')
    
    hubs = controller.network.identify_hubs()
    spreaders = controller.network.detect_fast_spreaders()
    
    return render_template('intelligence/network_graph.html',
                         graph=graph_data,
                         hubs=hubs,
                         spreaders=spreaders)


@bp.route('/api/network/build')
def build_network():
    """API: Rebuild network relationships."""
    result = get_controller().network.build_network()
    return jsonify(result)


# Confidence Scoring Routes
@bp.route('/confidence/<int:message_id>')
def confidence_display(message_id):
    """Display multi-dimensional confidence scores."""
    scores = get_controller().confidence.calculate_scores(message_id)
    return render_template('intelligence/confidence_display.html',
                         message_id=message_id,
                         scores=scores)


# Evolution Replay Routes
@bp.route('/evolution/<int:family_id>')
def evolution_replay(family_id):
    """Display mutation timeline with step-through."""
    timeline = get_controller().evolution.get_family_timeline(family_id)
    return render_template('intelligence/evolution_replay.html',
                         family_id=family_id,
                         timeline=timeline)


@bp.route('/api/evolution/step/<int:family_id>/<int:step>')
def evolution_step(family_id, step):
    """API: Get detailed view of evolution step."""
    detail = get_controller().evolution.get_step_detail(family_id, step)
    return jsonify(detail)


# Regional Analysis Routes
@bp.route('/regional')
def regional_comparison():
    """Display regional adaptation analysis."""
    # Get all families with regional profiles
    regions = get_controller().region.compare_regions()
    return render_template('intelligence/regional_comparison.html',
                         comparison=regions)


@bp.route('/api/regional/classify/<int:message_id>')
def classify_region(message_id):
    """API: Classify message regional target."""
    result = get_controller().region.classify_region(message_id)
    return jsonify(result)


# Counter-Strategy Routes
@bp.route('/protection/<int:message_id>')
def protection_playbook(message_id):
    """Display counter-strategy playbook."""
    countermeasures = get_controller().counter.generate_countermeasures(message_id)
    return render_template('intelligence/protection_playbook.html',
                         message_id=message_id,
                         countermeasures=countermeasures)


# Evidence Locker Routes
@bp.route('/evidence')
def evidence_locker():
    """Display all evidence records."""
    controller = get_controller()
    records = controller.evidence.list_evidence_records(limit=100)
    
    # Check if there's any data
    if records['total_count'] == 0:
        return render_template('intelligence/evidence_empty.html')
    
    return render_template('intelligence/evidence_locker.html',
                         records=records)


@bp.route('/evidence/<case_id>')
def evidence_detail(case_id):
    """Display specific evidence record."""
    record = get_controller().evidence.get_evidence_record(case_id)
    return render_template('intelligence/evidence_detail.html',
                         record=record)


@bp.route('/api/evidence/create/<int:message_id>', methods=['POST'])
def create_evidence(message_id):
    """API: Create forensic evidence record."""
    result = get_controller().evidence.create_evidence_record(message_id)
    return jsonify(result)


@bp.route('/api/evidence/report/<case_id>')
def evidence_report(case_id):
    """API: Generate case report (exportable)."""
    report = get_controller().evidence.generate_case_report(case_id)
    return jsonify(report)


# Institutional Dashboard Routes
@bp.route('/dashboard')
def institutional_dashboard():
    """Display institutional analytics dashboard."""
    controller = get_controller()
    metrics = controller.institution.get_dashboard_metrics(days=7)
    
    # Check if there's any data
    if metrics['overview']['total_messages_period'] == 0:
        return render_template('intelligence/dashboard_empty.html')
    
    awareness = controller.institution.generate_awareness_report()
    
    return render_template('intelligence/institutional_dashboard.html',
                         metrics=metrics,
                         awareness=awareness)


@bp.route('/api/institutional/report')
def export_report():
    """API: Generate exportable summary report."""
    days = request.args.get('days', default=30, type=int)
    report = get_controller().institution.export_summary_report(days)
    return jsonify(report)


# Full Intelligence Analysis
@bp.route('/api/analyze/<int:message_id>')
def full_analysis(message_id):
    """API: Run complete intelligence analysis on message."""
    result = get_controller().analyze_full_intelligence(message_id)
    return jsonify(result)
