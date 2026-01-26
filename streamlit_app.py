import streamlit as st
import json
from pathlib import Path
from detection_engine import detect_filter_deference, generate_flag_explanation
from audit_log import log_analysis, export_to_csv, log_validation_session

# ═══════════════════════════════════════════
# Page Configuration
# ═══════════════════════════════════════════

st.set_page_config(
    page_title="Crucible - FP-01 Detection Engine",
    page_icon=" ",
    layout="wide"
)

# Minimal CSS - only background color
st.markdown("""
<style>
    .main {
        background-color: #0f1419;
        color: #e8eaed;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════
# Control Placement Header
# ═══════════════════════════════════════════

st.title(" Crucible: FP-01 Detection Engine")
st.markdown("**Pre-clearance decision gate**")
st.markdown("*Intercepts analyst rationale before final approval*")
st.markdown("---")

# ═══════════════════════════════════════════
# Session State
# ═══════════════════════════════════════════

if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'detection_result' not in st.session_state:
    st.session_state.detection_result = None
if 'current_scenario' not in st.session_state:
    st.session_state.current_scenario = None

# ═══════════════════════════════════════════
# Load Scenarios
# ═══════════════════════════════════════════

@st.cache_data
def load_all_scenarios():
    """Load all available scenarios"""
    scenarios = {}
    scenario_dir = Path("scenarios")
    
    if scenario_dir.exists():
        for scenario_file in scenario_dir.glob("corpse_*.json"):
            with open(scenario_file, 'r') as f:
                data = json.load(f)
                scenarios[data['id']] = data
    
    return scenarios

scenarios = load_all_scenarios()

if not scenarios:
    st.error("⚠️ No scenarios found. Please ensure scenarios/ folder contains corpse_*.json files.")
    st.stop()

# ═══════════════════════════════════════════
# Scenario Selection
# ═══════════════════════════════════════════

st.markdown("### 📋 Select Scenario")

scenario_options = {
    f"{data['institution']} (£{data['fine_amount']})": scenario_id 
    for scenario_id, data in scenarios.items()
}

selected_display = st.selectbox(
    "Choose a case to analyze:",
    options=list(scenario_options.keys())
)

selected_id = scenario_options[selected_display]
scenario = scenarios[selected_id]
st.session_state.current_scenario = scenario

# ═══════════════════════════════════════════
# Display Scenario
# ═══════════════════════════════════════════

st.markdown(f"### {scenario['title']}")

# Use plain Streamlit info box - no unsafe HTML
st.info(scenario['scenario'])

# ═══════════════════════════════════════════
# Rationale Input
# ═══════════════════════════════════════════

st.markdown("###  Your Rationale")
st.markdown("**Explain your decision and reasoning:**")

rationale = st.text_area(
    "Rationale",
    height=200,
    placeholder="Write your analysis here... Explain why you would escalate or clear this case, and what specific factors informed your decision.",
    label_visibility="collapsed"
)

# Analysis button
if st.button("🔍 Analyze Rationale", use_container_width=False):
    if rationale.strip():
        with st.spinner("Analyzing rationale for filter-deference patterns..."):
            # Run detection
            result = detect_filter_deference(rationale)
            st.session_state.detection_result = result
            st.session_state.analysis_complete = True
            
            # Log to audit trail
            log_analysis(
                scenario_id=scenario['id'],
                rationale=rationale,
                detection_result=result
            )
    else:
        st.warning("⚠️ Please enter your rationale before analyzing.")

# ═══════════════════════════════════════════
# Display Results
# ═══════════════════════════════════════════

if st.session_state.analysis_complete and st.session_state.detection_result:
    st.markdown("---")
    st.markdown("### Analysis Results")
    
    result = st.session_state.detection_result
    
    if result['flagged']:
        # Flag detected - use Streamlit error box
        explanation = generate_flag_explanation(result, scenario['institution'])
        st.error(explanation)
        
        # Show FCA comparison
        st.markdown("### ⚖️ Regulatory Comparison")
        st.markdown("**FCA enforcement finding in this case:**")
        st.warning(scenario['fca_criticism'])
        
    else:
        # No flag - use Streamlit success box
        st.success(f"✅ No filter-deference detected.\n\nYour rationale demonstrates independent judgment and does not rely on system filters or policy proxies.")
    
    # Show correct approach for reference only
    st.markdown("### 📖 Post-Incident FCA Interpretation (For Comparison)")
    st.info(f"**FCA's position:** {scenario['correct_approach']}")
    
    # Reset button
    if st.button("🔄 Analyze Another Scenario"):
        st.session_state.analysis_complete = False
        st.session_state.detection_result = None
        st.rerun()

# ═══════════════════════════════════════════
# Audit Export
# ═══════════════════════════════════════════

st.markdown("---")
st.markdown("### 📥 Audit Trail Export")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Export Audit Trail (CSV)"):
        csv_data = export_to_csv()
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name="crucible_audit_log.csv",
            mime="text/csv"
        )

# ═══════════════════════════════════════════
# Validation Session Form
# ═══════════════════════════════════════════

st.markdown("---")
st.markdown("## 🎯 QA Validation Session")
st.markdown("*Complete this after reviewing all scenarios with QA head*")

with st.expander("Validation Sign-Off Form"):
    qa_head_name = st.text_input(
        "QA Head Name/ID",
        placeholder="e.g., John Smith - Senior AML Analyst"
    )
    
    st.markdown("**Validation Questions:**")
    
    q1 = st.radio(
        "Does FP-01 detection flag the failure mode across all reviewed scenarios?",
        ["Yes", "No"],
        key="q1"
    )
    
    q2 = st.radio(
        "Did the engine avoid false positives on clean rationales?",
        ["Yes", "No"],
        key="q2"
    )
    
    q3 = st.radio(
        "Would you recommend this mechanism for pilot testing in a production environment?",
        ["Yes", "No"],
        key="q3"
    )
    
    additional_notes = st.text_area(
        "Additional Notes (optional)",
        placeholder="Any observations, concerns, or recommendations...",
        height=100
    )
    
    if st.button("✅ Submit Validation"):
        if qa_head_name.strip():
            # Log validation session
            log_validation_session(
                qa_head_id=qa_head_name,
                scenarios_reviewed=list(scenarios.keys()),
                validation_responses={
                    "flags_failure_mode": q1 == "Yes",
                    "avoids_false_positives": q2 == "Yes",
                    "recommend_pilot": q3 == "Yes"
                },
                additional_notes=additional_notes,
                positive_cases=len(scenarios),
                negative_cases=2  # Based on clean_rationales.json
            )
            st.success("✅ Validation session logged successfully. Thank you for your feedback!")
            st.balloons()
        else:
            st.warning("⚠️ Please enter QA Head name/ID before submitting.")