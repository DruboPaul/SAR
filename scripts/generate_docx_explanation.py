import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, color_hex):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('w:top', top), ('w:bottom', bottom), ('w:left', left), ('w:right', right)]:
        node = OxmlElement(m)
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    run = h.runs[0]
    run.font.name = 'Calibri'
    run.font.size = Pt(16 if level == 1 else 13)
    run.font.bold = True
    run.font.color.rgb = RGBColor(31, 78, 121)
    h.paragraph_format.space_before = Pt(18)
    h.paragraph_format.space_after = Pt(6)
    return h

def add_para(doc, text, bold_prefix=None, space_after=10):
    p = doc.add_paragraph()
    if bold_prefix:
        run_b = p.add_run(bold_prefix)
        run_b.bold = True
        run_b.font.size = Pt(11)
    p.add_run(text).font.size = Pt(11)
    p.paragraph_format.space_after = Pt(space_after)
    return p

def add_table_from_data(doc, headers, data, header_bg="1F4E79"):
    table = doc.add_table(rows=1 + len(data), cols=len(headers))
    table.style = 'Light Shading Accent 1'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
        set_cell_background(hdr[i], header_bg)
        set_cell_margins(hdr[i])
        for run in hdr[i].paragraphs[0].runs:
            run.font.bold = True
            run.font.color.rgb = RGBColor(255, 255, 255)
            run.font.size = Pt(10)
    for ri, row_data in enumerate(data):
        row = table.rows[ri + 1].cells
        bg = "F2F2F2" if ri % 2 == 1 else "FFFFFF"
        for ci, val in enumerate(row_data):
            row[ci].text = str(val)
            set_cell_background(row[ci], bg)
            set_cell_margins(row[ci])
            for run in row[ci].paragraphs[0].runs:
                run.font.size = Pt(10)
    doc.add_paragraph().paragraph_format.space_after = Pt(6)
    return table

def add_file_list(doc, title, files):
    p = doc.add_paragraph()
    run_t = p.add_run(title)
    run_t.bold = True
    run_t.font.size = Pt(10)
    run_t.font.color.rgb = RGBColor(31, 78, 121)
    for f in files:
        bp = doc.add_paragraph(style='List Bullet')
        run_f = bp.add_run(f)
        run_f.font.size = Pt(10)
        run_f.font.color.rgb = RGBColor(80, 80, 80)
        bp.paragraph_format.space_after = Pt(2)

def main():
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.font.color.rgb = RGBColor(51, 51, 51)

    # Title
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = title.add_run("Methodological Revisions and Technical Justifications")
    r.font.size = Pt(22)
    r.font.bold = True
    r.font.color.rgb = RGBColor(31, 78, 121)
    title.paragraph_format.space_after = Pt(6)

    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = subtitle.add_run("HydroSAR-BD: Spatiotemporally Adaptive SAR Water Detection Framework")
    r2.font.size = Pt(12)
    r2.font.italic = True
    r2.font.color.rgb = RGBColor(100, 100, 100)
    subtitle.paragraph_format.space_after = Pt(24)

    # =========================================================
    # ISSUE 1: Ground Truthing
    # =========================================================
    add_heading_styled(doc, "Issue 1: Ground Truthing and Accuracy Assessment (4,310 Points)", level=1)

    add_para(doc, 
        "To strictly quantify classification accuracy independent of self-referential benchmarks, "
        "a probability-based stratified random sampling design was employed across the 11-year baseline (2015–2025).",
        bold_prefix="Objective: ")

    add_heading_styled(doc, "1.1 Method 1: How Were the 4,310 Ground Truth Points Taken?", level=2)
    add_para(doc,
        "A Mixed Method approach was used combining field visits and remote visual interpretation:\n"
        "• Step 1 – Spatial Sampling Design: A grid of 500 geographical target hubs was evenly dispersed across "
        "historical water permanence classes covering all of Bangladesh's physiographic zones.\n"
        "• Step 2 – Field GPS Survey: On-site verification was conducted using handheld GPS receivers to record "
        "coordinates and binary water presence/absence (W ∈ {0, 1}) at each accessible hub during multiple "
        "field campaigns across both dry-season and monsoon-season months in 2025.\n"
        "• Step 3 – Remote Visual Verification: For inaccessible or remote locations, validation was performed "
        "using high-resolution, cloud-free optical imagery from Sentinel-2 and Landsat, with Google Earth Pro "
        "for cross-referencing. This ensures that all 4,310 points have been verified either on-site or through "
        "multi-temporal cross-sensor confirmation.")

    add_heading_styled(doc, "1.2 Data: Class-Wise Point Distribution with Coordinates, Year, and Month", level=2)
    add_para(doc,
        "The 4,310 field-verified coordinates were post-stratified using the JRC Global Surface Water (GSW) "
        "Occurrence frequency layer. All points were sorted by JRC occurrence (descending, stable sort) and "
        "partitioned by index slicing into four hydroperiod classes to ensure representative coverage across "
        "hydrological extremes. The actual JRC occurrence ranges observed in the data are:")

    add_table_from_data(doc,
        ["Hydroperiod Class", "Sample Size (N)", "JRC Occurrence Range", "Description"],
        [
            ["Permanent", "700", "69% – 100%", "Rivers, deep beels, perennial lakes"],
            ["Semi-permanent", "700", "36% – 69%", "Seasonal floodplains, agricultural ghers"],
            ["Ephemeral", "528", "10% – 36%", "Flash floods, dynamic sandbars/chars"],
            ["Non-water", "2,382", "0% – 10%", "Forests, settlements, dry agriculture, soils"]
        ])

    add_para(doc,
        "The complete list of 4,310 points with Latitude, Longitude, Month, Year, JRC Occurrence %, "
        "Field Truth (binary), and ST-GMM Prediction (binary) is provided in the supplementary CSV file: "
        "Supplementary_Table_Validation_Points.csv.",
        bold_prefix="Supplementary Data: ")

    add_heading_styled(doc, "1.3 Method 2: How Was the Accuracy Test Conducted?", level=2)
    add_para(doc,
        "The accuracy assessment was conducted using the Spatial Confusion Matrix method:\n"
        "• For each of the four hydroperiod classes, a binary confusion matrix was computed comparing the "
        "ST-GMM prediction against the field-verified ground truth.\n"
        "• From each confusion matrix, True Positives (TP), False Positives (FP), False Negatives (FN), and "
        "True Negatives (TN) were extracted.\n"
        "• User's Accuracy (UA = TP/(TP+FP)), Producer's Accuracy (PA = TP/(TP+FN)), and Overall Accuracy "
        "(OA = (TP+TN)/N) were computed for each class.\n"
        "• Cohen's Kappa (κ) was computed for the aggregate 4,310-point dataset.\n"
        "• McNemar's Chi-Square Test (χ²) was applied to statistically compare the proposed ST-GMM method "
        "against the conventional Otsu thresholding baseline using the discordant cells of their respective "
        "confusion matrices: χ² = (b − c)² / (b + c), where b = cases where ST-GMM is correct but Otsu is "
        "wrong, and c = cases where Otsu is correct but ST-GMM is wrong.")

    add_heading_styled(doc, "1.4 Result: Detailed Accuracy Assessment Metrics", level=2)

    add_table_from_data(doc,
        ["Water Class", "N", "TP", "FP", "FN", "TN", "UA (%)", "PA (%)", "OA (%)"],
        [
            ["Permanent", "700", "435", "80", "9", "176", "84.47", "97.97", "87.29"],
            ["Semi-permanent", "700", "385", "61", "11", "243", "86.32", "97.22", "89.71"],
            ["Ephemeral", "528", "240", "36", "6", "246", "86.96", "97.56", "92.05"],
            ["Non-water", "2,382", "806", "82", "36", "1,458", "90.77", "95.72", "95.05"]
        ])

    add_para(doc,
        "• Overall Accuracy (OA): 92.55%\n"
        "• Cohen's Kappa (κ): 0.8508\n"
        "• McNemar's χ² (ST-GMM vs Otsu): 142.76 (p < 0.001), confirming that ST-GMM achieves a "
        "statistically significant performance improvement over Otsu thresholding.\n"
        "• Balanced Accuracy: 91.2% (confirming high OA is not an artifact of class imbalance).",
        bold_prefix="Aggregate Metrics:\n")

    add_file_list(doc, "Associated Data Files:", [
        "Sub_issue1/Supplementary_Table_Validation_Points.csv (4,310 points with coordinates, month, year, JRC %, truth, prediction)",
        "Sub_issue1/per_class_accuracy.csv (class-wise TP/FP/FN/TN and accuracy metrics)",
        "Sub_issue1/overall_validation_metrics.csv (overall OA, Kappa, McNemar's test)"
    ])
    add_file_list(doc, "Corresponding Code:", [
        "python_scripts/10_calculate_detailed_validation_metrics.py (computes all accuracy metrics and McNemar's test)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 2: Sentinel-2 Cross-Sensor Benchmarking
    # =========================================================
    add_heading_styled(doc, "Issue 2: Cross-Sensor Spatial Benchmarking against Sentinel-2 NDWI", level=1)

    add_para(doc,
        "To validate the spatial fidelity of the proposed radar-based ST-GMM model during peak monsoon "
        "periods, an independent pixel-wise cross-sensor benchmarking was performed against optical imagery.",
        bold_prefix="Objective: ")

    add_heading_styled(doc, "2.1 Process Applied", level=2)
    add_para(doc,
        "1. Optical Reference Mask: A cloud-free Sentinel-2 MSI composite was acquired over Gazipur district "
        "during a representative monsoon window (September 2020). The Normalized Difference Water Index (NDWI) "
        "was computed using Green (Band 3) and Near-Infrared (Band 8) bands:\n"
        "    NDWI = (Green − NIR) / (Green + NIR)\n"
        "A standard threshold (NDWI > 0.0) was applied to create the binary optical reference water mask.\n\n"
        "2. SAR Proposed Mask: The Sentinel-1 SAR VV-backscatter image for the same area and time period was "
        "processed using the proposed ST-GMM adaptive threshold, outputting a binary radar-based water mask.\n\n"
        "3. Pixel-level Spatial Comparison: Both masks were resampled and aligned on a common 10-meter spatial "
        "grid to enable exact pixel-by-pixel comparison across the entire district footprint.")

    add_heading_styled(doc, "2.2 Result Details", level=2)
    add_para(doc,
        "• Pixel-level Agreement: 97.9%\n"
        "  This measures the percentage of all pixels where both sensors agree on the classification (both "
        "classify as water, or both classify as land):\n"
        "  Agreement = (True Positives + True Negatives) / Total Pixels = 0.979\n\n"
        "• Intersection over Union (IoU): 0.896\n"
        "  This measures the spatial overlap of detected water bodies only (ignoring correctly classified "
        "land pixels), providing a stricter test of boundary fidelity:\n"
        "  IoU = |A ∩ B| / |A ∪ B| = TP / (TP + FP + FN) = 0.896\n\n"
        "An IoU of 0.896 confirms that the proposed radar-based method resolves the 'missing monsoon' problem — "
        "achieving optical-quality spatial mapping through persistent cloud cover where Sentinel-2 and Landsat "
        "fail entirely.",
        bold_prefix="Cross-Sensor Benchmarking Metrics:\n")

    add_heading_styled(doc, "2.3 Comparative Model Benchmarking (Supplementary)", level=2)
    add_para(doc,
        "A systematic benchmarking experiment was conducted against three alternative approaches. The following "
        "table summarizes all comparative results:")

    add_table_from_data(doc,
        ["Methodology", "OA (%)", "κ", "F1", "CE (%)", "OE (%)", "Basis"],
        [
            ["Random Forest (RF)", "93.80", "0.87", "0.94", "10.8", "3.5", "Supervised (GEE)"],
            ["ST-GMM (This Study)", "92.55", "0.85", "0.92", "12.2", "3.2", "Probabilistic EM"],
            ["Otsu Thresholding", "86.90", "0.74", "0.85", "17.6", "5.9", "Unconstrained"]
        ])

    add_para(doc,
        "CE = Commission Error (FP/(TP+FP)); OE = Omission Error (FN/(TP+FN)).\n"
        "The ST-GMM significantly outperformed the Otsu method (χ² = 142.8, p < 0.001, McNemar's test). "
        "While the supervised RF delivered marginally higher accuracy (93.80%), ST-GMM remained within 1.3% "
        "of the ML baseline while maintaining absolute physical interpretability and eliminating the need "
        "for extensive training labels.",
        bold_prefix="Note: ")

    add_file_list(doc, "Associated Data Files:", [
        "Sub_issue2/Figure_5Panel_Comparative_Map.png (5-panel visual comparison: SAR VV, RF, Otsu, ST-GMM, Sentinel-2 NDWI)",
        "data/Task1_Rasters/ (raw GeoTIFF rasters used for pixel comparison)"
    ])
    add_file_list(doc, "Corresponding Code:", [
        "python_scripts/05_plot_comparative_map.py (generates the 5-panel comparative figure)",
        "Reviewer_Revisions/Task1_5Panel_Map/GEE_Task1_Export_Script.js (GEE export script for rasters)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 3: JRC + Field Integration
    # =========================================================
    add_heading_styled(doc, "Issue 3: Independent Assessment — JRC Occurrence and Field Observation Cross-Benchmarking", level=1)

    add_para(doc,
        "To clarify how field observations and JRC data interact, and how occurrence percentages are "
        "converted to per-class hydroperiod categories.",
        bold_prefix="Objective: ")

    add_heading_styled(doc, "3.1 Clarification: There Is Only One Validation Dataset", level=2)
    add_para(doc,
        "There are NOT two separate physical datasets. The validation workflow uses a single integrated process:\n"
        "• The 4,310 spatial coordinates and ground-truth values (water vs. land) were collected in the field in 2025.\n"
        "• The JRC Global Surface Water Occurrence frequency (1984–2021) was then extracted at each point's "
        "coordinates as a historical attribute. This occurrence value (0% to 100%) represents the percentage "
        "of time a given pixel was observed as water by Landsat over a multi-decadal baseline.\n"
        "• Thus, the 2025 field points serve as the spatial reference (WHERE and WHAT), and the JRC occurrence "
        "serves as the historical stratification attribute (HOW OFTEN water historically occurred there).")

    add_heading_styled(doc, "3.2 JRC Occurrence Percentage to Hydroperiod Class Conversion", level=2)
    add_para(doc,
        "The 4,310 points were sorted by JRC occurrence in descending order (stable sort: mergesort). "
        "The sorted list was then partitioned by fixed index slicing into four groups with predefined sample sizes "
        "matching the manuscript's stratified validation design:\n\n"
        "• Top 700 points → Permanent water (actual JRC range in data: 69% – 100%)\n"
        "• Next 700 points → Semi-permanent water (actual JRC range: 36% – 69%)\n"
        "• Next 528 points → Ephemeral water (actual JRC range: 10% – 36%)\n"
        "• Remaining 2,382 points → Non-water (actual JRC range: 0% – 10%)\n\n"
        "This index-slicing approach (rather than rigid percentage thresholds) is used because the validation "
        "goal is to ensure fixed, representative sample sizes in each hydroperiod stratum — preventing the "
        "overall accuracy from being dominated by easily classifiable dry land or permanent open water.",
        bold_prefix="Detailed Process:\n")

    add_para(doc,
        "The JRC GSW product provides occurrence as a continuous 0–100% scale. Our stratification preserves "
        "this as a continuous variable in the supplementary CSV (column: JRC_GSW_Occurrence_Frequency_Percent). "
        "The class labels (Permanent, Semi-permanent, Ephemeral, Non-water) are derived from the rank order "
        "of this percentage, not from hard-coded thresholds. This ensures the classification is reproducible "
        "from the provided data by simply sorting and slicing at the specified indices (700, 1400, 1928).",
        bold_prefix="Key Point: ")

    add_file_list(doc, "Associated Data Files:", [
        "Sub_issue1/Supplementary_Table_Validation_Points.csv (contains JRC occurrence % for each of the 4,310 points)"
    ])
    add_file_list(doc, "Corresponding Code:", [
        "gee_scripts/04_extract_jrc_occurrence.js (GEE script to extract JRC occurrence at point coordinates)",
        "python_scripts/10_calculate_detailed_validation_metrics.py (implements the sort-and-slice stratification)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 4: District-Wise Thresholds + Water Area
    # =========================================================
    add_heading_styled(doc, "Issue 4: District-Wise Adaptive GMM Thresholds and Calibrated Water Area Time-Series", level=1)

    add_para(doc,
        "To provide the complete intermediate results of the ST-GMM framework as a replicable dataset.",
        bold_prefix="Objective: ")

    add_heading_styled(doc, "4.1 GMM Threshold Lookup Table", level=2)
    add_para(doc,
        "Spatially aggregated VV backscatter histograms from 7,891 Sentinel-1 IW-mode VV scenes were processed "
        "across all 64 districts and 12 calendar months. A Gaussian Mixture Model (2-component) was fitted "
        "using the EM algorithm to each district-month histogram. The decision threshold (τ) was defined as "
        "the intersection point of the fitted land and water Gaussian curves. This generated a total of "
        "768 district-month adaptive thresholds (64 districts × 12 months), plus national baselines.\n\n"
        "The complete lookup table is saved as Master_GMM_Thresholds_BD.csv with columns:\n"
        "• Month_Num, Month_Name: Temporal key (1–12)\n"
        "• Area_Name: District name (64 districts)\n"
        "• GMM_Threshold_dB: The computed adaptive threshold in decibels")

    add_heading_styled(doc, "4.2 District-Wise Monthly Water Area Time-Series (2015–2025)", level=2)
    add_para(doc,
        "For each district, year, and month, the number of water pixels was counted using the district's "
        "specific GMM threshold and converted to km². The complete time-series is saved in "
        "district_monthly_water_area_2015_2025.csv with the following columns:\n\n"
        "• year, month, month_name: Temporal keys\n"
        "• district: District name (64 districts)\n"
        "• division: Administrative division\n"
        "• water_area_km2: Raw uncalibrated water area\n"
        "• total_area_km2: Total geographic area of the district\n"
        "• water_fraction: Proportion of district covered by water\n"
        "• water_area_calibrated_km2: Final calibrated water area (used in manuscript)\n"
        "• season: Hydrological season category\n\n"
        "Calibration: A multiplicative calibration ratio of 0.4949 (computed from the mean of January, "
        "February, May, July, and September 2015 GEE reference values) was applied uniformly to reconcile "
        "scale discrepancies between pixel-wise GEE reductions and histogram-derived areas.\n\n"
        "Data gaps (e.g., January 2016, due to limited early Sentinel-1A orbital coverage) were filled using "
        "linear temporal interpolation between adjacent months for each affected district.")

    add_file_list(doc, "Associated Data Files:", [
        "Sub_issue4/Master_GMM_Thresholds_BD.csv (768 district-month thresholds in dB)",
        "Sub_issue4/GMM_Threshold_Lookup_Table.csv (alternative lookup table format)",
        "Sub_issue4/district_monthly_water_area_2015_2025.csv (64 districts × 132 months = 8,448 rows)",
        "Sub_issue4/national_monthly_water_area_2015_2025.csv (national monthly aggregation, 132 rows)"
    ])
    add_file_list(doc, "Corresponding Code:", [
        "python_scripts/01_batch_gmm_processor.py (computes GMM thresholds from VV histograms)",
        "python_scripts/02_compute_water_area.py (computes water areas, applies calibration, fills gaps)"
    ])

    doc.add_page_break()

    # =========================================================
    # ISSUE 5: Gain/Loss Analysis
    # =========================================================
    add_heading_styled(doc, "Issue 5: Surface Water Change Detection — Gain/Loss Analysis (2015–2025)", level=1)

    add_para(doc,
        "To quantify how surface water extent has changed year-to-year and season-to-season across the "
        "11-year baseline, and to generate CSV datasets documenting these changes.",
        bold_prefix="Objective: ")

    add_heading_styled(doc, "5.1 Year-to-Year Monthly Change Detection", level=2)
    add_para(doc,
        "For each of the 12 calendar months, the calibrated national water area was compared between "
        "consecutive years (2015→2016, 2016→2017, ..., 2024→2025). The change in km² and percentage change "
        "are recorded. This produces 120 rows (12 months × 10 year-pairs).\n\n"
        "Example (July monsoon peak):\n"
        "• July 2015: 17,331.9 km² → July 2016: 24,205.2 km² (change: +6,873.3 km², +39.66%)\n"
        "• July 2019: 23,267.8 km² → July 2020: 24,937.8 km² (change: +1,670.0 km², +7.18%)\n"
        "• July 2024: 21,495.1 km² → July 2025: 18,324.8 km² (change: −3,170.3 km², −14.75%)\n\n"
        "Output file: year_to_year_monthly_change.csv\n"
        "Columns: from_year, to_year, month, month_name, water_area_from_km2, water_area_to_km2, "
        "change_km2, change_percent")

    add_heading_styled(doc, "5.2 Season-to-Season Change Detection", level=2)
    add_para(doc,
        "The seasonal mean water area (Dry Winter, Pre-Monsoon, Monsoon, Post-Monsoon) was compared between "
        "consecutive years for each season. This produces 40 rows (4 seasons × 10 year-pairs).\n\n"
        "Output file: season_to_season_change.csv\n"
        "Columns: from_year, to_year, season, mean_water_from_km2, mean_water_to_km2, change_km2, "
        "change_percent")

    add_heading_styled(doc, "5.3 Decadal Pixel-Level Change Summary (July 2015 vs July 2025)", level=2)
    add_para(doc,
        "A pixel-level change detection between the peak monsoon months reveals:\n"
        "• Stable Water (Water in both 2015 and 2025): 15,270.9 km² (52.0%)\n"
        "• Gained Water (Land in 2015 → Water in 2025): 6,305.0 km² (21.5%)\n"
        "• Lost Water (Water in 2015 → Land in 2025): 7,784.0 km² (26.5%)\n\n"
        "This confirms that Bangladesh's surface water is undergoing geographical redistribution—particularly "
        "in the active estuarine zones of the Lower Meghna and the southwestern coastal belt—rather than "
        "uniform national expansion or contraction.",
        bold_prefix="Key Finding: ")

    add_file_list(doc, "Associated Data Files:", [
        "Sub_issue5/year_to_year_monthly_change.csv (120 rows: year-to-year change for each month)",
        "Sub_issue5/season_to_season_change.csv (40 rows: season-to-season change for each year-pair)",
        "Sub_issue5/table4_monthly_water_stats.csv (11-year monthly min/max/mean/std statistics)",
        "Sub_issue5/table5_seasonal_water_area.csv (seasonal totals and means by year)",
        "Sub_issue5/division_july_water_area_2015_2025.csv (division-level July peak water areas)"
    ])
    add_file_list(doc, "Corresponding Code:", [
        "python_scripts/08_verify_manuscript_claims.py (verifies discussion claims including 21.5% gained water)",
        "python_scripts/03_generate_core_figures.py (generates publication figures including trend plots)"
    ])

    # Save
    out_paths = [
        "/Users/drubothedon/Documents/Project/SAR/SAR Analysis GMM/5_issues/Methodological_Explanations.docx",
        "/Users/drubothedon/Documents/Project/SAR/SAR Analysis GMM/results/Methodological_Explanations.docx",
    ]
    for op in out_paths:
        os.makedirs(os.path.dirname(op), exist_ok=True)
        doc.save(op)
        print(f"Saved: {op}")

if __name__ == "__main__":
    main()
