"""
seed_db.py - Seed 10 realistic Telecom Incident records into ChromaDB
"""
import sys
from datetime import datetime
from ingestion_data import ingest_data, chroma_client

# 10 Detailed Telecom Incidents for Hackathon MVP Testing
SAMPLE_TICKETS = [
    {
        "summary": "BGP session flapping on edge router CMG-12 after firmware push",
        "Issue_Type": "Incident",
        "Assignee": "Alex Rivera",
        "Components": "CMG-12",
        "Created": datetime.now(),
        "Priority": "Critical",
        "Reporter": "NOC Operator 1",
        "Build": "14.2",
        "Customers": ["Vodafone", "AT&T Enterprise"],
        "Market": "North America",
        "Product_Release": "Q3 Core Upgrade",
        "RCA_Category": "Firmware MTU Reset",
        "Sub_Components": "BGP Daemon",
        "Technical_Solution_Provided": "Firmware upgrade 14.2 reset default MTU from 1500 to 1400 causing packet drops. Solution: Pinned MTU to 1500 in post-upgrade script and cleared BGP session.",
        "Technology": ["BGP", "Cisco", "Routing"],
        "Description": "Edge router CMG-12 experienced recurring BGP neighbor flaps following the 14.2 release upgrade due to MTU mismatch."
    },
    {
        "summary": "High latency and packet loss on 5G UPF node UPF-CORE-01",
        "Issue_Type": "Incident",
        "Assignee": "Priya Sharma",
        "Components": "UPF-CORE-01",
        "Created": datetime.now(),
        "Priority": "High",
        "Reporter": "SNOC Alert Automation",
        "Build": "v3.1.0",
        "Customers": ["T-Mobile", "Verizon Wireless"],
        "Market": "Global 5G Core",
        "Product_Release": "5G Standalone Release 2",
        "RCA_Category": "Kernel Buffer Exhaustion",
        "Sub_Components": "GTP-U Packet Processor",
        "Technical_Solution_Provided": "Increased socket receive buffer net.core.rmem_max to 67108864 in sysctl.conf and restarted UPF service container.",
        "Technology": ["5G Core", "UPF", "Linux Kernel"],
        "Description": "User plane function UPF-CORE-01 dropped GTP-U packets during peak hour traffic under heavy payload."
    },
    {
        "summary": "Login button unclickable on mobile view in Customer Self-Care Portal",
        "Issue_Type": "Bug",
        "Assignee": "John Doe",
        "Components": "UI Frontend",
        "Created": datetime.now(),
        "Priority": "Medium",
        "Reporter": "Alice Smith",
        "Build": "v2.4.1",
        "Customers": ["Acme Corp", "Globex"],
        "Market": "North America",
        "Product_Release": "Q3 Release",
        "RCA_Category": "CSS Breakpoint Overlap",
        "Sub_Components": "Mobile Header",
        "Technical_Solution_Provided": "Updated viewport media queries in header.css to prevent fixed footer banner from overlapping the sign-in submit button on screens under 768px.",
        "Technology": ["React", "CSS", "TypeScript"],
        "Description": "Users on iOS Safari report that the main sign-in button overlaps with the footer banner."
    },
    {
        "summary": "Voice call setup failure on IMS CSCF node P-CSCF-04",
        "Issue_Type": "Incident",
        "Assignee": "Marcus Vance",
        "Components": "P-CSCF-04",
        "Created": datetime.now(),
        "Priority": "High",
        "Reporter": "Voice NOC Specialist",
        "Build": "22.3",
        "Customers": ["Orange Telecom", "Telefonica"],
        "Market": "EMEA",
        "Product_Release": "VoLTE Enterprise Pack",
        "RCA_Category": "SIP Timer T1 Timeout",
        "Sub_Components": "SIP Signaling Stack",
        "Technical_Solution_Provided": "Adjusted SIP retransmission timer T1 from 500ms to 1000ms for high latency backhaul connections.",
        "Technology": ["IMS", "SIP", "VoLTE"],
        "Description": "VoLTE subscribers experiencing 504 Server Timeout during call origination over satellite backhaul."
    },
    {
        "summary": "5G gNodeB cell drop on site RAN-NORTH-88",
        "Issue_Type": "Incident",
        "Assignee": "David Chen",
        "Components": "RAN-NORTH-88",
        "Created": datetime.now(),
        "Priority": "Critical",
        "Reporter": "RAN Operations",
        "Build": "v4.0.2",
        "Customers": ["Telstra", "Singtel"],
        "Market": "APAC",
        "Product_Release": "NR RAN Release 4",
        "RCA_Category": "CPRI Fiber Link Mismatch",
        "Sub_Components": "Remote Radio Unit (RRU)",
        "Technical_Solution_Provided": "Cleaned optical SFP transceiver connector on RRU port 2 and re-calibrated CPRI line rate to Option 7.",
        "Technology": ["5G RAN", "CPRI", "gNodeB"],
        "Description": "Baseband unit reported loss of signal alarms on CPRI port connecting to Remote Radio Unit."
    },
    {
        "summary": "SMS Gateway queue backup on SMSC-WEST-02",
        "Issue_Type": "Incident",
        "Assignee": "Elena Rostova",
        "Components": "SMSC-WEST-02",
        "Created": datetime.now(),
        "Priority": "High",
        "Reporter": "Messaging NOC",
        "Build": "v1.8.4",
        "Customers": ["Enterprise Banking Clients"],
        "Market": "LATAM",
        "Product_Release": "A2P Messaging v1",
        "RCA_Category": "SMPP Throttling Limit",
        "Sub_Components": "SMPP Ingress Queue",
        "Technical_Solution_Provided": "Increased SMPP bind rate limit per enterprise client from 50 msg/s to 200 msg/s and restarted queue worker daemon.",
        "Technology": ["SMSC", "SMPP", "Telecom Messaging"],
        "Description": "OTP SMS deliveries delayed by over 10 minutes due to message queue throttling."
    },
    {
        "summary": "Memory leak causing OOM crashes on HSS database subscriber node HSS-DB-01",
        "Issue_Type": "Incident",
        "Assignee": "Karan Patel",
        "Components": "HSS-DB-01",
        "Created": datetime.now(),
        "Priority": "Critical",
        "Reporter": "Subscriber DB Admin",
        "Build": "v5.2.0",
        "Customers": ["Global Roaming Partners"],
        "Market": "Global",
        "Product_Release": "Subscriber Core 5",
        "RCA_Category": "Java Heap Memory Leak",
        "Sub_Components": "Diameter Session Cache",
        "Technical_Solution_Provided": "Applied patch v5.2.1 addressing unclosed Diameter session context handles and increased JVM MaxMetaspaceSize to 4G.",
        "Technology": ["HSS", "Diameter", "Java"],
        "Description": "Home Subscriber Server node crashed twice during peak subscriber registration hours due to OutOfMemory exception."
    },
    {
        "summary": "OTN Optical Switch link degradation on Ring-Alpha",
        "Issue_Type": "Incident",
        "Assignee": "Sven Lindqvist",
        "Components": "OTN-ALPHA-MUX",
        "Created": datetime.now(),
        "Priority": "Medium",
        "Reporter": "Optical Transport Team",
        "Build": "v12.0",
        "Customers": ["Wholesale Transit Operators"],
        "Market": "Europe",
        "Product_Release": "Optical Backbone v12",
        "RCA_Category": "Fiber Attenuation Drift",
        "Sub_Components": "EDFA Amplifier Card",
        "Technical_Solution_Provided": "Adjusted EDFA optical amplifier gain profile by +2.5 dB and rescheduled physical OTDR fiber span audit.",
        "Technology": ["OTN", "DWDM", "Optical"],
        "Description": "Bit error rate (BER) alarms triggered on 100G transponder channel 32."
    },
    {
        "summary": "Billing CDR ingestion failure on Rating Engine node RE-03",
        "Issue_Type": "Incident",
        "Assignee": "Sarah Jenkins",
        "Components": "Rating Engine RE-03",
        "Created": datetime.now(),
        "Priority": "High",
        "Reporter": "Billing Operations",
        "Build": "v3.8.1",
        "Customers": ["Retail Mobile Subscribers"],
        "Market": "North America",
        "Product_Release": "Rating Engine 3.8",
        "RCA_Category": "Schema Validation Error",
        "Sub_Components": "ASN.1 File Parser",
        "Technical_Solution_Provided": "Updated ASN.1 CDR parser schema definition to support new 5G roaming data usage field structure.",
        "Technology": ["Billing", "CDR", "ASN.1"],
        "Description": "Rating engine dropped 150,000 unrated roaming call detail records due to unexpected field length."
    },
    {
        "summary": "DNS resolution timeout for internal NOC management domains",
        "Issue_Type": "Incident",
        "Assignee": "Michael Scott",
        "Components": "NOC-DNS-01",
        "Created": datetime.now(),
        "Priority": "Medium",
        "Reporter": "IT Helpdesk",
        "Build": "v9.18",
        "Customers": ["Internal NOC Operations"],
        "Market": "Internal Infrastructure",
        "Product_Release": "IT Core Infra",
        "RCA_Category": "BIND Cache Lock Contention",
        "Sub_Components": "BIND Resolver Engine",
        "Technical_Solution_Provided": "Upgraded BIND9 daemon configuration to enable rndc reconfig and tuned max-cache-size parameters.",
        "Technology": ["DNS", "BIND", "Infrastructure"],
        "Description": "NOC monitoring dashboards failed to resolve telemetry hostnames during network maintenance."
    }
]


def seed_database(collections=["jira_tickets"]):
    print("🚀 Starting ChromaDB Data Ingestion for 10 Telecom Incidents...")
    for target_col in collections:
        print(f"\n📦 Seeding collection: '{target_col}'...")
        count = 0
        for ticket in SAMPLE_TICKETS:
            try:
                point_id = ingest_data(
                    summary=ticket["summary"],
                    Issue_Type=ticket["Issue_Type"],
                    Assignee=ticket["Assignee"],
                    Components=ticket["Components"],
                    Created=ticket["Created"],
                    Priority=ticket["Priority"],
                    Reporter=ticket["Reporter"],
                    Build=ticket["Build"],
                    Customers=ticket["Customers"],
                    Market=ticket["Market"],
                    Product_Release=ticket["Product_Release"],
                    RCA_Category=ticket["RCA_Category"],
                    Sub_Components=ticket["Sub_Components"],
                    Technical_Solution_Provided=ticket["Technical_Solution_Provided"],
                    Technology=ticket["Technology"],
                    Description=ticket["Description"],
                    collection_name=target_col
                )
                count += 1
                print(f"  [+] Ingested Ticket #{count}: {ticket['Components']} ({ticket['Build']}) -> Point ID: {point_id}")
            except Exception as e:
                print(f"  [-] Failed to ingest ticket '{ticket['summary']}': {e}")
        
        print(f"✅ Collection '{target_col}' populated with {count} records!")

if __name__ == "__main__":
    seed_database()
