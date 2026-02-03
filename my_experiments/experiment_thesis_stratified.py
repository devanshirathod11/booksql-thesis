import pandas as pd
import os
import shutil

# ================= CONFIGURATION =================
# 1. Path where your 7 original CSVs are located
SOURCE_DIR = "/home/bisag/Documents/Devanshi_Intern/BookSQL/DATA/BookSQL/Tables/"  # <--- Change this if they are in a subfolder like "./BookSQL_v2/"

# 2. Your Locked-in Industry IDs (From Ground Truth)
TARGET_DOMAINS = {
    'Retail': 16,       # Retail Trade
    'Construction': 6,  # Construction
    'Service': 10       # Information
}

OUTPUT_DIR = "./thesis_datasets"

# ================= AUTOMATIC PROCESSING =================
# 1. Reset Output Directory
if os.path.exists(OUTPUT_DIR):
    shutil.rmtree(OUTPUT_DIR)
os.makedirs(OUTPUT_DIR)

print(f"Scanning '{SOURCE_DIR}' for CSV files...")

# Get list of all CSVs in the folder
all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.csv')]
print(f"Found {len(all_files)} files: {all_files}\n")

print(f"Creating Thesis Datasets in '{OUTPUT_DIR}'...\n")

for filename in all_files:
    # Skip the mapping file if it's there
    if filename == "Industry_Details.csv": 
        continue
        
    print(f"Processing {filename}...")
    
    try:
        # Load and Clean Headers
        file_path = os.path.join(SOURCE_DIR, filename)
        df = pd.read_csv(file_path)
        
        # 1. Remove "Unnamed" columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
        
        # 2. Standardize Column Names (Lowercase, underscores)
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        
        # 3. Check if this table belongs to specific businesses
        # (Most tables have 'business_id', but some might not. 
        # If a table has NO business_id, we assume it's shared/global or skip it).
        
        if 'business_id' in df.columns:
            for domain, bid in TARGET_DOMAINS.items():
                # Create domain folder
                domain_dir = os.path.join(OUTPUT_DIR, domain)
                os.makedirs(domain_dir, exist_ok=True)
                
                # Filter for the specific Business ID
                subset = df[df['business_id'] == bid]
                
                # Only save if data exists for this business
                if not subset.empty:
                    save_path = os.path.join(domain_dir, filename)
                    subset.to_csv(save_path, index=False)
        else:
            print(f"  [Skipping] {filename} (No 'business_id' column found)")

    except Exception as e:
        print(f"  [Error] Could not process {filename}: {e}")

print("\n" + "="*50)
print("✅ SUCCESS! 7-Table Thesis Datasets created.")
print("Folder Structure:")
for d in TARGET_DOMAINS:
    print(f"  - {OUTPUT_DIR}/{d}/")
print("="*50)



