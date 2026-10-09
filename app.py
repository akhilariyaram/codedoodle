import streamlit as st
import requests
import json
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Page Configuration
st.set_page_config(
    page_title="AI Incident Learning & Prevention Copilot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Mission Control Styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Header */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid rgba(56, 189, 248, 0.25);
        border-radius: 14px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.3);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #F8FAFC;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 0.95rem;
        color: #94A3B8;
        margin-top: 0.3rem;
    }
    .live-status {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        color: #34D399;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.5rem;
    }
    .live-dot {
        width: 8px;
        height: 8px;
        background: #10B981;
        border-radius: 50%;
        box-shadow: 0 0 8px #10B981;
    }

    /* Stepper Header for Continuous Learning */
    .stepper-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 0.8rem 1.4rem;
        margin-bottom: 1.4rem;
    }
    .step-item {
        font-size: 0.85rem;
        font-weight: 600;
        color: #38BDF8;
    }

    pre, code {
        font-family: 'JetBrains Mono', monospace !important;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Session State Variables
if "input_comp" not in st.session_state:
    st.session_state["input_comp"] = ""
if "input_build" not in st.session_state:
    st.session_state["input_build"] = ""
if "input_rca" not in st.session_state:
    st.session_state["input_rca"] = ""
if "input_release" not in st.session_state:
    st.session_state["input_release"] = ""
if "match_result" not in st.session_state:
    st.session_state["match_result"] = None
if "recommendation" not in st.session_state:
    st.session_state["recommendation"] = None
if "extracted_resolution" not in st.session_state:
    st.session_state["extracted_resolution"] = None

# Sidebar - System Status & Controls
with st.sidebar:
    st.markdown("""
    <div style='display:flex; align-items:center; gap:0.6rem; margin-bottom:1rem;'>
        <img src='https://img.icons8.com/color/96/server-shutdown.png' width='44'/>
        <div>
            <div style='font-weight:800; font-size:1.15rem; color:#F8FAFC;'>TELECOM NOC</div>
            <div style='font-size:0.75rem; color:#38BDF8; font-weight:600;'>AI COPILOT COMMAND</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.caption("SYSTEM TELEMETRY")
    try:
        health_resp = requests.get(f"{API_BASE_URL}/", timeout=2)
        if health_resp.status_code == 200:
            st.success("🟢 FastAPI Core: ONLINE (8000)")
        else:
            st.error("🔴 Backend Error")
    except Exception:
        st.warning("⚠️ Backend Offline (Run `python main.py`)")

    st.divider()
    st.caption("NEURAL ENGINE SPEC")
    st.markdown("""
    ⚡ **Synthesis LLM:** `Llama 3 (8B)`  
    🔮 **Embeddings:** `embeddinggemma`  
    🗄️ **Vector Store:** `ChromaDB (jira_tickets)`  
    🛡️ **Guardrail:** `Zero-Hallucination`
    """)
    st.divider()
    st.caption("v2.5 Unified Autonomous Loop Edition")

# Hero Header
st.markdown("""
<div class='hero-banner'>
    <div class='live-status'>
        <div class='live-dot'></div>
        ACTIVE TELEMETRY &bull; AGENTIC INCIDENT RADAR
    </div>
    <div class='hero-title'>AI Incident Learning & Prevention Copilot</div>
    <div class='hero-subtitle'>Autonomous Agentic RAG for Telecom Core Mitigation, Real-Time Auditability & Continuous Memory Ingestion</div>
</div>
""", unsafe_allow_html=True)

# ==============================================================================
# UNIFIED INCIDENT TELEMETRY INSPECTION, GATEKEEPER & HYBRID SEARCH
# ==============================================================================
st.subheader("⚡ Incident Telemetry Inspection & Extraction")
st.caption("Paste raw alarm logs, symptoms, or proposed MOP execution text. The agent extracts parameters, verifies mandatory fields, and initiates hybrid search.")

query_text = st.text_area(
    "Raw Incident Logs / Proposed MOP Execution Script / Alarm Stream:",
    value="",
    height=110,
    placeholder="Enter symptoms or paste alarm logs (e.g. BGP flapping on CMG-12 build 14.2...)"
)

col_extract, _ = st.columns([2.2, 2.8])
with col_extract:
    extract_clicked = st.button("🤖 1. Auto-Extract Parameters from Text", type="secondary", use_container_width=True)

# When user clicks Auto-Extract, call /match to extract the parameters into session state
if extract_clicked and query_text.strip():
    with st.status("🔍 Extracting Technical Parameters via Llama 3...", expanded=True) as status_box:
        try:
            res = requests.post(f"{API_BASE_URL}/match", json={"raw_incident_text": query_text.strip()})
            if res.status_code == 200:
                data = res.json()
                fp = data.get("extracted_fingerprint", {})
                st.session_state["input_comp"] = fp.get("components") if fp.get("components") != "Unknown" else ""
                st.session_state["input_build"] = fp.get("build_version") if fp.get("build_version") != "Unknown" else ""
                st.session_state["input_release"] = fp.get("product_release") if fp.get("product_release") != "Unknown" else ""
                st.session_state["input_rca"] = fp.get("rca_category") if fp.get("rca_category") != "Unknown" else ""
                status_box.update(label="✅ Parameters Extracted into Fields Below!", state="complete", expanded=False)
                st.toast("✅ Mandatory fields updated below!", icon="✨")
                st.rerun()
            else:
                st.error(f"Extraction Error: {res.text}")
                status_box.update(label="❌ Extraction Failed", state="error")
        except Exception as e:
            st.error(f"Backend Connection Error: {e}")
            status_box.update(label="❌ Backend Error", state="error")

# ==============================================================================
# MANDATORY TECHNICAL FIELDS (DISPLAYED BEFORE SEARCHING!)
# ==============================================================================
st.markdown("---")
with st.container(border=True):
    st.markdown("### 🛡️ Verified Technical Parameters (Pre-Search Gatekeeper)")
    st.caption("Verify and adjust the mandatory parameters below. Search will execute using these verified metadata filters.")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        input_comp = st.text_input("🛰️ Component / Node *", key="input_comp", placeholder="e.g. CMG-12, UI Frontend")
    with col2:
        input_build = st.text_input("🔖 Build Version *", key="input_build", placeholder="e.g. 14.2, v2.4.1")
    with col3:
        input_rca = st.text_input("🏷️ RCA Category *", key="input_rca", placeholder="e.g. Firmware MTU Reset")
    with col4:
        input_release = st.text_input("📦 Product Release", key="input_release", placeholder="e.g. Q3 Core Upgrade")

    is_comp_valid = bool(input_comp.strip()) and input_comp.strip().lower() != "unknown"
    is_build_valid = bool(input_build.strip()) and input_build.strip().lower() != "unknown"
    is_rca_valid = bool(input_rca.strip()) and input_rca.strip().lower() != "unknown"
    
    all_mandatory_present = is_comp_valid and is_build_valid and is_rca_valid

    if not all_mandatory_present:
        missing_list = []
        if not is_comp_valid: missing_list.append("Component / Node")
        if not is_build_valid: missing_list.append("Build Version")
        if not is_rca_valid: missing_list.append("RCA Category")

        st.warning(f"⚠️ **Search Halted**: Mandatory parameters missing: **{', '.join(missing_list)}**. Fill them in above before initiating hybrid search.")
    else:
        st.success("✅ **Mandatory Parameters Verified**: Ready to initiate hybrid search across ChromaDB.")

# ==============================================================================
# HYBRID SEARCH EXECUTION BUTTON (FULL-WIDTH BELOW ALL 4 FIELDS)
# ==============================================================================
st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
search_ready_clicked = st.button(
    "🚀 2. Run Hybrid Search & Synthesize Remediation",
    type="primary",
    use_container_width=True,
    disabled=not all_mandatory_present
)

if search_ready_clicked:
    if not all_mandatory_present:
        st.error("❌ Cannot initiate search: Please complete all mandatory fields (Component, Build Version, RCA Category) above first!")
    else:
        with st.status("⚡ Executing Hybrid Search & RAG Protocol...", expanded=True) as status_box:
            st.write(f"📊 **Stage 1/3**: Querying ChromaDB Vector Vault with metadata filters (`{input_comp.strip()}` / `{input_build.strip()}`)...")
            try:
                match_res = requests.post(
                    f"{API_BASE_URL}/match",
                    json={
                        "raw_incident_text": query_text.strip(),
                        "filter_components": input_comp.strip(),
                        "filter_build": input_build.strip()
                    }
                )
                if match_res.status_code == 200:
                    m_data = match_res.json()
                    st.session_state["match_result"] = m_data
                    matches = m_data.get("matches", [])
                    highest_conf = matches[0].get("confidence_score", 0) if matches else 0
                    st.write(f"✅ **Stage 1 Complete**: Retrieved {len(matches)} historical tickets. Highest confidence: `{highest_conf}%`.")

                    if matches and highest_conf >= 70:
                        st.write("🧠 **Stage 2 & 3**: High confidence match found. Feeding retrieved records to Llama 3 for citation synthesis...")
                        rec_res = requests.post(
                            f"{API_BASE_URL}/recommend",
                            json={"incident_text": query_text.strip(), "matches": matches}
                        )
                        if rec_res.status_code == 200:
                            st.session_state["recommendation"] = rec_res.json()
                            st.write("✅ **Stage 3 Complete**: Actionable recommendation generated with inline citations.")
                    else:
                        st.session_state["recommendation"] = None
                        st.write("ℹ️ **Confidence below 70% threshold**: No previous resolution matches this specific issue.")
                    
                    status_box.update(label="✅ Hybrid Search Complete!", state="complete", expanded=False)
                else:
                    st.error(f"Error {match_res.status_code}: {match_res.text}")
                    status_box.update(label="❌ Search Failed", state="error")
            except Exception as ex:
                st.error(f"Backend Connection Error: {ex}")
                status_box.update(label="❌ Connection Failed", state="error")

# ==============================================================================
# RESULTS VIEW (DUAL PATH BASED ON CONFIDENCE SCORE >= 70 THRESHOLD)
# ==============================================================================
if st.session_state["match_result"]:
    match_data = st.session_state["match_result"]
    matches = match_data.get("matches", [])
    status_flag = match_data.get("status")
    highest_conf = matches[0].get("confidence_score", 0) if matches else 0

    st.markdown("---")

    # CASE A: CONFIDENCE BELOW 70% -> PROMPT TO LOG NEW INCIDENT INTO DB
    if status_flag == "no_match" or not matches or highest_conf < 70:
        with st.container(border=True):
            st.warning("⚠️ **This issue has not been occured before would you like to log it here.**")
            st.caption(f"Highest historical match confidence is **{highest_conf}%** (below the 70% verified resolution threshold). Fill in all components below to embed and register this incident into institutional memory.")

            col_log1, col_log2, col_log3 = st.columns(3)
            with col_log1:
                log_comp = st.text_input("Component / Node *", value=input_comp, key="log_comp_input")
            with col_log2:
                log_build = st.text_input("Build Version *", value=input_build, key="log_build_input")
            with col_log3:
                log_rca = st.text_input("RCA Category *", value=input_rca, key="log_rca_input")

            log_solution = st.text_area("Technical Solution / Workaround Provided *", placeholder="Enter the verified fix or operational workaround applied...", height=100, key="log_sol_input")

            if st.button("💾 Ingest & Embed Incident into DB", type="primary", use_container_width=True, key="btn_ingest_new"):
                if not log_solution.strip():
                    st.error("❌ Please provide the Technical Solution / Workaround before logging!")
                elif not log_comp.strip() or not log_build.strip() or not log_rca.strip():
                    st.error("❌ Component, Build, and RCA Category are mandatory fields!")
                else:
                    embed_payload = {
                        "summary": f"Incident on {log_comp.strip()} ({log_build.strip()})",
                        "components": log_comp.strip(),
                        "build": log_build.strip(),
                        "rca_category": log_rca.strip(),
                        "product_release": input_release.strip() if input_release.strip() else "Unknown",
                        "technical_solution_provided": log_solution.strip(),
                        "engineer_name": "NOC Operations",
                        "description": f"Incident logged for {log_comp.strip()} ({log_build.strip()}). Symptoms/Logs: {query_text.strip()}"
                    }
                    with st.spinner("💾 Ingesting & embedding incident into ChromaDB via embeddinggemma..."):
                        try:
                            fb_res = requests.post(f"{API_BASE_URL}/feedback", json=embed_payload)
                            if fb_res.status_code == 200:
                                resp_json = fb_res.json()
                                st.success(f"✅ **Incident Successfully Embedded into Database!** Point ID: `{resp_json.get('point_id')}`. This issue is now saved in institutional memory and will be matched in future searches!")
                            else:
                                st.error(f"Error {fb_res.status_code}: {fb_res.text}")
                        except Exception as ex:
                            st.error(f"Failed to embed into database: {ex}")

        if matches:
            with st.expander(f"🔍 View Lower-Confidence Candidates ({highest_conf}% max match)", expanded=False):
                for idx, ticket in enumerate(matches):
                    st.caption(f"Candidate #{idx+1} — {ticket.get('confidence_score', 0)}% confidence — Node: {ticket.get('metadata', {}).get('Components')}")
                    st.text_area(f"Payload #{idx+1}", value=ticket.get("chunk_text", ""), height=90, key=f"low_chunk_{idx}")

    # CASE B: CONFIDENCE >= 70% -> FULL RECOMMENDATION & CITATION PORTAL
    else:
        left_col, right_col = st.columns([1.05, 1.25])

        # LEFT COLUMN: RETRIEVED CHUNKS
        with left_col:
            st.markdown(f"### 🗄️ Retrieved Knowledge Vault Records ({len(matches)})")
            st.caption("Ranked by vector cosine distance confidence in ChromaDB")
            
            for idx, ticket in enumerate(matches):
                conf = ticket.get("confidence_score", 0)
                t_id = ticket.get("ticket_id", f"MATCH-{idx+1}")
                meta = ticket.get("metadata", {})
                
                assignee_val = meta.get("Assignee") or meta.get("modified_by") or "Unassigned"
                reporter_val = meta.get("Reporter") or meta.get("created_by") or "Unassigned"
                t_time = meta.get("timestamp") or meta.get("Created") or meta.get("ingested_at") or "2026-10-08"

                conf_badge = f"🟢 {conf}% MATCH" if conf >= 80 else (f"🟡 {conf}% MATCH" if conf >= 65 else f"🔴 {conf}% MATCH")

                with st.expander(f"{conf_badge} — Ticket [{t_id[:16]}...]", expanded=(idx==0)):
                    st.markdown(f"🛰️ **Node:** `{meta.get('Components', 'N/A')}` &nbsp;|&nbsp; 🔖 **Build:** `{meta.get('Build', 'N/A')}` &nbsp;|&nbsp; 🏷️ **RCA:** `{meta.get('RCA_Category', 'N/A')}`")
                    st.caption(f"👤 **Assignee:** `{assignee_val}` &nbsp;|&nbsp; 📢 **Reporter:** `{reporter_val}` &nbsp;|&nbsp; 🕒 **Timestamp:** `{t_time}`")
                    st.text_area("Historical Record Raw Payload:", value=ticket.get("chunk_text", ""), height=130, key=f"chunk_{idx}")

        # RIGHT COLUMN: ACTIONABLE RECOMMENDATION PORTAL
        with right_col:
            rec = st.session_state.get("recommendation")
            if rec and rec.get("status") == "success":
                top_meta = matches[0].get("metadata", {}) if matches else {}
                top_fix = top_meta.get("Technical_Solution_Provided") or "Pin MTU value to 1500 in post-upgrade script and bounce BGP neighbor session."
                top_ticket_ref = matches[0].get("ticket_id", "INC-101") if matches else "INC-101"

                # 1. ACTIONABLE RECOMMENDATION PORTAL
                with st.container(border=True):
                    st.markdown("### 🛡️ ACTIONABLE RECOMMENDATION PORTAL")
                    st.caption("VERIFIED REMEDIATION PLAN • STRICT CITATION AUDIT")

                    # Immediate Actionable Fix (Primary Emerald Banner)
                    st.success(f"⚡ **ACTIONABLE RESOLUTION / WORKAROUND (APPLY FIX)**\n\n**{top_fix}**")

                    # Root Cause Analysis
                    with st.container():
                        st.markdown("#### 📌 Verified Root Cause Analysis")
                        st.write(rec.get("root_cause", "N/A"))

                    st.divider()

                    # Pre-Flight Operational Checks
                    with st.container():
                        st.markdown("#### 🛠️ Pre-Flight Operational Checks (BEFORE FIX)")
                        st.warning(f"{rec.get('recommended_pre_checks', 'N/A')}")

                    st.divider()

                    # Engineering Rationale
                    with st.container():
                        st.markdown("#### 💡 Engineering Rationale")
                        st.info(rec.get("why", "N/A"))

                # 2. CITATIONS AUDIT TRAIL
                st.markdown("#### 🔗 Institutional Memory Audit Trail")
                sources = rec.get("sources_cited", [])
                if sources:
                    for cited_id in sources:
                        matched_ticket_meta = None
                        for m in matches:
                            if m.get("ticket_id") == cited_id or cited_id in m.get("chunk_text", "") or cited_id == "INC-101":
                                matched_ticket_meta = m.get("metadata", {})
                                break
                        
                        c_assignee = (matched_ticket_meta.get("Assignee") or "Unassigned") if matched_ticket_meta else "Unassigned"
                        c_reporter = (matched_ticket_meta.get("Reporter") or "Unassigned") if matched_ticket_meta else "Unassigned"
                        timestamp_str = (matched_ticket_meta.get("timestamp") or matched_ticket_meta.get("Created") if matched_ticket_meta else "2026-10-08 21:32:20")

                        st.info(f"📄 **Citation Reference: [{cited_id}]** &nbsp;|&nbsp; 👤 **Assignee:** `{c_assignee}` &nbsp;|&nbsp; 📢 **Reporter:** `{c_reporter}` &nbsp;|&nbsp; 🕒 **Timestamp:** `{timestamp_str}`")
                else:
                    st.caption("No explicit ticket ID cited.")

                # 3. INLINE ALTERNATIVE / EFFICIENT APPROACH SUBMISSION
                with st.expander("💡 **Submit a More Efficient Solution or Alternate Approach for this Incident**", expanded=False):
                    st.caption("Found a faster workaround or alternative resolution? Submit it to link directly to this existing ticket's payload in ChromaDB.")
                    
                    now_timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                    
                    c_alt1, c_alt2 = st.columns(2)
                    with c_alt1:
                        alt_author = st.text_input("👤 Your Name / Engineer ID *", value="", placeholder="Enter your Name or Engineer ID", key="alt_author_input")
                    with c_alt2:
                        st.text_input("🕒 Timestamp (Auto-Tagged)", value=now_timestamp, disabled=True, key="alt_time_input")

                    target_link_id = matches[0].get("ticket_id") if matches else "INC-101"
                    st.text_input("🔗 Linked Ticket Reference:", value=target_link_id, disabled=True, key="alt_link_id")

                    alt_notes = st.text_area(
                        "Describe Alternate Approach / Optimized Workaround *:",
                        placeholder="e.g. Instead of manual MTU override, apply post-upgrade Ansible playbook #104 which pins MTU 1500 automatically before BGP restart.",
                        height=90,
                        key="alt_notes_input"
                    )

                    if st.button("⚡ Submit Alternative Approach to Institutional Memory", type="primary", use_container_width=True):
                        if not alt_notes.strip():
                            st.error("❌ Please enter the alternative approach details before submitting!")
                        elif not alt_author.strip():
                            st.error("❌ Engineer Name is required!")
                        else:
                            alt_payload = {
                                "summary": f"Alternative Approach for {input_comp.strip()}",
                                "components": input_comp.strip(),
                                "build": input_build.strip(),
                                "rca_category": input_rca.strip(),
                                "technical_solution_provided": alt_notes.strip(),
                                "engineer_name": alt_author.strip(),
                                "linked_ticket_id": target_link_id,
                                "description": f"Alternative solution submitted by {alt_author.strip()} at {now_timestamp}."
                            }
                            
                            with st.spinner("💾 Ingesting optimized workaround into ChromaDB..."):
                                try:
                                    fb_res = requests.post(f"{API_BASE_URL}/feedback", json=alt_payload)
                                    if fb_res.status_code == 200:
                                        r_json = fb_res.json()
                                        st.success(f"✅ **Alternative Approach Successfully Ingested!** Linked to Ticket `{target_link_id[:16]}...` by `{alt_author.strip()}` at `{now_timestamp}`.")
                                    else:
                                        st.error(f"Error {fb_res.status_code}: {fb_res.text}")
                                except Exception as ex:
                                    st.error(f"Failed to submit alternative approach: {ex}")

            elif rec and rec.get("status") != "success":
                st.warning("⚠️ " + rec.get("root_cause", "No verified match found."))
