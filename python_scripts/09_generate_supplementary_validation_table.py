import os
import pandas as pd

def generate_supplementary_table():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    latlon_path = os.path.join(BASE_DIR, "data", "GEE_Upload_Ready_LatLon.csv")
    occ_path = os.path.join(BASE_DIR, "data", "Validation_Points_With_Occurrence.csv")
    output_path = os.path.join(BASE_DIR, "results", "Supplementary_Table_Validation_Points.csv")

    if not os.path.exists(latlon_path) or not os.path.exists(occ_path):
        print("Error: Required input validation CSVs not found in data/.")
        return

    # Load datasets
    df_latlon = pd.read_csv(latlon_path)
    df_occ = pd.read_csv(occ_path)

    # Sort both datasets to align them row-by-row
    sort_cols = ['Month', 'Field_Truth', 'class']
    
    df_latlon_sorted = df_latlon.sort_values(by=sort_cols).reset_index(drop=True)
    df_occ_sorted = df_occ.sort_values(by=sort_cols).reset_index(drop=True)

    # Verify that the sorted combination columns match exactly
    mismatches = (df_latlon_sorted[sort_cols] != df_occ_sorted[sort_cols]).any(axis=1).sum()
    if mismatches > 0:
        print(f"Error: Alignment failed. {mismatches} rows mismatch on key columns after sorting.")
        return

    # Create merged DataFrame
    df_merged = df_occ_sorted.copy()
    df_merged['Longitude'] = df_latlon_sorted['longitude']
    df_merged['Latitude'] = df_latlon_sorted['latitude']

    # Rename columns for presentation
    df_merged = df_merged.rename(columns={
        'Month': 'Month',
        'Year': 'Year',
        'Field_Truth': 'Field_Truth_Water_Binary',
        'class': 'ST_GMM_Predicted_Water_Binary',
        'occurrence': 'JRC_GSW_Occurrence_Frequency_Percent'
    })

    # Reorder columns
    col_order = [
        'Latitude', 'Longitude', 'Month', 'Year', 
        'JRC_GSW_Occurrence_Frequency_Percent', 
        'Field_Truth_Water_Binary', 'ST_GMM_Predicted_Water_Binary'
    ]
    df_merged = df_merged[col_order]

    # Save to CSV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_merged.to_csv(output_path, index=False)
    print(f"Supplementary Table generated and saved to: {output_path}")
    print(f"Total rows: {len(df_merged)}")

if __name__ == "__main__":
    generate_supplementary_table()
