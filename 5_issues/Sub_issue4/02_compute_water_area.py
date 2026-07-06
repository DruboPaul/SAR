# -*- coding: utf-8 -*-
"""
Water Area Computation from District Histograms + GMM Thresholds
================================================================

Workflow:
  1. Load Histogram CSV (64 districts x 12 months x 11 years)
  2. Load GMM Threshold CSV (64 districts x 12 months)
  3. Fill 31 missing entries via Linear Temporal Interpolation
  4. Apply threshold -> water pixel count -> water area (km2)
  5. National and Division-level aggregation
  6. Output CSVs for manuscript tables

Gap-filling: Linear temporal interpolation using adjacent months.
  - Jan 2016 missing -> (Dec 2015 + Feb 2016) / 2
  - Sep 2015 missing -> (Aug 2015 + Oct 2015) / 2
  - Nov 2015 missing -> (Oct 2015 + Dec 2015) / 2

Scale: 100m (from GEE export_11yr_histograms.js, line 73)
Pixel Area: 100m x 100m = 10,000 m2 = 0.01 km2
"""

import numpy as np
import pandas as pd
import ast
import os
from datetime import datetime

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST_CSV = os.path.join(BASE_DIR, "data", "GEE_data", "Bangladesh_District_VV_Histograms_2015_2025.csv")
THRESHOLD_CSV = os.path.join(BASE_DIR, "data", "Master_GMM_Thresholds_BD.csv")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "GEE_data", "computed_results")

# --- CONSTANTS ---
PIXEL_SCALE_M = 100
PIXEL_AREA_KM2 = (PIXEL_SCALE_M ** 2) / 1e6  # 0.01 km2

# District -> Division mapping
DISTRICT_TO_DIVISION = {
    'Bagerhat': 'Khulna', 'Bandarban': 'Chittagong', 'Barguna': 'Barisal',
    'Barisal': 'Barisal', 'Bhola': 'Barisal', 'Bogra': 'Rajshahi',
    'Brahamanbaria': 'Chittagong', 'Chandpur': 'Chittagong', 'Chittagong': 'Chittagong',
    'Chuadanga': 'Khulna', 'Comilla': 'Chittagong', "Cox's Bazar": 'Chittagong',
    'Dhaka': 'Dhaka', 'Dinajpur': 'Rangpur', 'Faridpur': 'Dhaka',
    'Feni': 'Chittagong', 'Gaibandha': 'Rangpur', 'Gazipur': 'Dhaka',
    'Gopalganj': 'Dhaka', 'Habiganj': 'Sylhet', 'Jamalpur': 'Dhaka',
    'Jessore': 'Khulna', 'Jhalokati': 'Barisal', 'Jhenaidah': 'Khulna',
    'Joypurhat': 'Rajshahi', 'Khagrachhari': 'Chittagong', 'Khulna': 'Khulna',
    'Kishoreganj': 'Dhaka', 'Kurigram': 'Rangpur', 'Kushtia': 'Khulna',
    'Lakshmipur': 'Chittagong', 'Lalmonirhat': 'Rangpur', 'Madaripur': 'Dhaka',
    'Magura': 'Khulna', 'Manikganj': 'Dhaka', 'Maulvibazar': 'Sylhet',
    'Meherpur': 'Khulna', 'Munshiganj': 'Dhaka', 'Mymensingh': 'Dhaka',
    'Naogaon': 'Rajshahi', 'Narail': 'Khulna', 'Narayanganj': 'Dhaka',
    'Narsingdi': 'Dhaka', 'Natore': 'Rajshahi', 'Nawabganj': 'Rajshahi',
    'Netrakona': 'Dhaka', 'Nilphamari': 'Rangpur', 'Noakhali': 'Chittagong',
    'Pabna': 'Rajshahi', 'Panchagarh': 'Rangpur', 'Patuakhali': 'Barisal',
    'Pirojpur': 'Barisal', 'Rajbari': 'Dhaka', 'Rajshahi': 'Rajshahi',
    'Rangamati': 'Chittagong', 'Rangpur': 'Rangpur', 'Satkhira': 'Khulna',
    'Shariatpur': 'Dhaka', 'Sherpur': 'Dhaka', 'Sirajganj': 'Rajshahi',
    'Sunamganj': 'Sylhet', 'Sylhet': 'Sylhet', 'Tangail': 'Dhaka',
    'Thakurgaon': 'Rangpur',
}

MONTH_NAMES = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}

# 2015 GEE console reference values for calibration
VALIDATION_2015 = {
    'January': 16961.3,
    'February': 21029.3,
    'May': 11670.4,
    'July': 22406.1,
    'September': 20329.6,
}


def safe_parse_list(s):
    """Parse stringified list from CSV."""
    if pd.isna(s) or s == '' or s == '[]':
        return []
    try:
        return ast.literal_eval(s)
    except (ValueError, SyntaxError):
        return []


def compute_water_area(bin_centers, counts, threshold):
    """
    Apply threshold to histogram: sum pixels where VV <= threshold.
    Returns (water_area_km2, total_area_km2).
    """
    bc = np.array(bin_centers, dtype=float)
    ct = np.array(counts, dtype=float)
    if len(bc) == 0 or len(ct) == 0:
        return 0.0, 0.0
    min_len = min(len(bc), len(ct))
    bc, ct = bc[:min_len], ct[:min_len]
    water_px = np.sum(ct[bc <= threshold])
    total_px = np.sum(ct)
    return float(water_px) * PIXEL_AREA_KM2, float(total_px) * PIXEL_AREA_KM2


def get_adjacent_months(year, month):
    """Get (prev_year, prev_month) and (next_year, next_month)."""
    if month == 1:
        prev_y, prev_m = year - 1, 12
    else:
        prev_y, prev_m = year, month - 1
    if month == 12:
        next_y, next_m = year + 1, 1
    else:
        next_y, next_m = year, month + 1
    return (prev_y, prev_m), (next_y, next_m)


def main():
    print("=" * 70)
    print("  WATER AREA COMPUTATION — GMM THRESHOLD + HISTOGRAM")
    print("  With Linear Temporal Interpolation for Missing Data")
    print("  " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 70)

    # --- Step 1: Load Thresholds ---
    print("\n[1/7] Loading GMM thresholds...")
    thresh_df = pd.read_csv(THRESHOLD_CSV)
    threshold_lookup = {}
    national_thresholds = {}
    for _, row in thresh_df.iterrows():
        key = (int(row['Month_Num']), row['Area_Name'])
        threshold_lookup[key] = float(row['GMM_Threshold_dB'])
        if row['Area_Name'] == 'national_mean':
            national_thresholds[int(row['Month_Num'])] = float(row['GMM_Threshold_dB'])
    print("  Loaded %d thresholds" % len(threshold_lookup))

    # --- Step 2: Load Histograms ---
    print("\n[2/7] Loading histogram CSV (57 MB, please wait)...")
    hist_df = pd.read_csv(HIST_CSV)
    hist_df['year'] = hist_df['year'].astype(int)
    hist_df['month'] = hist_df['month'].astype(int)
    print("  Loaded %d rows" % len(hist_df))

    # Identify missing
    empty_mask = hist_df['histogram_counts'].isna() | (hist_df['histogram_counts'] == '[]') | (hist_df['histogram_counts'] == '')
    n_missing = empty_mask.sum()
    print("  Missing histograms: %d / %d (%.2f%%)" % (n_missing, len(hist_df), 100.0 * n_missing / len(hist_df)))

    # --- Step 3: Compute water area for valid entries ---
    print("\n[3/7] Computing water area for all valid entries...")

    # Build lookup from histogram: (year, month, district) -> (water_km2, total_km2)
    area_lookup = {}
    processed = 0
    for idx, row in hist_df.iterrows():
        district = row['district_name']
        month = row['month']
        year = row['year']

        bc = safe_parse_list(row['histogram_counts'])
        bm = safe_parse_list(row['histogram_means'])

        if len(bc) == 0 or len(bm) == 0:
            continue

        threshold = threshold_lookup.get((month, district))
        if threshold is None:
            threshold = national_thresholds.get(month, -12.0)

        w_km2, t_km2 = compute_water_area(bm, bc, threshold)
        area_lookup[(year, month, district)] = (w_km2, t_km2)
        processed += 1

        if processed % 1000 == 0:
            print("  Processed %d / %d..." % (processed, len(hist_df)))

    print("  Computed water area for %d entries" % processed)

    # --- Step 4: Interpolate missing entries ---
    print("\n[4/7] Interpolating %d missing entries..." % n_missing)

    missing_rows = hist_df[empty_mask]
    interpolated = 0

    for _, row in missing_rows.iterrows():
        district = row['district_name']
        year = row['year']
        month = row['month']

        (py, pm), (ny, nm) = get_adjacent_months(year, month)

        prev_data = area_lookup.get((py, pm, district))
        next_data = area_lookup.get((ny, nm, district))

        if prev_data and next_data:
            w_km2 = (prev_data[0] + next_data[0]) / 2.0
            t_km2 = (prev_data[1] + next_data[1]) / 2.0
            method = "avg(%d-%02d + %d-%02d)" % (py, pm, ny, nm)
        elif prev_data:
            w_km2, t_km2 = prev_data
            method = "copy(%d-%02d)" % (py, pm)
        elif next_data:
            w_km2, t_km2 = next_data
            method = "copy(%d-%02d)" % (ny, nm)
        else:
            w_km2, t_km2 = 0.0, 0.0
            method = "no_data"

        area_lookup[(year, month, district)] = (w_km2, t_km2)
        interpolated += 1
        print("  Filled: %s %d-%02d -> %s = %.1f km2" % (district, year, month, method, w_km2))

    print("  Interpolated: %d entries" % interpolated)

    # --- Step 5: Build results dataframe ---
    print("\n[5/7] Building full results table...")

    results = []
    for (year, month, district), (w_km2, t_km2) in area_lookup.items():
        division = DISTRICT_TO_DIVISION.get(district, 'Unknown')
        w_frac = w_km2 / t_km2 if t_km2 > 0 else 0.0
        results.append({
            'year': year,
            'month': month,
            'month_name': MONTH_NAMES.get(month, str(month)),
            'district': district,
            'division': division,
            'water_area_km2': round(w_km2, 2),
            'total_area_km2': round(t_km2, 2),
            'water_fraction': round(w_frac, 6),
        })

    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['year', 'month', 'district']).reset_index(drop=True)

    # National monthly aggregation
    national = results_df.groupby(['year', 'month', 'month_name'])[['water_area_km2', 'total_area_km2']].sum().reset_index()
    national = national.sort_values(['year', 'month'])

    # --- Step 6: Calibration ---
    print("\n[6/7] Calibrating against 2015 GEE reference values...")
    print("  %-12s %-15s %-18s %-8s" % ('Month', 'GEE (250m)', 'Histogram (100m)', 'Ratio'))
    print("  " + "-" * 55)

    ratios = []
    for mname, gee_val in VALIDATION_2015.items():
        mnum = [k for k, v in MONTH_NAMES.items() if v == mname][0]
        row = national[(national['year'] == 2015) & (national['month'] == mnum)]
        if len(row) > 0:
            h_val = row['water_area_km2'].values[0]
            ratio = gee_val / h_val if h_val > 0 else 1.0
            ratios.append(ratio)
            print("  %-12s %-15.1f %-18.1f %-8.4f" % (mname, gee_val, h_val, ratio))

    cal_ratio = float(np.mean(ratios)) if ratios else 1.0
    print("\n  Calibration ratio (mean): %.4f" % cal_ratio)

    # Apply calibration
    national['water_area_calibrated_km2'] = (national['water_area_km2'] * cal_ratio).round(1)
    results_df['water_area_calibrated_km2'] = (results_df['water_area_km2'] * cal_ratio).round(1)

    # Division-level July
    july = results_df[results_df['month'] == 7]
    div_july = july.groupby(['year', 'division'])['water_area_calibrated_km2'].sum().reset_index()
    div_july = div_july.rename(columns={'water_area_calibrated_km2': 'water_area_km2'})
    div_july = div_july.sort_values(['division', 'year'])

    # Seasonal
    def season(m):
        if m in [12, 1, 2]: return 'Dry Winter (Dec-Feb)'
        elif m in [3, 4, 5]: return 'Pre-Monsoon (Mar-May)'
        elif m in [6, 7, 8, 9]: return 'Monsoon (Jun-Sep)'
        else: return 'Post-Monsoon (Oct-Nov)'

    results_df['season'] = results_df['month'].apply(season)
    seasonal = results_df.groupby(['year', 'season'])['water_area_calibrated_km2'].sum().reset_index()
    seasonal = seasonal.rename(columns={'water_area_calibrated_km2': 'total_water_km2'})
    season_months = {'Dry Winter (Dec-Feb)': 3, 'Pre-Monsoon (Mar-May)': 3,
                     'Monsoon (Jun-Sep)': 4, 'Post-Monsoon (Oct-Nov)': 2}
    seasonal['monthly_mean_km2'] = seasonal.apply(
        lambda r: round(r['total_water_km2'] / season_months.get(r['season'], 1), 1), axis=1)

    # Monthly stats across all years (for Table 4)
    monthly_stats = national.groupby(['month', 'month_name'])['water_area_calibrated_km2'].agg(['mean', 'min', 'max', 'std']).reset_index()
    monthly_stats = monthly_stats.rename(columns={'mean': 'mean_km2', 'min': 'min_km2', 'max': 'max_km2', 'std': 'std_km2'})
    monthly_stats = monthly_stats.sort_values('month').round(1)

    # --- Step 7: Save outputs ---
    print("\n[7/7] Saving output files...")
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    files = {
        "district_monthly_water_area_2015_2025.csv": results_df,
        "national_monthly_water_area_2015_2025.csv": national,
        "division_july_water_area_2015_2025.csv": div_july,
        "table4_monthly_water_stats.csv": monthly_stats,
        "table5_seasonal_water_area.csv": seasonal,
    }

    for fname, dataframe in files.items():
        path = os.path.join(OUTPUT_DIR, fname)
        dataframe.to_csv(path, index=False)
        print("  Saved: %s" % path)

    # --- Print summary tables ---
    print("\n" + "=" * 70)
    print("  TABLE 4: MONTHLY WATER AREA STATISTICS (2015-2025)")
    print("=" * 70)
    print("  %-12s %-12s %-12s %-12s %-10s" % ('Month', 'Mean(km2)', 'Min', 'Max', 'Std'))
    print("  " + "-" * 58)
    for _, r in monthly_stats.iterrows():
        print("  %-12s %-12.1f %-12.1f %-12.1f %-10.1f" % (
            r['month_name'], r['mean_km2'], r['min_km2'], r['max_km2'], r['std_km2']))

    print("\n" + "=" * 70)
    print("  NATIONAL MONTHLY WATER AREA BY YEAR (calibrated km2)")
    print("=" * 70)
    piv = national.pivot_table(index='month_name', columns='year', values='water_area_calibrated_km2')
    month_order = [MONTH_NAMES[i] for i in range(1, 13)]
    piv = piv.reindex([m for m in month_order if m in piv.index])
    print(piv.to_string())

    print("\n" + "=" * 70)
    print("  DIVISION JULY WATER AREA BY YEAR (calibrated km2)")
    print("=" * 70)
    piv2 = div_july.pivot_table(index='division', columns='year', values='water_area_km2')
    print(piv2.to_string())

    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print("  Scale: %dm | Pixel area: %.4f km2" % (PIXEL_SCALE_M, PIXEL_AREA_KM2))
    print("  Calibration ratio: %.4f" % cal_ratio)
    print("  Interpolated entries: %d" % interpolated)
    print("  Output: %s" % OUTPUT_DIR)
    print("  DONE!")
    print("=" * 70)


if __name__ == '__main__':
    main()
