
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST_CSV = os.path.join(BASE_DIR, "data", "GEE_data", "Bangladesh_District_VV_Histograms_2015_2025.csv")
THRESHOLD_CSV = os.path.join(BASE_DIR, "data", "Master_GMM_Thresholds_BD.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "figures", "debug_histograms")

DISTRICTS = ['Sunamganj', 'Sylhet', 'Kurigram', 'Bhola']
MONTHS = [3, 7] # March vs July
YEAR = 2020

def safe_parse_list(s):
    if pd.isna(s) or s == '' or s == '[]': return []
    try: return ast.literal_eval(s)
    except: return []

def plot_histograms():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print("Loading histogram CSV...")
    df = pd.read_csv(HIST_CSV)
    print("Loading threshold CSV...")
    thresh_df = pd.read_csv(THRESHOLD_CSV)
    
    for district in DISTRICTS:
        plt.figure(figsize=(10, 6))
        for m in MONTHS:
            row = df[(df['district_name'] == district) & (df['month'] == m) & (df['year'] == YEAR)]
            if row.empty: 
                print("No data for {} in month {}".format(district, m))
                continue
            
            counts_str = row['histogram_counts'].values[0]
            means_str = row['histogram_means'].values[0]
            
            counts = safe_parse_list(counts_str)
            means = safe_parse_list(means_str)
            
            if not counts: continue
            
            # Get threshold
            t_row = thresh_df[(thresh_df['Month_Num'] == m) & (thresh_df['Area_Name'] == district)]
            threshold = t_row['GMM_Threshold_dB'].values[0] if not t_row.empty else -12.0
            
            mname = 'March' if m == 3 else 'July'
            color = 'blue' if m == 3 else 'red'
            
            # Normalize for comparison
            counts = np.array(counts).astype(float)
            norm_counts = counts / np.max(counts)
            
            plt.plot(means, norm_counts, label="{} (Threshold: {:.2f})".format(mname, threshold), color=color, linewidth=2)
            plt.axvline(x=threshold, color=color, linestyle='--', alpha=0.6)
            
        plt.title("VV Histogram Comparison: {} ({})".format(district, YEAR))
        plt.xlabel("VV Backscatter (dB)")
        plt.ylabel("Normalized Frequency")
        plt.xlim(-30, 0)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        path = os.path.join(OUTPUT_DIR, "{}_seasonal_comp.png".format(district))
        plt.savefig(path)
        plt.close()
        print("Completed plot: {}".format(path))

if __name__ == "__main__":
    plot_histograms()
