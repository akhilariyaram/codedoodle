import json
import sys
from datetime import datetime

# UTF-8 for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from ingestion_data import ingest_data, chroma_client

def load_concatenated_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    decoder = json.JSONDecoder()
    pos = 0
    records = []
    while pos < len(content):
        while pos < len(content) and content[pos].isspace():
            pos += 1
        if pos >= len(content):
            break
        try:
            obj, end_pos = decoder.raw_decode(content, pos)
            records.append(obj)
            pos = end_pos
        except Exception as e:
            print(f"Error decoding at pos {pos}: {e}")
            break
    return records

def embed_all(target_collection="jira_tickets"):
    records = load_concatenated_json("tickets.json")
    print(f"Loaded {len(records)} tickets from tickets.json.")
    print(f"Target ChromaDB Collection: '{target_collection}' and 'jira_db'")

    for i, t in enumerate(records, 1):
        summary = t.get("summary", "Untitled Ticket")
        components = t.get("Components", "Unknown")
        build = t.get("Build", "Unknown")
        print(f"[{i}/{len(records)}] Ingesting -> Component: '{components}', Build: '{build}' | {summary[:50]}...")
        
        # Ingest into jira_tickets
        ingest_data(
            summary=summary,
            Issue_Type=t.get("Issue_Type", "Knowledge Base"),
            Assignee=t.get("Assignee", "Unassigned"),
            Components=components,
            Created=t.get("Created", datetime.utcnow().isoformat()),
            Priority=t.get("Priority", "Medium"),
            Reporter=t.get("Reporter", "System"),
            Build=build,
            Customers=t.get("Customers", []),
            Market=t.get("Market", "Global"),
            Product_Release=t.get("Product_Release", "Unknown"),
            RCA_Category=t.get("RCA_Category", "Other"),
            Sub_Components=t.get("Sub_Components", "General"),
            Technical_Solution_Provided=t.get("Technical_Solution_Provided", "No solution recorded."),
            Technology=t.get("Technology", ["Telecom"]),
            Description=t.get("Description", summary),
            collection_name=target_collection
        )

        # Also ingest into jira_db for full backward compatibility
        ingest_data(
            summary=summary,
            Issue_Type=t.get("Issue_Type", "Knowledge Base"),
            Assignee=t.get("Assignee", "Unassigned"),
            Components=components,
            Created=t.get("Created", datetime.utcnow().isoformat()),
            Priority=t.get("Priority", "Medium"),
            Reporter=t.get("Reporter", "System"),
            Build=build,
            Customers=t.get("Customers", []),
            Market=t.get("Market", "Global"),
            Product_Release=t.get("Product_Release", "Unknown"),
            RCA_Category=t.get("RCA_Category", "Other"),
            Sub_Components=t.get("Sub_Components", "General"),
            Technical_Solution_Provided=t.get("Technical_Solution_Provided", "No solution recorded."),
            Technology=t.get("Technology", ["Telecom"]),
            Description=t.get("Description", summary),
            collection_name="jira_db"
        )

    print(f"\nSUCCESS: All {len(records)} tickets embedded into ChromaDB '{target_collection}' and 'jira_db'!")

if __name__ == "__main__":
    embed_all("jira_tickets")
