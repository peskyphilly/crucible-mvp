Crucible FP-01 Detection Engine - Validation Protocol
Purpose
This protocol provides a structured framework for QA heads and financial crime experts to validate the Crucible FP-01 detection mechanism. The goal is to confirm that filter-deference failures can be reliably detected pre-incident using deterministic pattern matching.

Validation Methodology
1. Scope
What we are validating:

The existence and detectability of FP-01 (Filter Replaces Judgment) as a structural failure pattern
The reliability of deterministic detection using language pattern matching
The placement of this control in the pre-clearance decision workflow
What we are NOT validating:

Production-ready enterprise infrastructure
Bank procurement requirements
GDPR/compliance architecture
Multi-tenant deployment capabilities
2. Test Scenarios
The validation session includes:

Positive Cases (Should Flag):

CORPSE_01_NATIONWIDE - PEP monitoring failure (£264.8M fine)
CORPSE_02_BARCLAYS - Transaction monitoring failure (£72M fine)
CORPSE_03_MAKO - Onboarding failure (£1.89M fine)
CORPSE_04_COINBASE - High-risk jurisdiction monitoring (£3.5M fine)
Negative Cases (Should NOT Flag):

Clean rationale with independent judgment (see clean_rationales.json)
Clean rationale with comprehensive risk analysis (see clean_rationales.json)
3. Validation Session Procedure
Step 1: Review Detection Logic (10 minutes)
Examiner reviews:

The filter-deference patterns extracted from FCA notices
The deterministic detection mechanism (regex-based)
The control placement (pre-clearance decision gate)
Key Question: "Does this pattern appear in your own QA experience?"

Step 2: Test Positive Cases (15 minutes)
For each of the 4 FCA corpses:

Read the scenario
Write a rationale that includes filter-deference language (e.g., "per policy," "threshold not met," "system recommendation")
Submit for analysis
Verify: Does the engine flag this rationale?
Verify: Does the flagged language match actual FCA criticism?
Expected Result: All 4 positive cases should be flagged with specific pattern matches shown.

Step 3: Test Negative Cases (10 minutes)
For the 2 clean rationales:

Read the scenario
Review the provided clean rationale (shows independent judgment)
Submit for analysis
Verify: Does the engine correctly NOT flag this rationale?
Expected Result: Both clean rationales should pass through without flags.

Step 4: Audit Trail Review (5 minutes)
Export audit trail (CSV)
Verify: Are all test cases logged with timestamps?
Verify: Can you distinguish flagged vs. clean entries?
Verify: Is the log exportable and human-readable?
Step 5: Complete Validation Questions (5 minutes)
Answer the following validation questions:

Validation Questions
Question 1: Failure Pattern Recognition
"Does FP-01 (Filter Replaces Judgment) represent a real failure mode that you observe in financial crime quality assurance?"

☐ Yes - This pattern appears frequently in our QA reviews
☐ Partially - This pattern appears occasionally
☐ No - This pattern does not appear in our experience

Notes:

_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
Question 2: Detection Accuracy (Positive Cases)
"Did the detection engine correctly flag filter-deference language across all 4 FCA scenarios?"

☐ Yes - All 4 scenarios were flagged correctly
☐ Partially - Some scenarios were flagged correctly
☐ No - Detection failed on multiple scenarios

If Partially or No, specify which scenarios failed:

_________________________________________________________________
_________________________________________________________________
Question 3: False Positive Avoidance (Negative Cases)
"Did the detection engine correctly avoid flagging the clean rationales that demonstrated independent judgment?"

☐ Yes - Both clean rationales passed without flags
☐ No - One or both clean rationales were incorrectly flagged

If No, specify the issue:

_________________________________________________________________
_________________________________________________________________
Question 4: Control Placement
"Does pre-clearance detection (intercepting analyst rationale before final approval) make sense as a control placement for this failure mode?"

☐ Yes - This is the correct point of intervention
☐ No - This control should be placed elsewhere

If No, where should this control be placed?

_________________________________________________________________
_________________________________________________________________
Question 5: Practical Utility
"Would you recommend pilot testing this detection mechanism in a live QA workflow?"

☐ Yes - Recommend pilot
☐ Maybe - Needs modifications first (specify below)
☐ No - Not suitable for production use

If Maybe or No, what modifications are needed?

_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
Question 6: Additional Observations
"Any other observations, concerns, or recommendations?"

_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
Validation Sign-Off
Validator Information
Name: _______________________________________________________

Title/Role: _______________________________________________________

Institution: _______________________________________________________

Date: _______________________________________________________

Signature: _______________________________________________________

Logged Evidence
Note: Each validation session is logged as an append-only event in the system audit trail for evidentiary purposes. This creates a structured record that:

Documents which scenarios were reviewed
Records validation responses
Timestamps the expert review
Provides exportable proof of validation
Human signature above = Attestation of validation
Logged validation event = System evidence of review

Post-Validation
After completing this protocol:

Export the audit trail (CSV) - This contains all test results + validation session
Provide this signed protocol - Human attestation
Optional: Provide written testimonial - Expanded feedback on mechanism utility
These three artifacts (audit trail + signed protocol + testimonial) constitute the validation evidence package.

Contact
For questions about this validation protocol or the detection mechanism:

Crucible FP-01 Detection Engine
Technical validation framework for financial crime judgment controls

Appendix: Success Criteria
For this validation to pass, the following must be true:

✅ All 4 positive cases (FCA corpses) are flagged
✅ Both negative cases (clean rationales) are NOT flagged
✅ False positive rate < 10% (based on negative case testing)
✅ Audit trail is exportable and contains all test records
✅ Validator confirms FP-01 is a real failure pattern in their experience
✅ Validator recommends pilot testing (or specifies feasible modifications)

Outcome classification:

PASS: All criteria met, recommend pilot
PARTIAL PASS: Most criteria met, modifications specified, pilot feasible with changes
FAIL: Detection unreliable or failure pattern not recognized
End of Validation Protocol

