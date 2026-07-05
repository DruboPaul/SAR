import os
import pandas as pd
from sklearn.metrics import confusion_matrix, classification_report

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "Reviewer_Revisions")

# You need to provide a CSV that has the hydroperiod/occurrence data for each point.
# E.g., a column named 'Occurrence_Frequency' (0.0 to 1.0) and 'Field_Truth', 'Prediction'.
# Here we define the path to this hypothetical dataset.
VALIDATION_CSV = os.path.join(BASE_DIR, "data", "Sample_Points", "Validation_Points_With_Occurrence.csv")

def calculate_per_class_accuracy():
    if not os.path.exists(VALIDATION_CSV):
        print(f"Error: {VALIDATION_CSV} not found.")
        print("Please ensure your validation dataset includes the Water Occurrence/Persistence frequency.")
        print("You can extract this from GEE using the JRC Global Surface Water dataset for your points.")
        return

    df = pd.pd.read_csv(VALIDATION_CSV)

    # Classify points based on occurrence frequency F
    def get_water_class(f_value):
        if f_value >= 0.8:
            return 'Permanent'
        elif 0.4 < f_value < 0.8:
            return 'Semi-permanent'
        elif 0.0 < f_value <= 0.4:
            return 'Ephemeral'
        else:
            return 'Non-Water'

    df['Water_Class'] = df['Occurrence_Frequency'].apply(get_water_class)

    # Filter out non-water points for this specific analysis if reviewer only asked for the 3 water classes
    # Or keep them to show a full matrix. Let's do the 3 requested classes.
    classes_of_interest = ['Permanent', 'Semi-permanent', 'Ephemeral']
    df_water_only = df[df['Water_Class'].isin(classes_of_interest)]

    # Calculate confusion matrix for each subclass
    results = []
    
    for cls in classes_of_interest:
        subset = df[df['Water_Class'] == cls]
        if subset.empty:
            continue
            
        y_true = subset['Field_Truth']
        y_pred = subset['Prediction']  # E.g., SAR-based predicted class (0 or 1)
        
        # Calculate True Positives, False Positives, False Negatives
        # Assuming 1 = Water, 0 = Non-Water
        tp = ((y_true == 1) & (y_pred == 1)).sum()
        fp = ((y_true == 0) & (y_pred == 1)).sum()
        fn = ((y_true == 1) & (y_pred == 0)).sum()
        
        # User's Accuracy (Precision)
        user_acc = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        # Producer's Accuracy (Recall)
        prod_acc = tp / (tp + fn) if (tp + fn) > 0 else 0
        
        results.append({
            'Water_Class': cls,
            'Total_Points': len(subset),
            'Users_Accuracy_%': round(user_acc * 100, 2),
            'Producers_Accuracy_%': round(prod_acc * 100, 2)
        })

    results_df = pd.DataFrame(results)
    
    # Save to CSV
    out_file = os.path.join(OUTPUT_DIR, "Per_Class_Accuracy_Results.csv")
    results_df.to_csv(out_file, index=False)
    
    print("\nPer-Class Accuracy Results:")
    print(results_df.to_string(index=False))
    print(f"\nResults saved to: {out_file}")

if __name__ == "__main__":
    calculate_per_class_accuracy()
