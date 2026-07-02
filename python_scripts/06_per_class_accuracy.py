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
    
    # Define hydroperiod classes based on JRC Occurrence Frequency (0 to 100%)
    def classify_occurrence(occ):
        if occ >= 80:
            return 'Permanent'
        elif 40 < occ < 80:
            return 'Semi-permanent'
        elif 0 < occ <= 40:
            return 'Ephemeral'
        else:
            return 'Non-Water'
            
    df['Water_Class'] = df['occurrence'].apply(classify_occurrence)
    
    results = []
    classes = ['Permanent', 'Semi-permanent', 'Ephemeral']
    
    print("\n" + "="*60)
    print("           PER-CLASS ACCURACY ASSESSMENT RESULTS")
    print("="*60)
    
    for cls in classes:
        sub_df = df[df['Water_Class'] == cls]
        
        if len(sub_df) == 0:
            print(f"No points found for class: {cls}")
            continue
            
        y_true = sub_df['Field_Truth']
        # class is the prediction band exported from your SAR algorithm (0 = non-water, 1 = water)
        y_pred = sub_df['class'] 
        
        # Calculate Confusion Matrix elements
        tp = ((y_true == 1) & (y_pred == 1)).sum()
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        tn = ((y_true == 0) & (y_pred == 0)).sum()
        
        # User's Accuracy (Precision for water class)
        # UA = TP / (TP + FP) -> percentage of predicted water that is actually water
        ua = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        
        # Producer's Accuracy (Recall/Sensitivity for water class)
        # PA = TP / (TP + FN) -> percentage of actual water correctly identified
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
            'User\'s Accuracy (UA %)': round(ua, 2),
            'Producer\'s Accuracy (PA %)': round(pa, 2),
            'Class Accuracy (OA %)': round(oa, 2)
        })
        
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save output to CSV
    output_path = os.path.join(OUTPUT_DIR, "per_class_accuracy.csv")
    results_df.to_csv(output_path, index=False)
    
    print(results_df.to_string(index=False))
    print("="*60)
    print(f"Results successfully saved to: {output_path}\n")

if __name__ == "__main__":
    run_per_class_accuracy()
