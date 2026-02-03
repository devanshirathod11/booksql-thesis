import pandas as pd
import os
import re
from openai import OpenAI

# ================= CONFIGURATION =================
VLLM_API_URL = "http://192.168.7.176:3504/v1"
MODEL_ID = "./Qwen2_5_VL_7B_Instruct/"
INPUT_CSV = "evaluation_input.csv"
OUTPUT_CSV = "results_thesis_stratified_v2.csv"
THESIS_DIR = "/home/bisag/Documents/Devanshi_Intern/BookSQL/thesis_datasets"

client = OpenAI(api_key="EMPTY", base_url=VLLM_API_URL)

def get_stratified_schema(industry):
    """Reads headers from the specific industry folder."""
    path = os.path.join(THESIS_DIR, industry)
    if not os.path.exists(path): return ""
    
    context = ""
    for f in os.listdir(path):
        if f.endswith(".csv"):
            df = pd.read_csv(os.path.join(path, f), nrows=1)
            cols = [c.strip().lower().replace(" ", "_") for c in df.columns if "unnamed" not in c.lower()]
            context += f"Table: {f.replace('.csv', '')}\nColumns: {', '.join(cols)}\n\n"
    return context

def extract_sql(text):
    pattern = r"```sql(.*?)```"
    match = re.search(pattern, text, re.DOTALL)
    if match: return match.group(1).strip()
    if text.strip().upper().startswith("SELECT"): return text.strip()
    return text.strip()

def run():
    print("--- STARTING EXPERIMENT 2: STRATIFIED THESIS DATA ---")
    df = pd.read_csv(INPUT_CSV)
    
    results = []
    
    for idx, row in df.iterrows():
        q = row['Question']
        industry = row['Industry']
        print(f"[{idx+1}/{len(df)}] Industry: {industry} | Asking: {q[:50]}...")
        
        schema = get_stratified_schema(industry)
        
        prompt = f"""You are a Financial SQL Expert for a {industry} company.
The database contains data ONLY for this company.
Think step-by-step about Accounting Rules. Write a valid **SQLite** query.
Schema:
{schema}"""

        try:
            resp = client.chat.completions.create(
                model=MODEL_ID,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": q}
                ],
                temperature=0.1, max_tokens=300
            )
            raw = resp.choices[0].message.content
            sql = extract_sql(raw)
        except Exception as e:
            print(f"Error: {e}")
            raw, sql = "ERROR", "ERROR"
            
        results.append({
            "Industry": industry,
            "Question": q,
            "Gold_SQL": row['Gold_SQL'],
            "Stratified_Raw_Response": raw,
            "Stratified_Generated_SQL": sql
        })
        
    pd.DataFrame(results).to_csv(OUTPUT_CSV, index=False)
    print(f"✅ Stratified Results saved to {OUTPUT_CSV}")

if __name__ == "__main__":
    run()