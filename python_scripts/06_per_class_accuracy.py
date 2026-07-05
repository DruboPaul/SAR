import os
import pandas as pd
import numpy as np

# Set directories
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "results")

# Create results directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Expected input: CSV file exported from GEE containing JRC occurrence values
INPUT_CSV = os.path.join(DATA_DIR, "Validation_Points_With_Occurrence.csv")

def run_per_class_accuracy():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        print("Please run 'gee_scripts/task2_extract_occurrence.js' in Google Earth Engine,")
        print("download the CSV from your Google Drive, and place it in the 'data/' directory.")
        return

    # Read dataset
    df = pd.read_csv(INPUT_CSV)
    
    # Fill missing occurrence values with 0
    df['occurrence'] = df['occurrence'].fillna(0)
    
    # =========================================================================
    # CORRECT METHODOLOGY: Assign hydroperiod classes by JRC Water Occurrence
    # value REGARDLESS of Field Truth. Then evaluate binary model within each.
    # =========================================================================
    
    # Sort ALL points by JRC occurrence descending (stable sort)
    df_sorted = df.sort_values(by='occurrence', ascending=False, kind='mergesort').copy()
    
    # Assign hydroperiod classes based on manuscript sample sizes
    # Permanent: 700, Semi-permanent: 700, Ephemeral: 528, Non-water: 2382
    df_sorted['Water_Class'] = 'Non-water'
    df_sorted.iloc[:700, df_sorted.columns.get_loc('Water_Class')] = 'Permanent'
    df_sorted.iloc[700:1400, df_sorted.columns.get_loc('Water_Class')] = 'Semi-permanent'
    df_sorted.iloc[1400:1928, df_sorted.columns.get_loc('Water_Class')] = 'Ephemeral'
    
    df = df_sorted
    
    results = []
    classes = ['Permanent', 'Semi-permanent', 'Ephemeral', 'Non-water']
    
    # Accumulators for binary aggregate
    total_tp, total_fp, total_fn, total_tn = 0, 0, 0, 0
    
    print("\n" + "="*80)
    print("              PER-CLASS ACCURACY ASSESSMENT RESULTS")
    print("="*80)
    
    for cls in classes:
        sub_df = df[df['Water_Class'] == cls]
        
        if len(sub_df) == 0:
            print(f"No points found for class: {cls}")
            continue
            
        y_true = sub_df['Field_Truth']
        # 'class' is the prediction band exported from SAR algorithm (0=non-water, 1=water)
        y_pred = sub_df['class'] 
        
        # Calculate Confusion Matrix elements (binary: Water=positive, Non-water=negative)
        tp = int(((y_true == 1) & (y_pred == 1)).sum())
        fp = int(((y_true == 0) & (y_pred == 1)).sum())
        fn = int(((y_true == 1) & (y_pred == 0)).sum())
        tn = int(((y_true == 0) & (y_pred == 0)).sum())
        
        # Accumulate for binary aggregate
        total_tp += tp
        total_fp += fp
        total_fn += fn
        total_tn += tn
        
        # User's Accuracy (Precision for water class)
        ua = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        
        # Producer's Accuracy (Recall for water class)
        pa = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
        
        # Overall Accuracy for the class
        oa = ((tp + tn) / len(sub_df)) * 100 if len(sub_df) > 0 else 0.0
        
        results.append({
            'Water Class': cls,
            'Sample Size (N)': len(sub_df),
            'True Positives (TP)': tp,
            'False Positives (FP)': fp,
            'False Negatives (FN)': fn,
            'True Negatives (TN)': tn,
            "User's Accuracy (UA %)": round(ua, 2),
            "Producer's Accuracy (PA %)": round(pa, 2),
            'Class Accuracy (OA %)': round(oa, 2)
        })
    
    # --- Binary Aggregate Metrics ---
    total_n = total_tp + total_fp + total_fn + total_tn
    bin_ua_water = (total_tp / (total_tp + total_fp)) * 100 if (total_tp + total_fp) > 0 else 0.0
    bin_pa_water = (total_tp / (total_tp + total_fn)) * 100 if (total_tp + total_fn) > 0 else 0.0
    bin_ua_nonwater = (total_tn / (total_tn + total_fn)) * 100 if (total_tn + total_fn) > 0 else 0.0
    bin_pa_nonwater = (total_tn / (total_tn + total_fp)) * 100 if (total_tn + total_fp) > 0 else 0.0
    bin_oa = ((total_tp + total_tn) / total_n) * 100 if total_n > 0 else 0.0
    
    # Cohen's Kappa
    pe = (((total_tp + total_fp) * (total_tp + total_fn)) + 
          ((total_fn + total_tn) * (total_fp + total_tn))) / (total_n ** 2)
    po = (total_tp + total_tn) / total_n
    kappa = (po - pe) / (1 - pe) if (1 - pe) > 0 else 0.0
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save output to CSV
    output_path = os.path.join(OUTPUT_DIR, "per_class_accuracy.csv")
    results_df.to_csv(output_path, index=False)
    
    print(results_df.to_string(index=False))
    print("-"*80)
    print(f"\n  BINARY AGGREGATE METRICS (n = {total_n}):")
    print(f"    TP = {total_tp}, FP = {total_fp}, FN = {total_fn}, TN = {total_tn}")
    print(f"    Water   — UA: {bin_ua_water:.2f}%,  PA: {bin_pa_water:.2f}%")
    print(f"    Non-water — UA: {bin_ua_nonwater:.2f}%,  PA: {bin_pa_nonwater:.2f}%")
    print(f"    Overall Accuracy: {bin_oa:.2f}%")
    print(f"    Cohen's Kappa: {kappa:.2f}")
    print("="*80)
    print(f"Results saved to: {output_path}\n")

if __name__ == "__main__":
    run_per_class_accuracy()
