import pandas as pd

def merge():
    print("Merging results...")
    
    # Load both
    try:
        df_mixed = pd.read_csv("results_main_mixed.csv")
        df_strat = pd.read_csv("results_thesis_stratified_v2.csv")
    except FileNotFoundError:
        print("❌ Error: Run Experiment 1 and 2 first!")
        return

    # Merge on Question and Industry (and Gold_SQL just to be safe)
    # We want columns: Question, Industry, Gold_SQL, Mixed_Generated_SQL, Stratified_Generated_SQL
    
    merged = pd.merge(
        df_mixed[['Industry', 'Question', 'Gold_SQL', 'Mixed_Generated_SQL', 'Mixed_Raw_Response']],
        df_strat[['Industry', 'Question', 'Stratified_Generated_SQL', 'Stratified_Raw_Response']],
        on=['Industry', 'Question'],
        how='inner'
    )
    
    merged.to_csv("experiment_results_final_v1.csv", index=False)
    print(f"✅ Merged {len(merged)} records.")
    print("Ready for Evaluation! File: 'experiment_results_final_v1.csv'")

if __name__ == "__main__":
    merge()