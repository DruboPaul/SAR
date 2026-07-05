import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
from sklearn.mixture import GaussianMixture
import seaborn as sns

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

# Set working directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, "data", "GEE_data", "Bangladesh_District_VV_Histograms_2015_2025.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "Reviewer_Revisions")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def perform_aic_bic_test():
    print(f"Loading data from {INPUT_CSV}...")
    try:
        df = pd.read_csv(INPUT_CSV)
    except FileNotFoundError:
        print(f"Error: Could not find {INPUT_CSV}. Please ensure it exists.")
        return

    # Parse histogram data
    df['histogram_counts'] = df['histogram_counts'].apply(ast.literal_eval)
    
    if 'histogram_means' in df.columns:
         df['histogram_means'] = df['histogram_means'].apply(ast.literal_eval)
    else:
         # Fallback bin generation if not present
         df['histogram_means'] = [np.linspace(-30, 5, len(h)) for h in df['histogram_counts']]

    # Select a few diverse samples to represent different settings
    # E.g., Sunamganj (Haor/Deep water), Dhaka (Urban), Bhola (Coastal)
    sample_districts = ['Sunamganj', 'Dhaka', 'Bhola']
    # Select month 7 (July - monsoon) or 2 (Feb - dry)
    
    results = []
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    for idx, dist in enumerate(sample_districts):
        # Filter for district and a specific month (e.g., August = 8 or July = 7)
        subset = df[(df['district_name'] == dist) & (df['month'] == 8)]
        if subset.empty:
            # Fallback to the first available row for this district
            subset = df[df['district_name'] == dist]
            
        if subset.empty:
            print(f"Warning: No data found for {dist}. Skipping.")
            continue
            
        row = subset.iloc[0]
        month = row['month']
        counts = np.array(row['histogram_counts'])
        bins = np.array(row['histogram_means'])
        
        # Reconstruct 1D samples from histogram
        mask = counts > 0
        counts = counts[mask]
        bins = bins[mask]
        
        if len(bins) < 5 or counts.sum() < 100:
            print(f"Skipping {dist} due to insufficient data.")
            continue
            
        # Reconstruct samples (scale down counts to avoid memory issues if counts are huge)
        # Using a scaling factor so we process ~100k points max per district
        total_counts = counts.sum()
        scale_factor = max(1, total_counts // 100000)
        scaled_counts = (counts / scale_factor).astype(int)
        
        samples = np.repeat(bins, scaled_counts).reshape(-1, 1)
        
        aic_scores = []
        bic_scores = []
        n_components_range = [2, 3, 4, 5]
        
        print(f"Fitting GMMs for {dist} (Month: {month})...")
        for n in n_components_range:
            gmm = GaussianMixture(n_components=n, covariance_type='full', max_iter=200, random_state=42)
            gmm.fit(samples)
            aic_scores.append(gmm.aic(samples))
            bic_scores.append(gmm.bic(samples))
            
            # Store results
            results.append({
                'District': dist,
                'Components': n,
                'AIC': gmm.aic(samples),
                'BIC': gmm.bic(samples)
            })
            
        # Plotting
        ax = axes[idx]
        ax.plot(n_components_range, aic_scores, marker='o', label='AIC')
        ax.plot(n_components_range, bic_scores, marker='s', label='BIC')
        ax.set_title(f"{dist} (Mixed Landscape)\nAIC/BIC vs Components")
        ax.set_xlabel("Number of GMM Components")
        ax.set_ylabel("Information Criterion Score")
        ax.set_xticks(n_components_range)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

    plt.tight_layout()
    plot_path = os.path.join(OUTPUT_DIR, "GMM_AIC_BIC_Test_Plot.png")
    plt.savefig(plot_path, dpi=300)
    print(f"Plot saved to: {plot_path}")
    
    # Save table
    results_df = pd.DataFrame(results)
    table_path = os.path.join(OUTPUT_DIR, "GMM_AIC_BIC_Scores.csv")
    results_df.to_csv(table_path, index=False)
    print(f"Results table saved to: {table_path}")
    
    # Display the table
    print("\nAIC / BIC Scores Summary:")
    print(results_df)

if __name__ == "__main__":
    perform_aic_bic_test()
