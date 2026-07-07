# Sub-Issue 1: 4,310 Validation Points Sampling and Accuracy Assessment

## 1. Ground Truth Sampling Methodology
To strictly quantify the classification accuracy of the proposed ST-GMM framework independent of self-referential benchmarks, a probability-based stratified random sampling design was employed across the 11-year baseline (2015–2025).
* **Sampling Pool selection:** A grid of **500 geographical hubs** was evenly dispersed across the historical permanence classes in Bangladesh to cover varied physiographic and climatic zones.
* **Point Extraction:** From these hubs, a total of **4,310 spatially referenced field observations** were selected representing binary water presence/absence ($W \in \{0, 1\}$).
* **Validation Dates:** The sampling was spread across both dry-season and monsoon-season months to represent the hydrological extremes of the delta.

## 2. Reference Class Post-Stratification
To ensure representative coverage across hydrological extremes, the 4,310 points were post-stratified based on the JRC Global Surface Water Occurrence Layer ($F$). The points were sorted and sliced into four distinct hydroperiod categories:
1. **Permanent water bodies** (JRC occurrence range: 69% – 100%): **700 points** (comprising permanent rivers, deep beels, and perennial lakes).
2. **Semi-permanent water** (JRC occurrence range: 36% – 69%): **700 points** (representing seasonal floodplains, dynamic beels, and agricultural gher zones).
3. **Ephemeral water** (JRC occurrence range: 10% – 36%): **528 points** (representing short-duration monsoon flash floods, ephemeral inundation, and dynamic sandbars).
4. **Non-water** (JRC occurrence range: 0% – 10%): **2,382 points** (representing diverse land covers: urban settlements, permanent agriculture, forests, and dry soils).

**Note:** The class boundaries are determined by index slicing (sorting all 4,310 points by JRC occurrence descending and partitioning at indices 700, 1400, 1928), not by rigid percentage thresholds. This ensures fixed, representative sample sizes in each hydroperiod stratum.

## 3. Field Verification and Cross-Sensor Check
* **On-site verification:** Actual field observations in Bangladesh were conducted using handheld GPS receivers to verify local land cover classes.
* **Optical Cross-Check:** For remote and inaccessible areas, manual/visual validation was performed using high-resolution, cloud-free optical imagery from **Sentinel-2** and **Landsat** sensors corresponding to the exact year and month of the validation point.

## 4. Final Accuracy Assessment Metrics
Based on the final correct metrics calculated by our validation script:

### Class-Wise Metrics
| Water Class | N | True Positives (TP) | False Positives (FP) | False Negatives (FN) | True Negatives (TN) | User's Accuracy (UA %) | Producer's Accuracy (PA %) | Class Accuracy (OA %) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Permanent** | 700 | 435 | 80 | 9 | 176 | 84.47% | 97.97% | 87.29% |
| **Semi-permanent** | 700 | 385 | 61 | 11 | 243 | 86.32% | 97.22% | 89.71% |
| **Ephemeral** | 528 | 240 | 36 | 6 | 246 | 86.96% | 97.56% | 92.05% |
| **Non-water** | 2382 | 806 | 82 | 36 | 1458 | 90.77% | 95.72% | 95.05% |

### Overall Performance & Statistical Baseline Comparison
* **Overall Accuracy (OA)**: **92.55%**
* **Cohen's Kappa ($\kappa$)**: **0.8508**
* **McNemar's Chi-Square ($\chi^2$ vs Otsu)**: **142.7597** (rounds to **142.8**, $p < 0.001$). This confirms that the proposed ST-GMM method significantly outperforms the conventional unsupervised Otsu method.

## 5. Associated Files in this Folder
* **`Supplementary_Table_Validation_Points.csv`**: The complete list of 4,310 validation points with Latitude, Longitude, Month, Year, JRC Occurrence %, Field Truth, and ST-GMM Prediction.
* **`per_class_accuracy.csv`**: The class-wise accuracy metrics summary.
* **`overall_validation_metrics.csv`**: The aggregate overall accuracy and McNemar's test results.
* **`10_calculate_detailed_validation_metrics.py`**: The python script used to compute all accuracy metrics and McNemar's test from the raw points table.
