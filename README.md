# HydroSAR-BD: Replication and Reviewer Revision Repository

This repository contains the clean, production-ready code, datasets, and scripts to reproduce the core results and address the reviewer comments for the **HydroSAR-BD** manuscript (a dynamic GMM-based surface water mapping framework using Sentinel-1 SAR and Sentinel-2 optical data).

---

## 📁 Repository Structure

```text
├── README.md                           # Main replication guide (this file)
├── HydroSAR_Replication_Notebook.ipynb  # Unified replication notebook (Jupyter/Colab)
├── data/                               # Data folder (contains validation points & rasters)
│   ├── Final_Binary_Field_Validation_2025.csv      # 4,310 validation points
│   ├── Bangladesh_District_VV_Histograms_2015_2025.csv # District backscatter histograms
│   └── Task1_Rasters/                  # Place exported GeoTIFFs here for Task 1
├── gee_scripts/                        # JavaScript files to copy-paste into GEE Editor
│   ├── task1_export_5panels.js         # Exports 5 scenarios for comparative map
│   └── task2_extract_occurrence.js     # Extracts JRC occurrence frequency for points
└── python_scripts/                     # Python scripts for local execution
    ├── task1_plot_5panels.py           # Compiles and plots the 5-panel map
    ├── task2_per_class_accuracy.py     # Calculates per-class validation accuracy
    └── task3_gmm_aic_bic.py            # Performs GMM component information tests
```

---

## 🛠️ Step-by-Step Replication Guide

### Task 1: 5-Panel Comparative Visual Map
This task visualizes the performance of 5 different water mapping methods over Gazipur District, Bangladesh.
1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Copy and paste the code from `gee_scripts/task1_export_5panels.js` and click **Run**.
3. In the **Tasks** tab (right panel), click **Run** for all 5 tasks to export the GeoTIFFs to your Google Drive.
4. Download the 5 exported `.tif` files and place them in the `data/Task1_Rasters/` directory.
5. Run the plotting script locally:
   ```bash
   python python_scripts/task1_plot_5panels.py
   ```
   The final high-resolution figure will be saved in `results/Figure_5Panel_Comparative_Map.png`.

---

### Task 2: Per-Class Accuracy Assessment
This task calculates the User's and Producer's Accuracy across three classes: **Permanent**, **Semi-permanent**, and **Ephemeral** water, using 4,310 validated ground-truth points.
1. Upload `data/Final_Binary_Field_Validation_2025.csv` as an Asset in your GEE account.
2. Paste and run `gee_scripts/task2_extract_occurrence.js` in GEE. It will sample the JRC Global Surface Water Occurrence dataset at the validation points.
3. Export the resulting table and download it as `Validation_Points_With_Occurrence.csv`. Place it inside the `data/` folder.
4. Run the Python accuracy script:
   ```bash
   python python_scripts/task2_per_class_accuracy.py
   ```
   The results table will be printed on screen and saved under `results/per_class_accuracy.csv`.

---

### Task 3: GMM Component Justification (AIC/BIC Test)
This task fits 2, 3, 4, and 5-component GMMs on Sentinel-1 backscatter values to statistically prove that a 2-component model is optimal and avoids overfitting.
1. Ensure `data/Bangladesh_District_VV_Histograms_2015_2025.csv` is present.
2. Run the script:
   ```bash
   python python_scripts/task3_gmm_aic_bic.py
   ```
   This will output the AIC and BIC scores for Sunamganj, Dhaka, and Bhola districts, and generate the diagnostic plot `results/GMM_AIC_BIC_Test_Plot.png`.

---

## 📓 Jupyter Notebook (Google Colab)
For a single, unified execution environment:
* Open `HydroSAR_Replication_Notebook.ipynb` in Jupyter Notebook, JupyterLab, or upload it to **Google Colab**.
* Ensure the required files are present in the `data/` directory.
* Run the cells sequentially to reproduce the figures and tables in a single step.
