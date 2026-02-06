# import json
# import re
# import uuid

# # ============================================================
# # CONFIGURATION
# # ============================================================

# INPUT_JSONS = {
#     "train": "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/train.json",   # update paths if needed
#     "dev":   "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/val.json",
#     "test":  "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/test.json"
# }

# OUTPUT_GOLD_JSON = "gold_questions_with_kpi.json"
# OUTPUT_REVIEW_JSON = "kpi_manual_review.json"

# # ============================================================
# # KPI HEURISTICS (MINIMAL, DEFENSIBLE)
# # ============================================================

# FLOW_KEYWORDS = [
#     "total", "sum", "spent", "spend", "revenue", "sales",
#     "expense", "expenses", "paid", "received", "how many",
#     "count", "ytd", "year to date", "last year", "this year",
#     "last 12 months", "month to date", "fiscal"
# ]

# STOCK_KEYWORDS = [
#     "balance", "open credit", "outstanding", "inventory",
#     "cash", "assets", "liability", "owed"
# ]

# EVENT_KEYWORDS = [
#     "first", "last", "earliest", "latest", "largest",
#     "smallest", "most recent"
# ]

# RATIO_KEYWORDS = [
#     "rate", "percentage", "ratio", "margin", "growth"
# ]

# # ============================================================
# # KPI CLASSIFIER
# # ==================================================
# print("=" * 60)
# print(f"✔ Auto-labeled questions : {len(gold_data)}")
# print(f"⚠ Needs manual review   : {len(needs_review)}")
# print(f"📄 Output file           : {OUTPUT_GOLD_JSON}")
# print(f"📄 Review file           : {OUTPUT_REVIEW_JSON}")


# <--------- version 2 --------->==========

# def infer_kpi_type(question):
#     q = question.lower()

#     # EVENT has highest priority
#     if any(k in q for k in EVENT_KEYWORDS):
#         return "event"

#     # RATIO
#     if any(k in q for k in RATIO_KEYWORDS):
#         return "ratio"

#     # STOCK
#     if any(k in q for k in STOCK_KEYWORDS):
#         return "stock"

#     # FLOW
#     if any(k in q for k in FLOW_KEYWORDS):
#         return "flow"

#     return "ambiguous"

# # ============================================================
# # MAIN PIPELINE
# # ============================================================

# gold_data = []
# needs_review = []

# qid_counter = 1

# for split, path in INPUT_JSONS.items():
#     with open(path, "r") as f:
#         data = json.load(f)

#     for entry in data:
#         question = entry.get("Query", entry.get("question", "")).strip()
#         gold_sql = entry.get("SQL", entry.get("sql", "")).strip()
#         difficulty = entry.get("Levels", entry.get("level", "")).lower()

#         if not question or not gold_sql:
#             continue

#         kpi_type = infer_kpi_type(question)

#         record = {
#             "question_id": f"Q_{qid_counter:05d}",
#             "split": split,
#             "difficulty": difficulty,
#             "question": question,
#             "gold_sql": gold_sql,
#             "kpi_type": kpi_type
#         }

#         if kpi_type == "ambiguous":
#             needs_review.append(record)
#         else:
#             gold_data.append(record)

#         qid_counter += 1

# # ============================================================
# # WRITE OUTPUTS
# # ============================================================

# with open(OUTPUT_GOLD_JSON, "w") as f:
#     json.dump(gold_data, f, indent=2)

# with open(OUTPUT_REVIEW_JSON, "w") as f:
#     json.dump(needs_review, f, indent=2)

# print("=" * 60)
# print("✅ GOLD JSON CREATED WITH AUTO KPI ANNOTATION")
# print("=" * 60)
# print(f"✔ Auto-labeled questions : {len(gold_data)}")
# print(f"⚠ Needs manual review   : {len(needs_review)}")
# print(f"📄 Output file           : {OUTPUT_GOLD_JSON}")
# print(f"📄 Review file           : {OUTPUT_REVIEW_JSON}")


# <--------- version 2 --------->

import json
import re

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_JSONS = {
    "train": "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/train.json",   # update paths if needed
    "dev":   "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/val.json",
    "test":  "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/BookSQL/test.json"
}

OUTPUT_GOLD_JSON = "gold_questions_with_kpi_v2.json"
OUTPUT_REVIEW_JSON = "kpi_manual_review_v2.json"

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize(text):
    return text.lower().strip()

def has_any(text, keywords):
    return any(k in text for k in keywords)

def sql_has_any(sql, keywords):
    sql = sql.lower()
    return any(k in sql for k in keywords)

# ============================================================
# KPI CLASSIFICATION RULES (ORDER MATTERS)
# ============================================================

LIST_PHRASES = [
    "give me list", "list", "show", "return",
    "did we receive", "which customer", "which customers",
    "what are the customers", "what are my transactions"
]

EVENT_KEYWORDS = [
    "first", "last", "lowest", "highest",
    "cheapest", "most expensive", "earliest", "latest"
]

STOCK_KEYWORDS = [
    "open", "outstanding", "unpaid", "as of"
]

# ============================================================
# KPI INFERENCE
# ============================================================

def infer_kpi_type(question, sql):
    q = normalize(question)
    s = normalize(sql)

    # ---------- RULE 1: LIST ----------
    if (
        has_any(q, LIST_PHRASES)
        or (
            sql_has_any(s, ["select transaction_id", "select customers", "select product_service"])
            and not sql_has_any(s, ["sum(", "count(", "avg(", "min(", "max("])
        )
    ):
        return "list"

    # ---------- RULE 2: EVENT ----------
    if has_any(q, EVENT_KEYWORDS) or sql_has_any(s, ["min(", "max(", "order by", "limit 1"]):
        return "event"

    # ---------- RULE 3: STOCK ----------
    if has_any(q, STOCK_KEYWORDS):
        return "stock"

    # ---------- RULE 4: FLOW ----------
    if sql_has_any(s, ["sum(", "count(", "avg("]):
        return "flow"

    # ---------- FALLBACK ----------
    return "ambiguous"

# ============================================================
# MAIN PIPELINE
# ============================================================

gold_data = []
needs_review = []
qid_counter = 1

for split, path in INPUT_JSONS.items():
    with open(path, "r") as f:
        data = json.load(f)

    for entry in data:
        question = entry.get("Query", entry.get("question", "")).strip()
        gold_sql = entry.get("SQL", entry.get("sql", "")).strip()
        difficulty = entry.get("Levels", entry.get("level", "")).lower()

        if not question or not gold_sql:
            continue

        kpi_type = infer_kpi_type(question, gold_sql)

        record = {
            "question_id": f"Q_{qid_counter:05d}",
            "split": split,
            "difficulty": difficulty,
            "question": question,
            "gold_sql": gold_sql,
            "kpi_type": kpi_type
        }

        if kpi_type == "ambiguous":
            needs_review.append(record)
        else:
            gold_data.append(record)

        qid_counter += 1

# ============================================================
# WRITE OUTPUTS
# ============================================================

with open(OUTPUT_GOLD_JSON, "w") as f:
    json.dump(gold_data, f, indent=2)

with open(OUTPUT_REVIEW_JSON, "w") as f:
    json.dump(needs_review, f, indent=2)

print("=" * 60)
print("✅ KPI AUTO-ANNOTATION (v2) COMPLETE")
print("=" * 60)
print(f"✔ Auto-labeled questions : {len(gold_data)}")
print(f"⚠ Needs manual review   : {len(needs_review)}")
print(f"📄 Gold JSON             : {OUTPUT_GOLD_JSON}")
print(f"📄 Manual review JSON    : {OUTPUT_REVIEW_JSON}")
