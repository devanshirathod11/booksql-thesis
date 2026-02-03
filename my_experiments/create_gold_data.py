# import json
# import pandas as pd
# import re

# # ================= CONFIGURATION =================
# INPUT_JSON = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/val.json"  # Path to your BookSQL dev file
# OUTPUT_CSV = "evaluation_input.csv"
# MAX_QUESTIONS_PER_IND = 15  # Limit rows per industry for thesis manageability

# # Keywords to map generic questions to your Specific Industries
# DOMAIN_KEYWORDS = {
#     "Retail": [
#         "sales", "revenue", "product", "goods", "shipping", "refund", 
#         "customer", "income", "sold", "gross profit"
#     ],
#     "Construction": [
#         "job", "project", "material", "subcontractor", "expense", 
#         "cost", "payable", "vendor", "bill", "invoice"
#     ],
#     "Service": [
#         "service", "consulting", "fee", "billable", "hour", 
#         "rate", "client", "professional", "salary", "employee"
#     ]
# }

# # ================= PROCESSING LOGIC =================

# def clean_sql(sql_text):
#     """Normalizes SQL (removes newlines, extra spaces)."""
#     if not sql_text: return ""
#     return re.sub(r'\s+', ' ', sql_text).strip()

# def categorize_query(query_text):
#     """Decides which Industry this question belongs to based on keywords."""
#     q_lower = query_text.lower()
    
#     # Priority Check: Check specific keywords
#     for industry, keywords in DOMAIN_KEYWORDS.items():
#         for k in keywords:
#             # We use word boundaries \b to avoid partial matches
#             if re.search(r'\b' + re.escape(k) + r'\b', q_lower):
#                 return industry
    
#     return "Generic" # Fallback if no specific keywords found

# def main():
#     print(f"Loading {INPUT_JSON}...")
#     try:
#         with open(INPUT_JSON, 'r') as f:
#             data = json.load(f)
#     except FileNotFoundError:
#         print("❌ Error: dev.json not found. Please paste it in this folder.")
#         return

#     print(f"Found {len(data)} total queries. Filtering for Thesis Domains...")

#     dataset = []
#     counters = {"Retail": 0, "Construction": 0, "Service": 0}

#     for entry in data:
#         question = entry.get('Query', '')
#         gold_sql = entry.get('SQL', '')
        
#         if not question or not gold_sql:
#             continue

#         # Determine Industry
#         industry = categorize_query(question)
        
#         # Only add if it matches one of our 3 Thesis Industries
#         if industry in counters:
#             if counters[industry] < MAX_QUESTIONS_PER_IND:
#                 dataset.append({
#                     "Industry": industry,
#                     "Question": question,
#                     "Gold_SQL": clean_sql(gold_sql),
#                     "Generated_SQL": "" # Placeholder for next step
#                 })
#                 counters[industry] += 1

#     # Convert to DataFrame
#     df = pd.DataFrame(dataset)
    
#     # Sort for better readability
#     df = df.sort_values(by="Industry")
    
#     # Save
#     df.to_csv(OUTPUT_CSV, index=False)
    
#     print("\n" + "="*50)
#     print("✅ GOLD STANDARD DATASET CREATED")
#     print("="*50)
#     print(df['Industry'].value_counts())
#     print(f"\nSaved to: {OUTPUT_CSV}")
#     print("You can now run 'run_thesis_experiment.py' using this file.")

# if __name__ == "__main__":
#     main()


import json
import pandas as pd
import re

# ================= CONFIGURATION =================
# Using your specific path
INPUT_JSON = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/val.json" 
OUTPUT_CSV = "evaluation_input.csv"
MAX_QUESTIONS_PER_IND = 15 

DOMAIN_KEYWORDS = {
    "Retail": ["sales", "revenue", "product", "goods", "shipping", "refund", "customer", "income", "sold"],
    "Construction": ["job", "project", "material", "subcontractor", "expense", "cost", "payable", "vendor", "bill"],
    "Service": ["service", "consulting", "fee", "billable", "hour", "rate", "client", "professional", "salary"]
}

# ================= SCHEMA FIXER (CRITICAL) =================

def fix_gold_sql(sql_text):
    """
    Adjusts the Gold SQL from the benchmark to match your specific CSV filenames.
    This ensures the DSF metric doesn't fail due to simple filename mismatches.
    """
    if not sql_text: return ""
    
    # 1. Fix Table Names: benchmark uses 'chart_of_accounts', your file is 'chart_of_account_OB'
    sql_text = sql_text.replace("chart_of_accounts", "chart_of_account_OB")
    
    # 2. Fix potential column naming issues (Standardize to lowercase)
    # BookSQL sometimes uses CamelCase; your CSV cleaning script used lowercase_underscores.
    sql_text = sql_text.lower()
    
    # 3. Clean whitespace
    sql_text = re.sub(r'\s+', ' ', sql_text).strip()
    
    return sql_text

# ================= PROCESSING LOGIC =================

def categorize_query(query_text):
    q_lower = query_text.lower()
    for industry, keywords in DOMAIN_KEYWORDS.items():
        for k in keywords:
            if re.search(r'\b' + re.escape(k) + r'\b', q_lower):
                return industry
    return "Generic"

def main():
    print(f"Loading {INPUT_JSON}...")
    try:
        with open(INPUT_JSON, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File not found at {INPUT_JSON}")
        return

    dataset = []
    counters = {"Retail": 0, "Construction": 0, "Service": 0}

    for entry in data:
        # Use .get() to handle different JSON keys if they vary
        question = entry.get('Query', entry.get('question', ''))
        raw_gold_sql = entry.get('SQL', entry.get('sql', ''))
        
        if not question or not raw_gold_sql:
            continue

        industry = categorize_query(question)
        
        if industry in counters and counters[industry] < MAX_QUESTIONS_PER_IND:
            # APPLY THE FIX HERE
            fixed_sql = fix_gold_sql(raw_gold_sql)
            
            dataset.append({
                "Industry": industry,
                "Question": question,
                "Gold_SQL": fixed_sql,
                "Generated_SQL": "" 
            })
            counters[industry] += 1

    df = pd.DataFrame(dataset)
    df = df.sort_values(by="Industry")
    df.to_csv(OUTPUT_CSV, index=False)
    
    print("\n" + "="*50)
    print("✅ GOLD STANDARD DATASET CREATED WITH SCHEMA FIXES")
    print("="*50)
    print(df['Industry'].value_counts())
    print(f"Example Fix: chart_of_accounts -> chart_of_account_OB")

if __name__ == "__main__":
    main()