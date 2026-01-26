import json
import csv
from io import StringIO
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# ═══════════════════════════════════════════
# Append-Only Audit Log
# ═══════════════════════════════════════════
# This is append-only logging for evidentiary purposes.
# NOT cryptographically immutable.
# NOT production compliance infrastructure.
# ═══════════════════════════════════════════

AUDIT_LOG_FILE = Path("audit_log.jsonl")

def log_analysis(
    scenario_id: str,
    rationale: str,
    detection_result: Dict,
    analyst_id: str = "DEMO_ANALYST"
) -> None:
    """
    Logs analysis to append-only audit trail.
    
    Args:
        scenario_id: Identifier for the scenario analyzed
        rationale: The analyst's written rationale
        detection_result: Output from detection_engine
        analyst_id: Identifier for the analyst (default: DEMO_ANALYST)
    """
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "RATIONALE_ANALYSIS",
        "scenario_id": scenario_id,
        "analyst_id": analyst_id,
        "rationale": rationale,
        "rationale_length_words": len(rationale.split()),
        "flagged": detection_result['flagged'],
        "matches": detection_result['matches'],
        "match_count": detection_result['match_count']
    }
    
    # Append to JSONL file (one JSON object per line)
    with open(AUDIT_LOG_FILE, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

def log_validation_session(
    qa_head_id: str,
    scenarios_reviewed: List[str],
    validation_responses: Dict[str, bool],
    additional_notes: str,
    positive_cases: int,
    negative_cases: int
) -> None:
    """
    Logs QA validation session as append-only evidence.
    
    This is evidentiary logging for expert validation, NOT production compliance.
    Each validation session is logged to demonstrate that expert review occurred.
    
    Args:
        qa_head_id: Name/ID of QA head conducting validation
        scenarios_reviewed: List of scenario IDs reviewed
        validation_responses: Dictionary of Yes/No responses to validation questions
        additional_notes: Free-text observations from QA head
        positive_cases: Number of filter-deference scenarios tested
        negative_cases: Number of clean rationales tested
    """
    
    validation_entry = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "VALIDATION_SESSION",
        "qa_head_id": qa_head_id,
        "scenarios_reviewed": scenarios_reviewed,
        "positive_cases_tested": positive_cases,
        "negative_cases_tested": negative_cases,
        "validation_responses": validation_responses,
        "additional_notes": additional_notes,
        "validation_outcome": "PASSED" if all(validation_responses.values()) else "PARTIAL"
    }
    
    with open(AUDIT_LOG_FILE, 'a') as f:
        f.write(json.dumps(validation_entry) + '\n')

def get_recent_logs(limit: int = 10) -> List[Dict]:
    """
    Retrieves most recent log entries.
    
    Args:
        limit: Maximum number of entries to return
        
    Returns:
        List of log entry dictionaries
    """
    
    if not AUDIT_LOG_FILE.exists():
        return []
    
    logs = []
    with open(AUDIT_LOG_FILE, 'r') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    # Return most recent first
    return logs[-limit:][::-1]

def export_to_csv() -> str:
    """
    Exports audit log to CSV format for external review.
    
    Returns:
        CSV string containing all log entries
    """
    
    if not AUDIT_LOG_FILE.exists():
        return "timestamp,event_type,details\n(No logs recorded yet)"
    
    logs = []
    with open(AUDIT_LOG_FILE, 'r') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    if not logs:
        return "timestamp,event_type,details\n(No logs recorded yet)"
    
    # Create CSV in memory
    output = StringIO()
    
    # Determine all possible fields
    fieldnames = set()
    for log in logs:
        fieldnames.update(log.keys())
    
    fieldnames = sorted(fieldnames)
    
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    
    for log in logs:
        # Flatten nested dicts for CSV
        flat_log = {}
        for key, value in log.items():
            if isinstance(value, (dict, list)):
                flat_log[key] = json.dumps(value)
            else:
                flat_log[key] = value
        writer.writerow(flat_log)
    
    return output.getvalue()

def get_statistics() -> Dict:
    """
    Calculates aggregate statistics from audit log.
    
    Returns:
        Dictionary with:
        - total_analyses
        - total_flagged
        - flag_rate
        - total_validations
        - validations_passed
    """
    
    if not AUDIT_LOG_FILE.exists():
        return {
            "total_analyses": 0,
            "total_flagged": 0,
            "flag_rate": 0.0,
            "total_validations": 0,
            "validations_passed": 0
        }
    
    logs = []
    with open(AUDIT_LOG_FILE, 'r') as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    analyses = [log for log in logs if log.get('event_type') == 'RATIONALE_ANALYSIS']
    validations = [log for log in logs if log.get('event_type') == 'VALIDATION_SESSION']
    
    total_analyses = len(analyses)
    flagged = sum(1 for log in analyses if log.get('flagged'))
    
    total_validations = len(validations)
    validations_passed = sum(1 for log in validations if log.get('validation_outcome') == 'PASSED')
    
    return {
        "total_analyses": total_analyses,
        "total_flagged": flagged,
        "flag_rate": (flagged / total_analyses * 100) if total_analyses > 0 else 0.0,
        "total_validations": total_validations,
        "validations_passed": validations_passed
    }