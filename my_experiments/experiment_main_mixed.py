import os
import pandas as pd
from openai import OpenAI
import csv

# ================= CONFIGURATION =================
# 1. vLLM Server Details
VLLM_API_KEY = "EMPTY" # vLLM usually doesn't need a key, or use yours
VLLM_API_URL = "http://192.168.7.176:5404/v1" # <--- REPLACE WITH YOUR VLLM URL
MODEL_ID = "/data/UC-5/DYNAMIC_SQL_QUERY/Qwen2_5_VL_7B_Instruct/" # <--- REPLACE WITH YOUR MODEL ID

# 2. Data Path (Where the raw, big CSVs are)
MAIN_DATA_PATH = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/Tables/" 

# 3. Output File
OUTPUT_FILE = "results_main_mixed_v1.csv"

# 4. Test Questions (Designed to fail on mixed data)
TEST_QUESTIONS = [
    "What is the total revenue for the company?", # Risk: Summing all 27 companies
    "Calculate the total cost of Job Materials.", # Risk: Summing materials across unrelated projects
    "List the top 5 customers by balance.",        # Risk: Listing customers from wrong businesses
    "which product did most of our income come from Last month?" , # Risk: Mixing products across companies
    "What is the average payment amount received?", # Risk: Averaging payments across businesses
    "Show me the total expenses for each department.", # Risk: Mixing departments from different companies
    "How many vendors do we have in total?", # Risk: Counting vendors across all companies
    "What is the total number of employees?", # Risk: Counting employees from all businesses
    "List the top 3 payment methods used by our customers.", # Risk: Mixing payment methods across companies
    "What is the total sales amount for each product/service?" # Risk: Mixing sales data across companies   
]

# =================================================

client = OpenAI(api_key=VLLM_API_KEY, base_url=VLLM_API_URL)

def get_schema_from_headers(folder_path):
    """
    Reads only headers from CSVs to build context without loading 1M rows.
    """
    context = ""
    # List of key tables to include in context
    target_files = ["Master_txn_table.csv", "customer_table.csv", "chart_of_account_OB.csv", "employee_table.csv", "payment_method.csv", "product_service_table.csv", "vendor_table.csv"]
    
    for filename in target_files:
        path = os.path.join(folder_path, filename)
        if os.path.exists(path):
            # Read only the header
            df = pd.read_csv(path, nrows=1)
            # Clean column names
            cols = [c.strip().lower().replace(" ", "_") for c in df.columns if "unnamed" not in c.lower()]
            context += f"Table: {filename.replace('.csv', '')}\nColumns: {', '.join(cols)}\n\n"
            
    return context

def run_experiment():
    print(f"--- STARTING EXPERIMENT A: MAIN MIXED DATA ---")
    print(f"Connecting to vLLM at: {VLLM_API_URL}")
    
    # 1. Build Schema Context
    schema_context = get_schema_from_headers(MAIN_DATA_PATH)
    print("Schema Context Built.")

    results = []

    for q in TEST_QUESTIONS:
        print(f"Asking: {q}")
        
        # System Prompt enforces Chain of Thought
        prompt = f"""You are a SQL expert. The database contains data for MULTIPLE companies (Multi-Tenant).
You MUST explain your logic step-by-step before writing the SQL.
Ensure you handle the 'business_id' correctly to avoid data leaks.

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
            "Dataset_Type": "Main_Mixed",
            "Question": q,
            "Generated_Output": answer
        })

    # Save
    pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
    print(f"Done. Results saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    run_experiment()