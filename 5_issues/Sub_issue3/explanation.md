# Sub-Issue 3: JRC Occurrence and Field Observation Cross-Benchmarking

## 1. Context and Objective
Reviewers raised concerns about a potential contradiction between JRC (Landsat 2020) and Field (2025) validation points. 
* **The Reality:** There are **not** two separate physical validation datasets. 
* **The Process:** We used a single integrated validation workflow. The spatial coordinates and ground-truth values ($W \in \{0, 1\}$) were collected in the field in **2025** (field ground points). Then, the historical **JRC Global Surface Water (GSW) Occurrence Frequency Layer (1984–2021)** was used to post-stratify (group) these 4,310 points into hydrological hydroperiods to ensure a scientifically balanced accuracy assessment.

## 2. JRC Occurrence Extraction and post-stratification
1. **GEE Point Upload:** The coordinates of the 4,310 field-verified points were uploaded to Google Earth Engine (GEE) as a FeatureCollection (`users/drubothedon/GEE_Upload_Ready_LatLon`).
2. **Occurrence Band Sampling:** The GEE script loaded the JRC GSW Occurrence band (`JRC/GSW1_4/GlobalSurfaceWater`, band: `occurrence`), which represents the percentage of time (0% to 100%) that a given pixel was observed as water by Landsat over a multi-decadal baseline. The occurrence value was sampled at each point's coordinates.
3. **Class Slicing:** The points were then sorted by JRC occurrence descending (stable sort) and sliced into four groups representing distinct hydroperiods:
   - **Permanent water** ($N=700$): Selected from the highest occurrence frequencies ($F \ge 80\%$, representing permanent water).
   - **Semi-permanent water** ($N=700$): Selected from middle occurrences ($40\% \le F < 80\%$, representing seasonal agricultural ghers and floodplains).
   - **Ephemeral water** ($N=528$): Selected from low occurrences ($0\% < F < 40\%$, representing flash-flood zones and dynamic sandbars).
   - **Non-water** ($N=2382$): Selected from zero occurrence ($F = 0\%$, representing dry land, urban areas, and forests).

This post-stratification prevents the overall validation metrics from being dominated by easy-to-classify permanent open water or dry land, providing a rigorous test of the model on dynamic floodplains.

## 3. Associated Files in this Folder
* **`04_extract_jrc_occurrence.js`**: The Google Earth Engine (GEE) JavaScript code used to load the validation points asset, extract the JRC occurrence frequency values, and export the resulting table.
