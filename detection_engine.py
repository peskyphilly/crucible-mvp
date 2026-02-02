import re
from typing import Dict, List, Optional
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
    "system flags": r"system flags",
    "system indicates": r"system indicates",
}

# ═══════════════════════════════════════════════════════════════════
# NEW MODULE 1: Evidence-of-Absence Lexicon (Phase 1.5)
# ═══════════════════════════════════════════════════════════════════
# Catches euphemized automation where "system" is buried in nominalizations
# Detects "aligns with parameters" instead of "system said"
# ═══════════════════════════════════════════════════════════════════

EUPHEMIZED_AUTOMATION_PATTERNS = {
    "aligns with parameters": r"aligns? with (?:automated |risk |system )*parameters",
    "consistent with parameters": r"consistent with (?:automated |risk |system )*parameters",
    "consistent with profile": r"consistent with (?:established |baseline |risk )*profile",
    "within parameters": r"within (?:acceptable |risk |normal |system )*parameters",
    "aligns with guidelines": r"aligns? with (?:system |automated )*guidelines",
    "within guidelines": r"within (?:acceptable |system )*(?:guidelines|timeframes)",
    "per system guidelines": r"per system guidelines",
    "meets parameters": r"meets (?:risk |system )*parameters",
    "satisfies parameters": r"satisfies (?:risk |system )*parameters",
    "within risk appetite": r"within (?:acceptable |our )*risk appetite",
    "control environment": r"control environment",
    "control framework": r"control framework",
    "risk framework": r"risk framework",
    "monitoring parameters": r"monitoring parameters",
    "screening criteria": r"screening criteria",
    "standard profile": r"standard (?:risk )*profile",
    "baseline profile": r"baseline (?:risk )*profile",
    "established profile": r"established (?:baseline |risk )*profile",
    "baseline assessment": r"baseline assessment",
}

EVIDENCE_OF_ABSENCE_PATTERNS = {
    "no flags": r"no flags?",
    "no alerts": r"no alerts?",
    "no hits": r"no hits?",
    "no concerns": r"no concerns?",
    "no red flags": r"no red flags?",
    "clean screening": r"clean screening",
    "clear screening": r"clear screening",
    "negative screening": r"negative screening",
    "nil returns": r"nil returns?",
}

# ═══════════════════════════════════════════════════════════════════
# NEW MODULE 2: Policy Inversion Patterns (Phase 1.5)
# ═══════════════════════════════════════════════════════════════════
# Catches when policy compliance is used to JUSTIFY inaction
# Rather than as a minimum standard
# ═══════════════════════════════════════════════════════════════════

POLICY_CITATION_PATTERNS = {
    "policy compliance": r"(?:complies with|meets|satisfies|adheres to|follows) (?:the )?(?:policy|procedure|requirement)",
    "in accordance with": r"in accordance with",
    "as per policy": r"as per (?:the )?(?:policy|procedure|guidelines|AML policy)",
    "per policy": r"per (?:the )?(?:AML )?(?:policy|procedure)",
    "under policy": r"under (?:the )?(?:policy|procedure)",
    "per procedure": r"per (?:the )?procedure",
    "policy section": r"(?:policy|procedure) (?:Section|section) [\d\.]+",
}

NEGATIVE_OUTCOME_PATTERNS = {
    "no escalation": r"no escalation",
    "not required": r"not required",
    "no further action": r"no further (?:action|review|investigation)",
    "standard monitoring": r"standard monitoring",
    "continue monitoring": r"continue (?:standard )?monitoring",
    "cleared": r"cleared?",
    "no restriction": r"no restriction",
    "acceptable": r"acceptable",
}

THRESHOLD_ABSOLUTISM_PATTERNS = {
    "below threshold": r"(?:is|are|was|were) (?:below|under|less than) (?:the )?(?:threshold|£?\d{1,3}(?:,\d{3})*(?:k)?)",
    "under threshold": r"(?:is|are|was|were) under (?:the )?(?:threshold|£?\d{1,3}(?:,\d{3})*(?:k)?)",
    "does not exceed": r"does not exceed (?:the )?(?:threshold|£?\d{1,3}(?:,\d{3})*(?:k)?)",
}

# ═══════════════════════════════════════════════════════════════════
# NEW MODULE 3: Distributive Warrant Patterns (Phase 1.5)
# ═══════════════════════════════════════════════════════════════════
# Catches part-to-whole fallacy: "each part is safe, therefore whole is safe"
# ═══════════════════════════════════════════════════════════════════

DISTRIBUTIVE_LEXICON = {
    "each": r"\beach\b",
    "per transaction": r"per transaction",
    "individual": r"individual (?:transaction|deposit|transfer|payment)",
    "any single": r"any single",
    "every": r"every (?:transaction|deposit|transfer|payment)",
    "respective": r"respective",
}

# ═══════════════════════════════════════════════════════════════════
# NEW MODULE 4: Quantity Parser Patterns (Phase 1.5)
# ═══════════════════════════════════════════════════════════════════
# Numerical patterns for aggregate blindness detection
# ═══════════════════════════════════════════════════════════════════

# Regex for extracting monetary amounts
MONEY_PATTERN = r"£?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K|thousand|million|M)?"
RANGE_PATTERN = r"£?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?\s*[-–to]\s*£?(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|K)?"

# Temporal/count patterns
COUNT_PATTERN = r"(\d+)\s*(?:deposits?|transactions?|transfers?|payments?)"
TEMPORAL_PATTERN = r"(\d+)\s*(?:days?|weeks?|months?|years?)"

# Aggregate markers
AGGREGATE_MARKERS = ["total", "aggregate", "sum", "combined", "overall", "in total", "totaling", "totalling"]

# ═══════════════════════════════════════════════════════════════════
# ORIGINAL: Flagging Configuration
# ═══════════════════════════════════════════════════════════════════

FLAGGING_THRESHOLD = 1  # Number of patterns required to flag

# ═══════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS: Substantive Analysis Detection
# ═══════════════════════════════════════════════════════════════════

SUBSTANTIVE_INDICATORS = [
    # Behavioral analysis
    r"behavio(?:u)?r", r"pattern", r"velocity", r"frequency", r"structuring", r"layering",
    r"smurfing", r"unusual", r"anomalous", r"atypical",
    
    # Intent/purpose assessment
    r"intent", r"purpose", r"source", r"origin", r"derivation", r"provenance",
    r"legitimate", r"plausible", r"credible", r"explanation",
    
    # Comparative context
    r"compared to", r"inconsistent with", r"deviation from", r"differs from",
    r"benchmark", r"expected", r"typical", r"normal",
    
    # Risk assessment
    r"risk", r"exposure", r"threat", r"vulnerability", r"concern", r"suspicious",
    r"questionable", r"high-risk", r"red flag", r"warning sign",
    
    # Jurisdictional/customer context
    r"jurisdiction", r"PEP", r"sanction", r"adverse media", r"reputation",
]

def has_substantive_analysis(text: str, proximity_window: int = 500) -> bool:
    """
    Checks if rationale contains substantive risk analysis.
    
    Args:
        text: The rationale text
        proximity_window: Character window to check for substantive indicators
        
    Returns:
        True if substantive analysis detected, False otherwise
    """
    text_lower = text.lower()
    
    # Procedural contexts that invalidate substantive indicators
    procedural_contexts = [
        r"risk parameters", r"risk appetite", r"risk profile", r"risk framework",
        r"control environment", r"baseline", r"established profile",
        r"standard (?:risk )?profile", r"normal parameters"
    ]
    
    for indicator in SUBSTANTIVE_INDICATORS:
        matches = list(re.finditer(indicator, text_lower))
        for match in matches:
            # Check if indicator is negated
            context_start = max(0, match.start() - 30)
            context_end = min(len(text_lower), match.end() + 30)
            context = text_lower[context_start:context_end]
            
            # Skip if negated
            if re.search(r"\b(?:not|no|neither|nor)\s+" + indicator, context):
                continue
            
            # Skip if in procedural context (like "risk parameters" vs "risk assessment")
            in_procedural_context = False
            for proc_pattern in procedural_contexts:
                if re.search(proc_pattern, context):
                    in_procedural_context = True
                    break
            
            if in_procedural_context:
                continue
                
            return True
    
    return False

# ═══════════════════════════════════════════════════════════════════
# NEW DETECTION FUNCTIONS: Modular Detection Logic
# ═══════════════════════════════════════════════════════════════════

def detect_euphemized_automation(rationale: str) -> Dict:
    """
    Detects euphemized automation language (Module 1).
    
    Catches "aligns with parameters" instead of "system said"
    """
    rationale_lower = rationale.lower()
    rationale_lower = ' '.join(rationale_lower.split())
    
    matches = []
    match_locations = []
    
    # Check euphemized system references
    for human_phrase, regex_pattern in EUPHEMIZED_AUTOMATION_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            matches.append(human_phrase)
            for match in re.finditer(regex_pattern, rationale_lower):
                match_locations.append({
                    'phrase': human_phrase,
                    'position': match.start(),
                    'context': rationale[max(0, match.start()-30):match.end()+30].strip()
                })
    
    # Check evidence-of-absence language
    for human_phrase, regex_pattern in EVIDENCE_OF_ABSENCE_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            # Only flag if NOT accompanied by substantive analysis
            if not has_substantive_analysis(rationale):
                matches.append(f"{human_phrase} (absence as proof)")
                for match in re.finditer(regex_pattern, rationale_lower):
                    match_locations.append({
                        'phrase': human_phrase,
                        'position': match.start(),
                        'context': rationale[max(0, match.start()-30):match.end()+30].strip()
                    })
    
    return {
        'flagged': len(matches) > 0,
        'matches': list(set(matches)),
        'match_count': len(matches),
        'match_locations': match_locations,
        'detection_type': 'EUPHEMIZED_AUTOMATION'
    }

def detect_policy_inversion(rationale: str) -> Dict:
    """
    Detects policy inversion patterns (Module 2).
    
    Catches when policy compliance is used to justify inaction
    rather than as a minimum standard.
    """
    rationale_lower = rationale.lower()
    rationale_lower = ' '.join(rationale_lower.split())
    
    matches = []
    match_locations = []
    
    has_policy_citation = False
    has_negative_outcome = False
    has_threshold_absolutism = False
    
    # Check for policy citations
    for human_phrase, regex_pattern in POLICY_CITATION_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            has_policy_citation = True
            matches.append(f"policy citation: {human_phrase}")
    
    # Check for negative outcomes
    for human_phrase, regex_pattern in NEGATIVE_OUTCOME_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            has_negative_outcome = True
            matches.append(f"negative outcome: {human_phrase}")
    
    # Check for threshold absolutism
    for human_phrase, regex_pattern in THRESHOLD_ABSOLUTISM_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            has_threshold_absolutism = True
            matches.append(f"threshold absolutism: {human_phrase}")
    
    # Flag if policy + negative outcome + no substantive analysis
    flagged = False
    if (has_policy_citation or has_threshold_absolutism) and has_negative_outcome:
        if not has_substantive_analysis(rationale):
            flagged = True
    
    return {
        'flagged': flagged,
        'matches': list(set(matches)) if flagged else [],
        'match_count': len(matches) if flagged else 0,
        'match_locations': match_locations,
        'detection_type': 'POLICY_INVERSION'
    }

def detect_distributive_warrant(rationale: str) -> Dict:
    """
    Detects distributive warrant fallacy (Module 3).
    
    Catches "each part is safe, therefore whole is safe" reasoning.
    """
    rationale_lower = rationale.lower()
    rationale_lower = ' '.join(rationale_lower.split())
    
    matches = []
    match_locations = []
    
    has_distributive_language = False
    has_negative_outcome = False
    has_aggregate_analysis = False
    
    # Check for distributive language
    for human_phrase, regex_pattern in DISTRIBUTIVE_LEXICON.items():
        if re.search(regex_pattern, rationale_lower):
            has_distributive_language = True
            matches.append(f"distributive language: {human_phrase}")
            for match in re.finditer(regex_pattern, rationale_lower):
                match_locations.append({
                    'phrase': human_phrase,
                    'position': match.start(),
                    'context': rationale[max(0, match.start()-30):match.end()+30].strip()
                })
    
    # Check for negative outcomes
    for human_phrase, regex_pattern in NEGATIVE_OUTCOME_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            has_negative_outcome = True
    
    # Check for aggregate analysis
    for marker in AGGREGATE_MARKERS:
        if marker in rationale_lower:
            has_aggregate_analysis = True
            break
    
    # Flag if distributive language + negative outcome + no aggregate analysis
    flagged = has_distributive_language and has_negative_outcome and not has_aggregate_analysis
    
    return {
        'flagged': flagged,
        'matches': list(set(matches)) if flagged else [],
        'match_count': len(matches) if flagged else 0,
        'match_locations': match_locations,
        'detection_type': 'DISTRIBUTIVE_WARRANT'
    }

def parse_money_amount(amount_str: str) -> float:
    """
    Converts money string to float value.
    
    Examples:
        "10,000" -> 10000.0
        "10k" -> 10000.0
        "2.5M" -> 2500000.0
    """
    amount_str = amount_str.replace(',', '').strip()
    
    if amount_str.endswith('k') or amount_str.endswith('K'):
        return float(amount_str[:-1]) * 1000
    elif amount_str.endswith('M') or amount_str.endswith('m'):
        return float(amount_str[:-1]) * 1000000
    elif 'thousand' in amount_str.lower():
        return float(amount_str.split()[0]) * 1000
    elif 'million' in amount_str.lower():
        return float(amount_str.split()[0]) * 1000000
    else:
        return float(amount_str)

def detect_aggregate_blindness(rationale: str, policy_threshold: float = 10000.0) -> Dict:
    """
    Detects aggregate blindness through quantity parsing (Module 4).
    
    Catches when individual amounts < threshold but aggregate > threshold
    and analyst only mentions individual amounts.
    
    Args:
        rationale: Analyst rationale text
        policy_threshold: Policy threshold (default £10,000)
    """
    rationale_lower = rationale.lower()
    rationale_lower = ' '.join(rationale_lower.split())
    
    matches = []
    match_locations = []
    
    # Extract monetary amounts
    amounts = []
    for match in re.finditer(MONEY_PATTERN, rationale_lower):
        try:
            amount = parse_money_amount(match.group(1))
            amounts.append(amount)
        except:
            continue
    
    # Extract ranges
    ranges = []
    for match in re.finditer(RANGE_PATTERN, rationale_lower):
        try:
            lower = parse_money_amount(match.group(1))
            upper = parse_money_amount(match.group(2))
            ranges.append((lower, upper))
        except:
            continue
    
    # Extract transaction counts
    transaction_count = None
    for match in re.finditer(COUNT_PATTERN, rationale_lower):
        try:
            transaction_count = int(match.group(1))
            break
        except:
            continue
    
    # Check for distributive language
    has_distributive = any(re.search(pattern, rationale_lower) 
                          for pattern in DISTRIBUTIVE_LEXICON.values())
    
    # Check for aggregate mentions
    has_aggregate_mention = any(marker in rationale_lower for marker in AGGREGATE_MARKERS)
    
    flagged = False

    # NEW: Check for aggregate ANALYSIS (not just mention)
    # Look for phrases that indicate the analyst is actually analyzing the aggregate
    aggregate_analysis_indicators = [
        r"aggregate (?:of|is|represents|suggests|indicates)",
        r"total (?:of|is|represents|suggests|indicates|value)",
        r"combined (?:total|value|amount)",
        r"sum (?:of|is|represents|totaling)",
        r"(?:totaling|totalling) £?\d",
        r"material change",
        r"transaction velocity",
        r"pattern as a whole",
        r"totality of",
    ]
    
    has_aggregate_analysis = any(re.search(pattern, rationale_lower) 
                                 for pattern in aggregate_analysis_indicators)
    
    # LOGIC 1: Range + count implies large aggregate
    if ranges and transaction_count and not has_aggregate_analysis:
        for lower, upper in ranges:
            estimated_total = upper * transaction_count
            if upper < policy_threshold and estimated_total > (policy_threshold * 5):
                flagged = True
                matches.append(f"range £{int(lower):,}-£{int(upper):,} × {transaction_count} transactions = ~£{int(estimated_total):,}")
                matches.append(f"individual < £{int(policy_threshold):,} threshold, but aggregate > £{int(policy_threshold * 5):,}")
    
    # LOGIC 2: Multiple amounts below threshold, sum exceeds threshold significantly
    if len(amounts) > 3 and not has_aggregate_mention and not has_aggregate_analysis:
        total = sum(amounts)
        max_single = max(amounts)
        if max_single < policy_threshold and total > (policy_threshold * 5):
            flagged = True
            matches.append(f"{len(amounts)} amounts totaling ~£{int(total):,}")
            matches.append(f"max single £{int(max_single):,} < threshold, but total > £{int(policy_threshold * 5):,}")
    
    # LOGIC 3: Distributive language + amounts below threshold
    if has_distributive and amounts and not has_aggregate_analysis:
        max_single = max(amounts)
        if max_single < policy_threshold and not has_aggregate_mention:
            matches.append("distributive language used with sub-threshold amounts")
            matches.append("no aggregate analysis despite multiple transactions")
            flagged = True
    
    return {
        'flagged': flagged,
        'matches': list(set(matches)),
        'match_count': len(matches),
        'match_locations': match_locations,
        'detection_type': 'AGGREGATE_BLINDNESS',
        'metadata': {
            'amounts': amounts,
            'ranges': ranges,
            'transaction_count': transaction_count,
            'estimated_total': sum(amounts) if amounts else None,
            'has_aggregate_analysis': has_aggregate_analysis  # ADD THIS LINE
        }
    }

# ═══════════════════════════════════════════════════════════════════
# UPDATED MAIN DETECTION FUNCTION
# ═══════════════════════════════════════════════════════════════════

def detect_filter_deference(rationale: str, policy_threshold: float = 10000.0) -> Dict:
    """
    ENHANCED: Detects all FP-01 patterns including Phase 1.5 modules.
    
    Runs all detection modules:
    - Phase 1: Explicit filter-deference
    - Module 1: Euphemized automation
    - Module 2: Policy inversion
    - Module 3: Distributive warrant
    - Module 4: Aggregate blindness
    
    Args:
        rationale: The analyst's written justification
        policy_threshold: Policy threshold for aggregate detection (default £10,000)
        
    Returns:
        Dictionary containing:
        - flagged: Boolean (True if any FP-01 pattern detected)
        - matches: List of all detected patterns
        - match_count: Total number of patterns detected
        - match_locations: Context snippets for matches
        - detection_breakdown: Results from each module
    """
    
    rationale_lower = rationale.lower()
    rationale_lower = ' '.join(rationale_lower.split())
    
    # Phase 1: Original filter-deference detection
    phase1_matches = []
    phase1_locations = []
    
    for human_phrase, regex_pattern in FILTER_DEFERENCE_PATTERNS.items():
        if re.search(regex_pattern, rationale_lower):
            phase1_matches.append(human_phrase)
            for match in re.finditer(regex_pattern, rationale_lower):
                phase1_locations.append({
                    'phrase': human_phrase,
                    'position': match.start(),
                    'context': rationale[max(0, match.start()-30):match.end()+30].strip()
                })
    
    phase1_result = {
        'flagged': len(phase1_matches) >= FLAGGING_THRESHOLD,
        'matches': list(set(phase1_matches)),
        'match_count': len(phase1_matches),
        'match_locations': phase1_locations,
        'detection_type': 'EXPLICIT_FILTER_DEFERENCE'
    }
    
    # Phase 1.5: Run all new modules
    euphemism_result = detect_euphemized_automation(rationale)
    policy_result = detect_policy_inversion(rationale)
    distributive_result = detect_distributive_warrant(rationale)
    aggregate_result = detect_aggregate_blindness(rationale, policy_threshold)
    
    # Combine all results
    all_modules = [phase1_result, euphemism_result, policy_result, distributive_result, aggregate_result]
    
    all_matches = []
    all_locations = []
    flagged_modules = []
    
    for module_result in all_modules:
        if module_result['flagged']:
            flagged_modules.append(module_result['detection_type'])
            all_matches.extend(module_result['matches'])
            all_locations.extend(module_result['match_locations'])
    
    overall_flagged = len(flagged_modules) > 0
    
    return {
        'flagged': overall_flagged,
        'matches': list(set(all_matches)),
        'match_count': len(all_matches),
        'match_locations': all_locations,
        'flagged_modules': flagged_modules,
        'detection_breakdown': {
            'explicit_filter_deference': phase1_result,
            'euphemized_automation': euphemism_result,
            'policy_inversion': policy_result,
            'distributive_warrant': distributive_result,
            'aggregate_blindness': aggregate_result
        }
    }

# ═══════════════════════════════════════════════════════════════════
# UPDATED EXPLANATION GENERATOR
# ═══════════════════════════════════════════════════════════════════

def generate_flag_explanation(detection_result: Dict, scenario_institution: str = "Multiple institutions") -> str:
    """
    ENHANCED: Generates human-readable explanation including all detection modules.
    
    Args:
        detection_result: Output from detect_filter_deference()
        scenario_institution: Name of institution for context
        
    Returns:
        String explanation for display to analyst
    """
    
    if not detection_result['flagged']:
        return "✅ No filter-deference detected. Rationale shows independent judgment."
    
    flagged_modules = detection_result.get('flagged_modules', [])
    matches = detection_result['matches']
    count = detection_result['match_count']
    
    explanation = f"🚩 FP-01 DETECTED: Filter Replaces Judgment\n\n"
    explanation += f"Your rationale triggered {len(flagged_modules)} detection module(s):\n\n"
    
    # Show which modules flagged
    module_names = {
        'EXPLICIT_FILTER_DEFERENCE': 'Explicit Filter-Deference',
        'EUPHEMIZED_AUTOMATION': 'Euphemized Automation',
        'POLICY_INVERSION': 'Policy-as-Warrant Inversion',
        'DISTRIBUTIVE_WARRANT': 'Distributive Warrant Fallacy',
        'AGGREGATE_BLINDNESS': 'Aggregate Blindness'
    }
    
    for module in flagged_modules:
        explanation += f"• {module_names.get(module, module)}\n"
    
    explanation += f"\n📋 DETECTED PATTERNS ({count} total):\n"
    for i, match in enumerate(matches[:10], 1):  # Show max 10
        explanation += f"{i}. {match}\n"
    
    # Show context snippets
    if detection_result['match_locations']:
        explanation += "\n📍 CONTEXT EXAMPLES:\n"
        for loc in detection_result['match_locations'][:3]:
            explanation += f"• ...{loc['context']}...\n"
    
    explanation += "\n⚠️ REGULATORY RISK:\n"
    explanation += "This reasoning structure appears in FCA enforcement findings where:\n"
    explanation += "• Reliance on filters/thresholds replaced independent judgment\n"
    explanation += "• Policy compliance was used to justify inaction\n"
    explanation += "• Aggregate risk was ignored through threshold atomization\n\n"
    explanation += f"Relevant cases: Nationwide (£264.8M), Barclays (£72M), Mako/Coinbase (£3.5M+)\n\n"
    explanation += "💡 REQUIRED: Substantive risk analysis demonstrating independent professional judgment."
    
    return explanation