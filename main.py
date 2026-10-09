import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import ollama

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("agent_backend")

def log_stage(endpoint: str, stage: int, message: str):
    logger.info(f"[{endpoint}] STAGE {stage}: {message}")

# Import existing core modules
from match import execute_agentic_match
from recommendations import generate_recommendation
from ingest_data import ingest_data

app = FastAPI(
    title="AI Incident Learning & Prevention Agent API",
    description="Agentic RAG R&D API for Telecom Incident Prevention and Continuous Learning",
    version="1.0.0",
)

# Enable CORS for Streamlit / Frontend interaction
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# PYDANTIC REQUEST & RESPONSE MODELS
# ==========================================

class MatchRequest(BaseModel):
    raw_incident_text: str = Field(..., description="Raw incident text, symptom description, or MOP log")
    filter_components: Optional[str] = Field(None, description="Optional override component filter")
    filter_build: Optional[str] = Field(None, description="Optional override build version filter")

class RecommendRequest(BaseModel):
    incident_text: str = Field(..., description="Raw incident text or symptom description")
    matches: List[Dict[str, Any]] = Field(default=[], description="List of matched historical ticket objects")

class ExtractResolutionRequest(BaseModel):
    raw_notes: str = Field(..., description="Messy resolution notes pasted by the engineer")

class FeedbackRequest(BaseModel):
    summary: str = Field(..., description="Summary of the incident resolution")
    components: str = Field(..., description="Target node/component involved (e.g. CMG-12, UI Frontend)")
    build: str = Field(..., description="Target build or release version (e.g. v2.4.1, 14.2)")
    rca_category: str = Field(..., description="Root Cause Analysis category")
    technical_solution_provided: str = Field(..., description="Detailed solution or workaround")
    technology: List[str] = Field(default=["Telecom Core", "Networking"], description="Technologies involved")
    issue_type: str = Field("Incident", description="Issue classification type")
    assignee: str = Field("AI Verified Engineer", description="Engineer assigned")
    engineer_name: Optional[str] = Field("NOC Engineer", description="Name of the engineer submitting or modifying")
    priority: str = Field("High", description="Ticket priority level")
    reporter: str = Field("NOC Specialist", description="Reporter of the incident")
    customers: List[str] = Field(default=["Enterprise Global"], description="Impacted customers list")
    market: str = Field("Global Telecom", description="Market sector")
    product_release: str = Field("Q4 Release", description="Product release string")
    sub_components: str = Field("Core Subsystem", description="Sub-component details")
    description: str = Field("", description="Full incident description and additional context")
    linked_ticket_id: Optional[str] = Field(None, description="Optional existing Ticket ID to link optimized solution")


# ==========================================
# API ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "AI Incident Learning & Prevention Agent API",
        "version": "1.0.0"
    }


@app.post("/match")
def match_incident(payload: MatchRequest):
    endpoint = "POST /match"
    log_stage(endpoint, 1, f"Received incident query: '{payload.raw_incident_text[:60]}...'")
    
    try:
        log_stage(endpoint, 2, "Executing Agentic Match & Extraction...")
        match_result = execute_agentic_match(
            user_query=payload.raw_incident_text,
            collection_name="jira_tickets",
            filter_components=payload.filter_components,
            filter_build=payload.filter_build
        )
        
        status_flag = match_result.get("status", "unknown")
        matches = match_result.get("matches", [])
        fingerprint = match_result.get("fingerprint", {})
        
        log_stage(endpoint, 3, f"Agentic Match Finished. Status: '{status_flag}', Component: '{fingerprint.get('components')}', Build: '{fingerprint.get('build_version')}', Matches Found: {len(matches)}")

        return {
            "status": status_flag,
            "message": match_result.get("message", ""),
            "matches": matches,
            "extracted_fingerprint": fingerprint
        }

    except Exception as e:
        logger.error(f"[{endpoint}] FAILED at runtime: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during agentic match execution: {str(e)}"
        )


@app.post("/recommend")
def recommend_fix(payload: RecommendRequest):
    endpoint = "POST /recommend"
    log_stage(endpoint, 1, f"Received request to synthesize advice from {len(payload.matches)} historical matches.")
    
    try:
        log_stage(endpoint, 2, "Formatting context chunks and prompting Llama 3 with strict citation guardrails...")
        json_str_advice = generate_recommendation(
            current_incident_text=payload.incident_text,
            matched_records=payload.matches,
            model_name="llama3"
        )
        parsed_advice = json.loads(json_str_advice)
        
        log_stage(endpoint, 3, f"Recommendation Synthesis Completed. Status: '{parsed_advice.get('status')}', Sources Cited: {parsed_advice.get('sources_cited', [])}")
        return parsed_advice

    except Exception as e:
        logger.error(f"[{endpoint}] FAILED at runtime: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recommendation: {str(e)}"
        )


@app.post("/extract_resolution")
def extract_resolution(payload: ExtractResolutionRequest):
    endpoint = "POST /extract_resolution"
    log_stage(endpoint, 1, f"Received messy resolution notes ({len(payload.raw_notes)} chars).")
    
    try:
        log_stage(endpoint, 2, "Structuring resolution notes using Llama 3 JSON format...")
        system_prompt = """You are an AI Telecom Systems Engineer.
Extract structured incident resolution details from messy engineer notes.
Output strictly JSON matching this structure:
{
  "summary": "Brief summary of the issue and fix",
  "components": "Target node or hardware component name (e.g. CMG-12, UI Frontend). Use 'Unknown' if missing.",
  "build": "Software build or version (e.g. v2.4.1, 14.2). Use 'Unknown' if missing.",
  "rca_category": "Root cause category (e.g. Firmware Reset, MTU Mismatch, Memory Leak, Config Drift)",
  "technical_solution_provided": "Detailed step-by-step resolution or workaround applied",
  "technology": ["List", "of", "technologies", "involved"]
}"""

        response = ollama.chat(
            model="llama3",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.raw_notes}
            ],
            format="json",
            options={"temperature": 0.1}
        )

        extracted_data = json.loads(response["message"]["content"])
        
        if not isinstance(extracted_data.get("technology"), list):
            extracted_data["technology"] = ["Telecom Core"]
        if not extracted_data.get("components"):
            extracted_data["components"] = "Unknown"
        if not extracted_data.get("build"):
            extracted_data["build"] = "Unknown"

        log_stage(endpoint, 3, f"Extraction Complete -> Component: '{extracted_data['components']}', Build: '{extracted_data['build']}', RCA: '{extracted_data.get('rca_category')}'")
        return extracted_data

    except Exception as e:
        logger.error(f"[{endpoint}] FAILED at runtime: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing resolution notes: {str(e)}"
        )


@app.post("/feedback")
def save_feedback(payload: FeedbackRequest):
    endpoint = "POST /feedback"
    author_name = payload.engineer_name or payload.assignee or "NOC Engineer"
    log_stage(endpoint, 1, f"Received human-verified feedback from '{author_name}' for component '{payload.components}' build '{payload.build}'.")
    
    try:
        effective_summary = payload.summary
        current_time_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        effective_description = payload.description or f"Verified solution by {author_name} at {current_time_str}."

        if payload.linked_ticket_id and payload.linked_ticket_id.strip():
            log_stage(endpoint, 2, f"Linking alternative approach to existing Ticket ID: '{payload.linked_ticket_id.strip()}' by '{author_name}'")
            effective_summary = f"[Optimized Approach for {payload.linked_ticket_id.strip()}] {payload.summary}"
            effective_description += f"\n\n[ALTERNATIVE APPROACH]: Submitted by {author_name} at {current_time_str} for ticket {payload.linked_ticket_id.strip()}:\n{payload.technical_solution_provided}"
        else:
            log_stage(endpoint, 2, f"Registering new verified incident record submitted by {author_name}.")

        log_stage(endpoint, 3, "Generating embedding via Ollama 'embeddinggemma' and storing in ChromaDB collection 'jira_db'...")
        point_id = ingest_data(
            summary=effective_summary,
            Issue_Type=payload.issue_type,
            Assignee=author_name,
            Components=payload.components,
            Created=datetime.utcnow(),
            Priority=payload.priority,
            Reporter=author_name,
            Build=payload.build,
            Customers=payload.customers,
            Market=payload.market,
            Product_Release=payload.product_release,
            RCA_Category=payload.rca_category,
            Sub_Components=payload.sub_components,
            Technical_Solution_Provided=payload.technical_solution_provided,
            Technology=payload.technology,
            Description=effective_description,
            collection_name="jira_tickets"
        )

        log_stage(endpoint, 4, f"Ingestion Complete! Point ID: {point_id}, Author: '{author_name}', Timestamp: '{current_time_str}'")
        return {
            "status": "success",
            "point_id": point_id,
            "engineer_name": author_name,
            "timestamp": current_time_str,
            "linked_ticket_id": payload.linked_ticket_id,
            "message": f"Successfully ingested verified learning into ChromaDB by {author_name} at {current_time_str} (ID: {point_id})."
        }

    except Exception as e:
        logger.error(f"[{endpoint}] FAILED at runtime: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving feedback to vector DB: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
