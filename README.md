# HydroSAR-BD: Spatiotemporal GMM for Dynamic Surface Water Mapping

This repository contains the complete, production-ready codebase for **HydroSAR-BD**, a framework for dynamic surface water mapping across Bangladesh using Sentinel-1 SAR and Sentinel-2 optical data. It includes both the core analysis scripts for the original manuscript and the supplementary validation scripts for comprehensive evaluation.

---

## 📁 Repository Structure

### 1. `gee_scripts/` (Google Earth Engine JavaScript)
*   **`01_export_11yr_histograms.js`**: Exports massive multi-year SAR backscatter histograms.
*   **`02a_export_february_thresholds.js` / `02b_export_july_thresholds.js`**: Extracts distinct dry and wet season thresholds.
*   **`03_export_comparative_models.js`**: Generates a 5-panel comparative map of Random Forest, Otsu, ST-GMM, and NDWI.
*   **`04_extract_jrc_occurrence.js`**: Extracts long-term JRC surface water occurrence frequencies.
*   **`10_earth_engine_app.js`**: The source code for the interactive HydroSAR-BD Web Application.

### 2. `python_scripts/` (Local Python Analysis & Plotting)
*   **`01_batch_gmm_processor.py`**: The core Spatiotemporal Gaussian Mixture Model (ST-GMM) algorithm.
*   **`02_compute_water_area.py`**: Computes areal water statistics across divisions/districts.
*   **`03_generate_core_figures.py`**: Generates publication-ready figures for the manuscript.
*   **`04_generate_flowchart.py`**: Creates the programmatic methodology flowchart.
*   **`05_plot_comparative_map.py`**: Plots the high-resolution 5-panel comparative model map.
*   **`06_per_class_accuracy.py`**: Evaluates User's and Producer's Accuracies across Permanent, Semi-permanent, and Ephemeral hydroperiods.
*   **`07_gmm_information_criteria.py`**: Calculates AIC/BIC goodness-of-fit diagnostics for component justification.

### 3. `data/` and `results/`
*   Contains the validated ground-truth datasets, extracted occurrence frequencies, histogram inputs, and the resulting high-resolution output figures and accuracy tables.

---

## 🛠️ Replication Guide

### A. Core GMM Processing
To run the primary ST-GMM algorithm on the SAR backscatter histograms:
```bash
python python_scripts/01_batch_gmm_processor.py
```

### B. Accuracy Assessment & Validation (Validation & Analysis)
To reproduce the rigorous validation metrics:
1. Ensure the ground truth data (`data/GEE_Upload_Ready_LatLon.csv`) has been processed through Earth Engine using `04_extract_jrc_occurrence.js`.
2. Run the accuracy evaluation:
```bash
python python_scripts/06_per_class_accuracy.py
```

### C. GMM Component Selection (AIC/BIC)
To statistically validate the selection of a 2-component GMM over 3- or 4-component alternatives:
```bash
python python_scripts/07_gmm_information_criteria.py
```

---

## 📓 Unified Execution (Jupyter)
For a seamless, end-to-end execution and validation of the pipeline, two professional Jupyter notebooks are provided:

1. **`HydroSAR_Results_Replication.ipynb`**: Quick replication (~5 mins) using pre-computed datasets from GitHub. Generates all accuracy tables, diagnostic tests, and publication figures without requiring a Google Earth Engine account.
2. **`HydroSAR_Full_GEE_Pipeline.ipynb`**: Full end-to-end pipeline. Authenticates via the GEE Python API to extract massive datasets directly from the archive and reproduce the entire analysis from scratch. Includes an interactive DEMO mode to quickly verify methodology on a single district.
