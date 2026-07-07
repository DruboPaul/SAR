# Sub-Issue 4: District-Wise Thresholds and Water Area Time-Series

## 1. GMM Calibration and Threshold Lookup Table
To resolve local backscatter variations across Bangladesh's complex geography, we computed spatiotemporally adaptive decision thresholds ($\tau_{dt}$) for all 64 districts and 12 calendar months:
* **Input Data:** Spatially aggregated VV backscatter histograms from **7,891 Sentinel-1 IW-mode VV scenes** processed over 11 years (2015–2025).
* **Fitting Algorithm:** Gaussian Mixture Modeling (GMM) was fitted to each district-month histogram using the EM algorithm. The threshold was defined as the intersection point of the fitted land and water Gaussian distributions.
* **Lookup Table:** This generated a total of **768 district-month thresholds** (plus national baselines) saved in `data/Master_GMM_Thresholds_BD.csv`.

## 2. Water Area Computation and Calibration
* **Areal Quantification:** For each district, year, and month, the number of water pixels was counted using the district's GMM threshold and multiplied by the pixel area ($0.01 \text{ km}^2$ for the 100m grid).
* **Interpolation of Data Gaps:** A few missing months (such as January 2016 early Sentinel-1 coverage gaps) were filled using linear temporal interpolation between adjacent months.
* **National Calibration:** To reconcile scale discrepancies between pixel-wise GEE reductions and histogram-derived areas, a multiplicative calibration ratio of **0.4949** (computed using the mean of January, February, May, July, and September 2015 reference values) was applied uniformly to all computed areas.

## 3. Results File Structure
The final processed time-series is saved in:
* **`district_monthly_water_area_2015_2025.csv`**: Contains the following columns:
  - `year`, `month`, `month_name`: The temporal keys.
  - `district`, `division`: The spatial identifiers.
  - `water_area_km2`: The raw uncalibrated water area.
  - `total_area_km2`: The total geographic area of the district.
  - `water_fraction`: The proportion of the district covered by water.
  - `water_area_calibrated_km2`: The final calibrated water area (used in the manuscript).
  - `season`: Hydrological season category.
* **`national_monthly_water_area_2015_2025.csv`**: The national monthly aggregation.

## 4. Associated Files in this Folder
* **`Master_GMM_Thresholds_BD.csv`**: The master GMM thresholds in dB for each district and month.
* **`GMM_Threshold_Lookup_Table.csv`**: The lookup table format of the GMM thresholds.
* **`district_monthly_water_area_2015_2025.csv`**: The final district-wise monthly water area time-series.
* **`national_monthly_water_area_2015_2025.csv`**: The national monthly water area time-series.
* **`01_batch_gmm_processor.py`**: The python script used to compute GMM thresholds from the histograms.
* **`02_compute_water_area.py`**: The python script used to compute water areas, apply calibration, and fill data gaps.
