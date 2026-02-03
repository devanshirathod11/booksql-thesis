import pandas as pd
import sqlite3
import sqlglot
from sqlglot import exp
import numpy as np
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import os
import Levenshtein

# ================= CONFIGURATION =================
INPUT_CSV = "experiment_results_final_v1.csv"  # The merged file you just created
OUTPUT_CSV = "tfaf_final_scorecard_v1.csv"     # The file for your Thesis
THESIS_DATA_DIR = "./thesis_datasets"       # Needed for DSF execution check

# Account types that CANNOT be summed (Stock variables)
STOCK_COLUMNS = [
    'inventory', 'stock_qty', 'balance', 'amount_due', 
    'open_balance', 'credit_limit', 'rate', 'billing_rate'
]

print("Loading Embedding Model (SDE Metric)...")
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# ================= HELPER: DB CONNECTION =================
def get_db_connection(industry):
    """Loads the specific industry CSVs into in-memory SQLite for DSF check."""
    conn = sqlite3.connect(":memory:")
    ind_path = os.path.join(THESIS_DATA_DIR, industry)
    
    if os.path.exists(ind_path):
        for file in os.listdir(ind_path):
            if file.endswith(".csv"):
                try:
                    df = pd.read_csv(os.path.join(ind_path, file))
                    # Clean columns for SQL execution
                    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
                    df.to_sql(file.replace(".csv", ""), conn, index=False)
                except:
                    pass
    return conn

# ================= METRIC 1: DSF (Row Set Intersection) =================
def calculate_DSF(gold_sql, pred_sql, db_conn):
    try:
        # Transformation: Attempt to strip Aggregations to check Logic Scope
        # Simple heuristic: execute as is, check returned row similarity
        cur = db_conn.cursor()
        
        # Exec Gold
        try:
            cur.execute(gold_sql)
            gold_rows = set(cur.fetchall())
        except:
            return 0.0 # Gold failed? Should not happen if Gold is valid.
        
        # Exec Pred
        try:
            cur.execute(pred_sql)
            pred_rows = set(cur.fetchall())
        except:
            return 0.0 # Syntax error in prediction
        
        if len(gold_rows) == 0: return 0.0
        
        # Jaccard
        intersection = len(gold_rows.intersection(pred_rows))
        union = len(gold_rows.union(pred_rows))
        
        return intersection / union if union > 0 else 0.0
    except:
        return 0.0

# ================= METRIC 2: SDE (Schema Distance) =================
def calculate_sde(gold_sql, pred_sql):
    try:
        gold_cols = set([c.name for c in sqlglot.parse_one(gold_sql).find_all(exp.Column)])
        pred_cols = set([c.name for c in sqlglot.parse_one(pred_sql).find_all(exp.Column)])
        
        errors = pred_cols - gold_cols
        if not errors: return 1.0 
        
        # If model used columns not in Gold, how "far" are they?
        gold_vecs = embed_model.encode(list(gold_cols)) if gold_cols else np.zeros((1, 384))
        scores = []
        for err in errors:
            err_vec = embed_model.encode([err])
            if len(gold_cols) > 0:
                sims = cosine_similarity(err_vec, gold_vecs)
                scores.append(np.max(sims))
            else:
                scores.append(0.0)
        return np.mean(scores)
    except:
        return 0.0

# ================= METRIC 3: SLED (Structure) =================
def calculate_SLED(gold_sql, pred_sql):
    try:
        # Use Levenshtein on standardized string as AST proxy
        clean_gold = re.sub(r'\s+', ' ', gold_sql.strip().lower())
        clean_pred = re.sub(r'\s+', ' ', pred_sql.strip().lower())
        
        dist = Levenshtein.distance(clean_gold, clean_pred)
        max_len = max(len(clean_gold), len(clean_pred))
        return 1 - (dist / max_len) if max_len > 0 else 0.0
    except:
        return 0.0

# ================= METRIC 4: TGP (Time) =================
def calculate_tgp(gold_sql, pred_sql):
    # Check for date patterns YYYY-MM-DD
    date_pattern = r"(\d{4}-\d{2}-\d{2})"
    gold_dates = set(re.findall(date_pattern, gold_sql))
    pred_dates = set(re.findall(date_pattern, pred_sql))
    
    if not gold_dates: return 1.0 # Question didn't involve time
    if not pred_dates: return 0.0 # Missed the time component
    
    # Jaccard of dates
    return len(gold_dates.intersection(pred_dates)) / len(gold_dates.union(pred_dates))

# ================= METRIC 5: ASV (Accounting Rules) =================
def calculate_asv(pred_sql):
    try:
        parsed = sqlglot.parse_one(pred_sql)
        aggs = parsed.find_all(exp.Sum)
        for agg in aggs:
            col = agg.find(exp.Column)
            if col and col.name.lower() in STOCK_COLUMNS:
                return 0.0 # Violation
        return 1.0
    except:
        return 0.0

# ================= MAIN LOOP =================
def run_evaluation():
    print(f"Loading Results from {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    
    score_data = []
    
    # Process by Industry to optimize DB loading
    for industry, group in df.groupby("Industry"):
        print(f"Scoring Industry: {industry}...")
        conn = get_db_connection(industry)
        
        for idx, row in group.iterrows():
            gold = row['Gold_SQL']
            
            # --- Score Mixed (Baseline) ---
            mix_sql = str(row['Mixed_Generated_SQL'])
            mix_scores = {
                "Mixed_DSF": calculate_DSF(gold, mix_sql, conn),
                "Mixed_SDE": calculate_sde(gold, mix_sql),
                "Mixed_SLED": calculate_SLED(gold, mix_sql),
                "Mixed_TGP": calculate_tgp(gold, mix_sql),
                "Mixed_ASV": calculate_asv(mix_sql)
            }
            
            # --- Score Stratified (Thesis) ---
            strat_sql = str(row['Stratified_Generated_SQL'])
            strat_scores = {
                "Strat_DSF": calculate_DSF(gold, strat_sql, conn),
                "Strat_SDE": calculate_sde(gold, strat_sql),
                "Strat_SLED": calculate_SLED(gold, strat_sql),
                "Strat_TGP": calculate_tgp(gold, strat_sql),
                "Strat_ASV": calculate_asv(strat_sql)
            }
            
            # Combine
            entry = {
                "Industry": industry,
                "Question": row['Question'],
                **mix_scores,
                **strat_scores
            }
            score_data.append(entry)
        
        conn.close()

    # Save
    scores_df = pd.DataFrame(score_data)
    scores_df.to_csv(OUTPUT_CSV, index=False)
    
    print("\n" + "="*60)
    print("FINAL THESIS SCORECARD GENERATED")
    print(f"File: {OUTPUT_CSV}")
    print("="*60)
    
    # Calculate Averages for "Results" Chapter
    print("\n--- AVERAGE SCORES (The Gap Analysis) ---")
    summary = scores_df[[
        'Mixed_DSF', 'Strat_DSF', 
        'Mixed_SDE', 'Strat_SDE', 
        'Mixed_ASV', 'Strat_ASV'
    ]].mean()
    print(summary)

if __name__ == "__main__":
    run_evaluation()