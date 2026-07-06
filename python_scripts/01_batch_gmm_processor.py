import os
import sys
import subprocess
import time

# ─── Dependency Check & Auto-Installer ─────────────────────────────────────────
def install_dependencies():
    requirements_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "requirements.txt")
    
    packages = []
    if os.path.exists(requirements_file):
        with open(requirements_file, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (handling versions like pandas>=1.3)
                    package = line.split(">")[0].split("=")[0].split("<")[0].strip()
                    packages.append(package)
    else:
        # Fallback to defaults if requirements.txt is missing
        packages = ["pandas", "numpy", "scikit-learn", "scipy"]

    for package in packages:
        try:
            # Map common package names to import names
            import_name = package.replace("-", "_")
            if package == "scikit-learn": import_name = "sklearn"
            __import__(import_name)
        except ImportError:
            print(f"{package} not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

import pandas as pd
import numpy as np
from sklearn.mixture import GaussianMixture
from scipy.stats import norm
import warnings

warnings.filterwarnings('ignore')

# Start timing
start_time = time.time()

# ─── Configuration ─────────────────────────────────────────────────────────────
# Path to the GEE-exported histogram CSV (User to provide this file)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "data", "GEE_data", "Bangladesh_District_VV_Histograms_2015_2025.csv")
OUTPUT_LOOKUP = os.path.join(BASE_DIR, "data", "GMM_Threshold_Lookup_Table.csv")
OUTPUT_MASTER = os.path.join(BASE_DIR, "data", "Master_GMM_Thresholds_BD.csv")

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

processed_count = 0

def fit_gmm_and_find_threshold(row):
    """
    Fits a 2-component GMM to the histogram data and finds the intersection.
    Input row contains: 'hist' (list of counts), 'bins' (list of centers)
    """
    counts = np.array(row['hist'])
    bins = np.array(row['bins'])
    
    # Filter out empty bins
    mask = counts > 0
    counts = counts[mask]
    bins = bins[mask]
    
    global processed_count
    processed_count += 1
    if processed_count % 500 == 0:
        print(f"  Processed {processed_count}/8448 rows...", flush=True)

    if len(bins) < 5 or counts.sum() < 100:
        return np.nan # Not enough data for a robust fit

    # Downsample if total counts are large to speed up GMM fitting
    total_counts = counts.sum()
    if total_counts > 10000:
        scale_factor = total_counts / 10000.0
        counts = (counts / scale_factor).astype(int)

    # Reconstruct samples
    samples = np.repeat(bins, counts.astype(int))
    
    try:
        gmm = GaussianMixture(n_components=2, covariance_type='full', max_iter=200, random_state=42)
        gmm.fit(samples.reshape(-1, 1))
        
        means = gmm.means_.flatten()
        stds = np.sqrt(gmm.covariances_.flatten())
        weights = gmm.weights_.flatten()
        
        # Sort by mean (water < land)
        idx = np.argsort(means)
        means, stds, weights = means[idx], stds[idx], weights[idx]
        
        # Find intersection
        x_range = np.linspace(bins.min(), bins.max(), 1000)
        pdf_water = weights[0] * norm.pdf(x_range, means[0], stds[0])
        pdf_land = weights[1] * norm.pdf(x_range, means[1], stds[1])
        
        # Intersection search between peaks
        search_mask = (x_range > means[0]) & (x_range < means[1])
        if not any(search_mask):
             return (means[0] * stds[1] + means[1] * stds[0]) / (stds[0] + stds[1])
             
        diff = pdf_water[search_mask] - pdf_land[search_mask]
        sign_changes = np.where(np.diff(np.sign(diff)))[0]
        
        if len(sign_changes) > 0:
            return x_range[search_mask][sign_changes[0]]
        else:
            # Fallback to weighted mean if no clear intersection point found
            return (means[0] * stds[1] + means[1] * stds[0]) / (stds[0] + stds[1])
            
    except Exception:
        return np.nan

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    print(f"Reading {INPUT_CSV}...")
    df = pd.read_csv(INPUT_CSV)
    
    # GEE exports hist as a string like "[10, 20, 30]"
    import ast
    df['hist'] = df['histogram_counts'].apply(ast.literal_eval)
    
    # Assuming bins are fixed from -30 to 5 in 0.2 increments (standard for our script)
    # If the CSV has a 'bins' column, use it; otherwise generate it.
    if 'histogram_means' not in df.columns:
        df['bins'] = [np.linspace(-30, 5, len(h)) for h in df['hist']]
    else:
        df['bins'] = df['histogram_means'].apply(ast.literal_eval)

    print(f"Calculating GMM thresholds for {len(df)} district-months...")
    
    # Apply GMM
    df['threshold'] = df.apply(fit_gmm_and_find_threshold, axis=1)
    
    # Drop rows where GMM failed
    failed = df['threshold'].isna().sum()
    if failed > 0:
        print(f"Warning: GMM failed for {failed} rows (likely insufficient water data).")
    
    # Save the lookup table
    # We group by District and Month to get a clean lookup table
    lookup = df.groupby(['district_name', 'month'])['threshold'].mean().reset_index()
    
    # Interpolate missing months if any
    lookup['threshold'] = lookup.groupby('district_name')['threshold'].transform(lambda x: x.interpolate().bfill().ffill())
    
    lookup.to_csv(OUTPUT_LOOKUP, index=False)
    print(f"Lookup table saved to: {OUTPUT_LOOKUP}")

    # Also save in the Master format expected by compute_water_area_from_histograms.py
    # Format: Month_Num, Month_Name, Area_Name, GMM_Threshold_dB
    master_rows = []
    for _, row in lookup.iterrows():
        master_rows.append({
            'Month_Num': int(row['month']),
            'Month_Name': MONTH_NAMES[int(row['month'])],
            'Area_Name': row['district_name'],
            'GMM_Threshold_dB': round(row['threshold'], 4)
        })

    # Add national mean thresholds
    national_mean = lookup.groupby('month')['threshold'].mean().reset_index()
    for _, row in national_mean.iterrows():
        master_rows.append({
            'Month_Num': int(row['month']),
            'Month_Name': MONTH_NAMES[int(row['month'])],
            'Area_Name': 'national_mean',
            'GMM_Threshold_dB': round(row['threshold'], 4)
        })

    master_df = pd.DataFrame(master_rows)
    master_df = master_df.sort_values(['Month_Num', 'Area_Name']).reset_index(drop=True)
    master_df.to_csv(OUTPUT_MASTER, index=False)
    print(f"Master threshold file saved to: {OUTPUT_MASTER}")
    
    # End timing
    end_time = time.time()
    total_time = end_time - start_time
    print(f"\nTotal Execution Time: {total_time:.2f} seconds ({total_time/60:.2f} minutes)")
    print(f"Average time per threshold: {(total_time/len(df))*1000:.2f} ms")

if __name__ == "__main__":
    main()
