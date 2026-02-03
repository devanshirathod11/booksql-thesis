import pandas as pd
import os
import re
from openai import OpenAI

# ================= CONFIGURATION =================
VLLM_API_URL = "http://192.168.7.176:3504/v1"
MODEL_ID = "./Qwen2_5_VL_7B_Instruct/" 
INPUT_CSV = "evaluation_input.csv"
OUTPUT_CSV = "results_main_mixed.csv"
MAIN_DATA_DIR = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/Tables"  # Where your 7 raw CSVs are located

# LIST OF ALL 7 TABLES (The Full "Swamp")
ALL_FILES = [
    "Master_txn_table.csv", 
    "chart_of_account_OB.csv", 
    "customer_table.csv",
    "vendor_table.csv",          # Crucial for Construction logic
    "employee_table.csv",        # Crucial for Service logic
    "product_service_table.csv", # Crucial for Retail logic
    "payment_method.csv"         # Payment details
]

client = OpenAI(api_key="EMPTY", base_url=VLLM_API_URL)

def get_main_schema():
    """Reads headers from ALL raw files to build the full 'Swamp' context."""
    context = ""
    for f in ALL_FILES:
        file_path = os.path.join(MAIN_DATA_DIR, f)
        if os.path.exists(file_path):
            try:
                # Read only the header row
                df = pd.read_csv(file_path, nrows=1)
                
                # Clean column names
                cols = [c.strip().lower().replace(" ", "_") for c in df.columns if "unnamed" not in c.lower()]
                
                # Add to prompt context
                context += f"Table: {f.replace('.csv', '')}\nColumns: {', '.join(cols)}\n\n"
            except Exception as e:
                print(f"Warning: Could not read {f}: {e}")
        else:
            print(f"Warning: File {f} not found in {MAIN_DATA_DIR}")
            
    return context

def extract_sql(text):
    # Regex to find markdown SQL blocks
    pattern = r"```sql(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    
    # Generic block
    pattern_generic = r"```(.*?)```"
    match_generic = re.search(pattern_generic, text, re.DOTALL)
    if match_generic: return match_generic.group(1).strip()
    
    # Raw start
    if text.strip().upper().startswith("SELECT"): return text.strip()
    
    return text.strip()

def run():
    print("--- STARTING EXPERIMENT 1: MAIN MIXED DATA (FULL SCHEMA) ---")
    
    # Load Questions
    if not os.path.exists(INPUT_CSV):
        print(f"❌ Error: {INPUT_CSV} not found. Run 'create_gold_from_json.py' first.")
        return

    df = pd.read_csv(INPUT_CSV)
    
    # Build the Massive Schema Context once
    schema = get_main_schema()
    print("Schema Context Built (All 7 Tables).")
    
    results = []
    
    for idx, row in df.iterrows():
        q = row['Question']
        print(f"[{idx+1}/{len(df)}] Asking: {q[:50]}...")
        
        # PROMPT: Explicitly warning about Multi-Tenant Data
        prompt = f"""You are a SQL Expert. The database contains data for MANY companies (Multi-Tenant).
Write a valid **SQLite** query.
Schema:
{schema}"""

        try:
            resp = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": q}
                ],
                temperature=0.1, max_tokens=350
            )
            raw = resp.choices[0].message.content
            sql = extract_sql(raw)
        except Exception as e:
            print(f"Error: {e}")
            raw, sql = "ERROR", "ERROR"
            
        results.append({
            "Industry": row['Industry'],
            "Question": q,
            "Gold_SQL": row['Gold_SQL'],
            "Mixed_Raw_Response": raw,
            "Mixed_Generated_SQL": sql
        })
        
    # Save Results
    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Main Mixed Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    run()