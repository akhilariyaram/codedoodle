from datetime import datetime
import uuid
import chromadb
import ollama

# Initialize Chroma client (persistent storage on disk, change path as needed)
chroma_client = chromadb.PersistentClient(path="./chroma_db")


def ingest_data(
    summary: str,
    Issue_Type: str,
    Assignee: str,
    Components: str,
    Created: datetime,
    Priority: str,
    Reporter: str,
    Build: str,
    Customers: list[str],
    Market: str,
    Product_Release: str,
    RCA_Category: str,
    Sub_Components: str,
    Technical_Solution_Provided: str,
    Technology: list[str],
    Description: str,
    collection_name: str = "jira_db",
) -> str:
    """
    Combines all parameters into a single string, generates an embedding
    via local Ollama, and stores the vector, metadata, and document in ChromaDB.
    """

    # 1. Combine all parameters into one string so they are all embedded together
    technology_str = ", ".join(Technology) if isinstance(Technology, list) else str(Technology)
    customers_str = ", ".join(Customers) if isinstance(Customers, list) else str(Customers)
    
    created_str = Created.strftime("%Y-%m-%d %H:%M:%S") if isinstance(Created, datetime) else str(Created)
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    combined_content = (
        f"summary: {summary}\n"
        f"Issue_type: {Issue_Type}\n"
        f"Assignee: {Assignee}\n"
        f"Components: {Components}\n"
        f"Created: {created_str}\n"
        f"Priority: {Priority}\n"
        f"Reporter: {Reporter}\n"
        f"Build: {Build}\n"
        f"Customers: {customers_str}\n"
        f"Market: {Market}\n"
        f"Product_Release: {Product_Release}\n"
        f"RCA_Category: {RCA_Category}\n"
        f"Sub_components: {Sub_Components}\n"
        f"Technical_Solution_Provided: {Technical_Solution_Provided}\n"
        f"Technology: {technology_str}\n"
        f"Description: {Description}\n"
        f"Modified_By: {Assignee}\n"
        f"Timestamp: {now_str}\n"
    )

    # 2. Generate embedding from local Ollama model using the combined content
    response = ollama.embeddings(model="embeddinggemma", prompt=combined_content)
    vector = response["embedding"]

    # 3. Prepare metadata dictionary
    point_id = str(uuid.uuid4())
    metadata = {
        "summary": summary,
        "Issue_Type": Issue_Type,
        "Assignee": Assignee,
        "Components": Components,
        "Created": created_str,
        "Priority": Priority,
        "Reporter": Reporter,
        "Build": Build,
        "Customers": customers_str,
        "Market": Market,
        "Product_Release": Product_Release,
        "RCA_Category": RCA_Category,
        "Sub_Components": Sub_Components,
        "Technical_Solution_Provided": Technical_Solution_Provided,
        "Technology": technology_str,
        "ingested_at": datetime.utcnow().isoformat(),
        "created_by": Reporter or Assignee or "NOC Specialist",
        "modified_by": Assignee or "NOC Engineer",
        "timestamp": now_str
    }

    # 4. Get or create collection in ChromaDB
    collection = chroma_client.get_or_create_collection(name=collection_name)

    # 5. Store/upsert into ChromaDB
    collection.upsert(
        ids=[point_id],
        embeddings=[vector],
        metadatas=[metadata],
        documents=[combined_content],
    )

    return point_id


if __name__ == "__main__":
    sample_id = ingest_data(
        summary="Login button unclickable on mobile view",
        Issue_Type="Bug",
        Assignee="John Doe",
        Components="UI Frontend",
        Created=datetime.now(),
        Priority="High",
        Reporter="Alice Smith",
        Build="v2.4.1",
        Customers=["Acme Corp", "Globex"],
        Market="North America",
        Product_Release="Q3 Release",
        RCA_Category="CSS Styling",
        Sub_Components="Mobile Header",
        Technical_Solution_Provided="Updated media query breakpoints in stylesheet.",
        Technology=["React", "CSS", "TypeScript"],
        Description="Users on iOS Safari report that the main sign-in button overlaps with the footer banner.",
        collection_name="jira_tickets",
    )
    print(f"ChromaDB Ingestion Successful! Point ID: {sample_id}")
