import pandas as pd
import json
import os

# ============================================================
# CONFIGURATION
# ============================================================

DATA_DIR = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/Tables"  # Update this path if your CSVs are elsewhere
OUTPUT_SCHEMA = "schema.json"

TABLE_FILES = {
    "chart_of_account_OB": "chart_of_account_OB.csv",
    "master_txn_table": "Master_txn_table.csv",
    "customer_table": "customer_table.csv",
    "vendor_table": "vendor_table.csv",
    "employee_table": "employee_table.csv",
    "payment_method": "payment_method.csv",
    "product_service_table": "product_service_table.csv"
}

# ============================================================
# TYPE INFERENCE
# ============================================================

def infer_type(series):
    dtype = series.dtype

    if pd.api.types.is_integer_dtype(dtype):
        return "integer"
    if pd.api.types.is_float_dtype(dtype):
        return "number"
    if pd.api.types.is_bool_dtype(dtype):
        return "boolean"
    if pd.api.types.is_datetime64_any_dtype(dtype):
        return "date"

    # Try parsing dates inside object columns
    if pd.api.types.is_object_dtype(dtype):
        sample = series.dropna().astype(str).head(20)
        try:
            pd.to_datetime(sample, errors="raise")
            return "date"
        except:
            return "string"

    return "string"

# ============================================================
# SCHEMA GENERATION
# ============================================================

schema = {
    "database": "BookSQL",
    "description": "Data-driven canonical schema inferred from original mixed CSVs. Used identically for mixed and stratified experiments.",
    "tables": [],
    "relationships": []  # filled manually later (intentionally)
}

for table_name, file_name in TABLE_FILES.items():
    path = os.path.join(DATA_DIR, file_name)
    df = pd.read_csv(path)

    # clean unnamed columns if any slipped in
    df = df.loc[:, ~df.columns.str.contains("^unnamed", case=False)]

    columns = []
    for col in df.columns:
        col_type = infer_type(df[col])
        columns.append({
            "name": col,
            "type": col_type
        })

    schema["tables"].append({
        "name": table_name,
        "description": f"Auto-inferred schema for {table_name}",
        "columns": columns
    })

# ============================================================
# WRITE SCHEMA
# ============================================================

with open(OUTPUT_SCHEMA, "w") as f:
    json.dump(schema, f, indent=2)

print("✅ schema.json generated from CSVs")
print(f"📄 Output: {OUTPUT_SCHEMA}")
