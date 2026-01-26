import re
from typing import Dict, List
from datetime import datetime

# ═══════════════════════════════════════════
# ⚠️ EDIT HERE: Detection Keywords
# ═══════════════════════════════════════════
# These are the exact phrases that indicate filter-deference.
# Inferred from FCA Final Notices (Nationwide, Barclays, Mako, Coinbase)
#
# TO ADD A KEYWORD:
# 1. Add a new line with format: "Human phrase": r"regex pattern",
# 2. Save file
# 3. Redeploy
# ═══════════════════════════════════════════

FILTER_DEFERENCE_PATTERNS = {
    "per policy": r"per policy",
    "per our policy": r"per our policy",
    "threshold not met": r"threshold not met",
    "does not meet the threshold": r"does not meet the threshold",
    "below threshold": r"below (?:reporting )?threshold",
    "no requirement to": r"no requirement to",
    "not required to": r"not required to",
    "as per guidelines": r"as per guidelines",
    "in line with procedures": r"in line with procedures",
    "in line with standard practice": r"in line with standard practice",
    "no further action required": r"no further action required",
    "standard practice": r"standard practice",
    "consistent with our approach": r"consistent with our approach",
    "system recommendation": r"system recommendation",
    "automated review": r"automated review",
    "filter indicates": r"filter indicates",
}

# ═══════════════════════════════════════════
# ⚠️ EDIT HERE: Flagging Threshold
# ═══════════════════════════════════════════
# How many filter-deference phrases trigger a flag?
# Current: 1 (any instance flags)
# Increase if you want to require multiple instances
# ═══════════════════════════════════════════

FLAGGING_THRESHOLD = 1  # Number of patterns required to flag

# ═══════════════════════════════════════════
# ⛔ DO NOT EDIT: Core Detection Logic
# ═══════════════════════════════════════════
# This function handles the actual pattern matching
# Changing this could break the engine
# ═══════════════════════════════════════════

def detect_filter_deference(rationale: str) -> Dict:
    """
    Detects filter-deference language in analyst rationale.
    
    Args:
        rationale: The analyst's written justification for their decision
        
    Returns:
        Dictionary containing:
        - flagged: Boolean (True if filter-deference detected)
        - matches: List of detected human-readable phrases
        - match_count: Number of matches found
        - match_locations: List of context snippets showing where matches occurred
    """
    
    rationale_lower = rationale.lower()
    # Remove extra whitespace and newlines for better matching
    rationale_lower = ' '.join(rationale_lower.split())
    matches = []
    match_locations = []
    
    # Search for each pattern
    for human_phrase, regex_pattern in FILTER_DEFERENCE_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            matches.append(human_phrase)  # Return human phrase, not regex
            # Find all occurrences
            for match in re.finditer(regex_pattern, rationale_lower):
                match_locations.append({
                    'phrase': human_phrase,
                    'position': match.start(),
                    'context': rationale[max(0, match.start()-30):match.end()+30].strip()
                })
    
    match_count = len(matches)
    flagged = match_count >= FLAGGING_THRESHOLD
    
    return {
        'flagged': flagged,
        'matches': list(set(matches)),  # Remove duplicates, show human phrases
        'match_count': match_count,
        'match_locations': match_locations
    }

def generate_flag_explanation(detection_result: Dict, scenario_institution: str = "Multiple institutions") -> str:
    """
    Generates human-readable explanation of why rationale was flagged.
    
    Args:
        detection_result: Output from detect_filter_deference()
        scenario_institution: Name of institution for context
        
    Returns:
        String explanation for display to analyst
    """
    
    if not detection_result['flagged']:
        return "✅ No filter-deference detected. Rationale shows independent judgment."
    
    matches = detection_result['matches']
    count = detection_result['match_count']
    
    explanation = f"🚩 FILTER-DEFERENCE DETECTED\n\n"
    explanation += f"Your rationale contains {count} instance(s) of filter-deference language:\n\n"
    
    for i, match in enumerate(matches, 1):
        explanation += f"{i}. \"{match}\"\n"
    
    # Show context snippets
    if detection_result['match_locations']:
        explanation += "\n📍 CONTEXT:\n"
        for loc in detection_result['match_locations'][:3]:  # Show max 3 examples
            explanation += f"• ...{loc['context']}...\n"
    
    explanation += "\n⚠️ REGULATORY RISK:\n"
    explanation += "This reasoning structure appears in FCA enforcement findings where reliance on filters replaced independent judgment.\n\n"
    explanation += f"Relevant cases: Nationwide (£264.8M), Barclays (£72M), Mako/Coinbase (£3.5M+)\n\n"
    explanation += "This language pattern indicates judgment may have been outsourced to procedural filters."
    
    return explanation