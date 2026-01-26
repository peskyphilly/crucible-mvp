"""
Unit tests for Crucible FP-01 Detection Engine

Tests verify:
1. Positive cases: Filter-deference rationales ARE flagged (6 tests)
2. Negative cases: Clean rationales are NOT flagged (2 tests)

Run with: python -m pytest test_detection_engine.py -v
Or simply: python test_detection_engine.py
"""

import sys
from detection_engine import detect_filter_deference

# ═══════════════════════════════════════════
# POSITIVE TEST CASES (Should Flag)
# ═══════════════════════════════════════════

def test_nationwide_filter_deference():
    """Test detection of Nationwide-style filter-deference"""
    rationale = """
    The account has been open for 14 months. Per policy, EDD refresh is required 
    at 12 months for PEP accounts. However, the system recommendation indicates 
    no immediate action required, as the account activity is consistent with the 
    customer profile established at onboarding. Therefore, I am clearing this case.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag 'per policy' and 'system recommendation'"
    assert 'per policy' in result['matches'], "Should detect 'per policy'"
    assert len(result['matches']) >= 1, "Should detect at least one filter-deference phrase"
    print("✓ PASSED: Nationwide filter-deference detection")

def test_barclays_threshold_deference():
    """Test detection of Barclays-style threshold deference"""
    rationale = """
    The client has generated 12 alerts in the last 90 days. However, these alerts 
    are below threshold for immediate escalation and are in line with standard 
    practice for this client risk profile. The automated review indicates the 
    transactions fall within normal parameters. I recommend no further action.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag threshold and standard practice language"
    assert 'below threshold' in result['matches'], "Should detect 'below threshold'"
    assert 'in line with standard practice' in result['matches'] or 'standard practice' in result['matches'], "Should detect standard practice"
    print("✓ PASSED: Barclays threshold-deference detection")

def test_mako_checklist_completion():
    """Test detection of Mako-style checklist completion language"""
    rationale = """
    Enhanced Due Diligence requirements have been met for this client. The EDD 
    package has been completed as per guidelines, and no sanctions matches were 
    identified during screening. Per our policy, we can proceed with onboarding 
    since all procedural requirements are satisfied.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag policy and guideline deference"
    assert 'as per guidelines' in result['matches'], "Should detect 'as per guidelines'"
    assert 'per policy' in result['matches'] or 'per our policy' in result['matches'], "Should detect policy reference"
    print("✓ PASSED: Mako checklist-completion detection")

def test_coinbase_threshold_atomization():
    """Test detection of Coinbase-style transaction atomization"""
    rationale = """
    The customer's individual transactions are below reporting threshold. Each 
    deposit is within the standard retail risk profile parameters. Per our policy, 
    transactions under £10,000 do not require enhanced review. The system 
    recommendation is to continue monitoring under standard procedures.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag threshold and policy language"
    assert 'below threshold' in result['matches'] or 'threshold not met' in result['matches'], "Should detect threshold language"
    assert 'per policy' in result['matches'] or 'per our policy' in result['matches'], "Should detect policy deference"
    print("✓ PASSED: Coinbase threshold-atomization detection")

def test_multiple_filter_phrases():
    """Test detection when multiple filter-deference phrases are present"""
    rationale = """
    Per policy, this case does not meet the threshold for escalation. The system 
    recommendation indicates no further action required. This is consistent with 
    our approach for similar cases.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag multiple filter-deference phrases"
    assert result['match_count'] >= 3, "Should detect at least 3 distinct phrases"
    print("✓ PASSED: Multiple filter-deference phrases detection")

def test_no_requirement_language():
    """Test detection of 'no requirement' language"""
    rationale = """
    After reviewing the case, I note that there is no requirement to escalate 
    based on current policy guidelines. The customer's activity falls within 
    acceptable parameters, and per our procedures, no further action is required.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == True, "Should flag 'no requirement' language"
    assert 'no requirement to' in result['matches'] or 'no further action required' in result['matches'], "Should detect requirement language"
    print("✓ PASSED: 'No requirement' language detection")

# ═══════════════════════════════════════════
# NEGATIVE TEST CASES (Should NOT Flag)
# ═══════════════════════════════════════════

def test_clean_rationale_with_judgment():
    """Test that independent judgment rationales are NOT flagged"""
    rationale = """
    The customer's account shows concerning patterns that require immediate attention:
    
    1. The EDD is 14 months overdue, exceeding both the 12-month PEP requirement 
       and the 6-month high-risk jurisdiction requirement. This is a clear breach.
    
    2. The customer has been unresponsive to two outreach attempts, which is itself 
       a red flag for potential account takeover or money laundering.
    
    3. The transaction pattern (rapid in-and-out movements to third parties) does 
       not align with the stated legitimate business purpose.
    
    Despite the system indicating no immediate action is needed, I am escalating 
    this case because the cumulative risk factors - outdated due diligence, 
    unresponsive customer, and suspicious transaction patterns - present material 
    money laundering risk that cannot be ignored regardless of system thresholds.
    
    The policy framework provides minimum standards, but professional judgment 
    requires escalation when multiple risk indicators converge, even if individual 
    elements appear within technical compliance.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == False, "Should NOT flag rationale demonstrating independent judgment"
    assert result['match_count'] == 0, "Should detect zero filter-deference phrases"
    print("✓ PASSED: Clean rationale with independent judgment NOT flagged")

def test_clean_rationale_with_risk_analysis():
    """Test that risk-based analysis is NOT flagged"""
    rationale = """
    I have reviewed this high-value transaction monitoring alert and identified 
    several concerning factors:
    
    First, the beneficial ownership structure remains unclear after 18 months, 
    which is unacceptable for a corporate relationship of this size and risk profile.
    
    Second, the frequency of alerts (12 in 90 days) suggests either a failure 
    in our initial risk assessment or a material change in the customer's behavior 
    that we have not adequately understood.
    
    Third, the movement of £4.2M through rapid in-out transactions to high-risk 
    jurisdictions is inconsistent with the stated 'international consulting' 
    business model, which should show more stable, predictable payment patterns.
    
    While our automated systems have not triggered an immediate escalation flag, 
    my assessment is that we are missing critical information about this 
    relationship. The combination of unclear ownership, alert frequency, 
    transaction velocity, and high-risk jurisdictions creates an unacceptable 
    risk exposure.
    
    I am escalating for immediate investigation and proposing we suspend further 
    activity until we can verify the source of funds and clarify the beneficial 
    ownership structure. This is a judgment call based on the totality of 
    circumstances, not a mechanical application of alert thresholds.
    """
    
    result = detect_filter_deference(rationale)
    assert result['flagged'] == False, "Should NOT flag comprehensive risk analysis"
    assert result['match_count'] == 0, "Should detect zero filter-deference phrases"
    print("✓ PASSED: Clean rationale with risk analysis NOT flagged")

# ═══════════════════════════════════════════
# Test Runner
# ═══════════════════════════════════════════

def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("CRUCIBLE FP-01 DETECTION ENGINE - UNIT TESTS")
    print("="*60 + "\n")
    
    print("POSITIVE TEST CASES (Should Flag Filter-Deference):")
    print("-" * 60)
    
    tests_positive = [
        test_nationwide_filter_deference,
        test_barclays_threshold_deference,
        test_mako_checklist_completion,
        test_coinbase_threshold_atomization,
        test_multiple_filter_phrases,
        test_no_requirement_language
    ]
    
    passed_positive = 0
    for test in tests_positive:
        try:
            test()
            passed_positive += 1
        except AssertionError as e:
            print(f"✗ FAILED: {test.__name__}")
            print(f"  Error: {e}\n")
    
    print(f"\nPositive Tests: {passed_positive}/{len(tests_positive)} passed\n")
    
    print("\nNEGATIVE TEST CASES (Should NOT Flag Clean Rationales):")
    print("-" * 60)
    
    tests_negative = [
        test_clean_rationale_with_judgment,
        test_clean_rationale_with_risk_analysis
    ]
    
    passed_negative = 0
    for test in tests_negative:
        try:
            test()
            passed_negative += 1
        except AssertionError as e:
            print(f"✗ FAILED: {test.__name__}")
            print(f"  Error: {e}\n")
    
    print(f"\nNegative Tests: {passed_negative}/{len(tests_negative)} passed\n")
    
    print("="*60)
    total_passed = passed_positive + passed_negative
    total_tests = len(tests_positive) + len(tests_negative)
    print(f"TOTAL: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("✅ ALL TESTS PASSED - Detection engine is working correctly")
    else:
        print("❌ SOME TESTS FAILED - Review detection logic")
    
    print("="*60 + "\n")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)