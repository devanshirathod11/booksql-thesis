import os
import pandas as pd
from openai import OpenAI

# ================= CONFIGURATION =================
# 1. vLLM Server Details
VLLM_API_KEY = "EMPTY"
VLLM_API_URL = "http://192.168.7.176:5404/v1" # <--- REPLACE WITH YOUR VLLM URL
MODEL_ID = "/data/UC-5/DYNAMIC_SQL_QUERY/Qwen2_5_VL_7B_Instruct/" # <--- REPLACE WITH YOUR MODEL ID

# 2. Data Path (Where your thesis_datasets folder is)
THESIS_DATA_PATH = "./thesis_datasets"

# 3. Output File
OUTPUT_FILE = "results_thesis_stratified_v1.csv"

# 4. Specific Industry Questions (Testing T-FAF Metrics)
TEST_SCENARIOS = {
    "Hospitality": [
        "What is the total revenue from Room Rent in Q1 2023?" 
        "How many unique guests stayed in the hotel in March?"
        "List the top 5 services availed by guests in February 2022."
        "Calculate the average length of stay for guests in January 2024."
        "What is the total expenditure on Food & Beverages in 2023 and 2024?"
        # Metric: ASV (Stock vs Flow)
    ],
    "Service": [
        "List all clients who paid for Design Consulting services." 
        "What is the total revenue generated from IT Support services in 2023?"
        "Calculate the average project duration for completed projects in 2022."
        "How many service tickets were resolved in Q4 2023?"
        "What is the total cost incurred for outsourced services in 2023?"
        # Metric: SDE (Schema Hallucination check)
    ],
    "Construction": [
        "Calculate the total cost of Job Materials for all projects." 
        "List the top 3 suppliers by total purchase amount in 2023."
        "What is the average labor cost per project in 2022?"
        "How many active projects were there in Q2 2023?"
        "What is the total revenue from completed projects in 2023?"
        # Metric: RSI (Complex Joins)
    ]
}
# =================================================

client = OpenAI(api_key=VLLM_API_KEY, base_url=VLLM_API_URL)

def get_schema_from_headers(folder_path):
    context = ""
    for filename in os.listdir(folder_path):
        if filename.endswith(".csv"):
            path = os.path.join(folder_path, filename)
            df = pd.read_csv(path, nrows=1)
            cols = [c.strip().lower().replace(" ", "_") for c in df.columns if "unnamed" not in c.lower()]
            context += f"Table: {filename.replace('.csv', '')}\nColumns: {', '.join(cols)}\n\n"
    return context

def run_experiment():
    print(f"--- STARTING EXPERIMENT B: THESIS STRATIFIED DATA ---")
    print(f"Connecting to vLLM at: {VLLM_API_URL}")
    
    results = []

    for industry, questions in TEST_SCENARIOS.items():
        print(f"\nProcessing Industry: {industry}")
        
        # 1. Point to the specific Industry Folder
        ind_path = os.path.join(THESIS_DATA_PATH, industry)
        if not os.path.exists(ind_path):
            print(f"Skipping {industry} (Folder not found)")
            continue
            
        # 2. Build Context for THIS industry only
        schema_context = get_schema_from_headers(ind_path)

        for q in questions:
            print(f"Asking: {q}")
            
            prompt = f"""You are a Financial SQL expert for a {industry} company.
The database contains data for THIS company only.
Think step-by-step about the Accounting Logic (Account Types, Flows) before writing SQL.

### Schema:
{schema_context}

### User Question:
{q}

### Response (Step-by-Step Logic + SQL):
"""

            response = client.chat.completions.create(
                model=MODEL_ID,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            results.append({
                "Dataset_Type": "Thesis_Stratified",
                "Industry": industry,
                "Question": q,
                "Generated_Output": answer
            })

    # Save
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
    print(f"Done. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_experiment()