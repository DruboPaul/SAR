# Sub-Issue 2: Sentinel-2 Cross-Sensor Benchmarking

## 1. Process Applied
To validate the spatial fidelity of our proposed radar-based ST-GMM model during peak monsoon periods, we performed a pixel-wise cross-sensor benchmarking against optical imagery.
* **Optical Reference:** A cloud-free Sentinel-2 MSI composite was acquired over Gazipur district during a representative monsoon window (September 2020). The Normalized Difference Water Index (NDWI) was computed using the Green (Band 3) and Near-Infrared (Band 8) bands:
  $$\text{NDWI} = \frac{\text{Green} - \text{NIR}}{\text{Green} + \text{NIR}}$$
  A standard threshold ($\text{NDWI} > 0.0$) was applied to create the binary optical reference water mask.
* **SAR Proposed Mask:** The Sentinel-1 SAR VV-backscatter image was processed using the proposed ST-GMM adaptive threshold, outputting a binary radar-based water mask.
* **Grid Alignment:** Both masks were aligned on a common 10-meter spatial grid to enable exact pixel-by-pixel spatial comparison.

## 2. Benchmark Comparison Results
The cross-sensor benchmarking yielded excellent spatial overlap, confirming that the radar-based thresholding accurately mirrors high-resolution optical mapping without cloud dependency:
* **Pixel-level Agreement**: **97.9%**
  This measures the overall percentage of matching pixels (both land and water) between the two sensors:
  $$\text{Agreement} = \frac{\text{True Positives} + \text{True Negatives}}{\text{Total Pixels}} = 0.979$$
* **Intersection over Union (IoU)**: **0.896**
  This measures the spatial overlap of the detected water bodies, calculating the ratio of the intersection of water pixels to the union of water pixels:
  $$\text{IoU} = \frac{|A \cap B|}{|A \cup B|} = \frac{\text{True Positives}}{\text{True Positives} + \text{False Positives} + \text{False Negatives}} = 0.896$$

## 3. Associated Files in this Folder
* **`Figure_5Panel_Comparative_Map.png`**: The publication figure showing a visual side-by-side comparison of Gazipur district water masks in September 2020:
  - (a) Raw Sentinel-1 SAR VV backscatter.
  - (b) Supervised Machine Learning (Random Forest) baseline.
  - (c) Global Unsupervised (Otsu) thresholding.
  - (d) Proposed Spatiotemporally Adaptive GMM (ST-GMM).
  - (e) Continuous Sentinel-2 NDWI (Optical Reference).
* **`05_plot_comparative_map.py`**: The python script used to load the processed GeoTIFF rasters and generate the 5-panel comparative map figure.
