# -*- coding: utf-8 -*-
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

def draw_box(ax, x, y, w, h, text_main, text_sub, bg_color, border_color, dashed=False):
    # Draw box
    ls = '--' if dashed else '-'
    rect = patches.FancyBboxPatch((x - w/2, y - h/2), w, h, 
                                  boxstyle="round,pad=0.1", 
                                  facecolor=bg_color, 
                                  edgecolor=border_color,
                                  linewidth=1.2,
                                  linestyle=ls,
                                  zorder=2)
    ax.add_patch(rect)
    
    # Text
    if text_main:
        ax.text(x, y + 0.1, text_main, ha='center', va='bottom', fontsize=10, fontweight='bold', color=border_color, zorder=3)
    if text_sub:
        lines = text_sub.split('\n')
        for i, line in enumerate(lines):
            ax.text(x, y - 0.1 - (i*0.2), line, ha='center', va='top', fontsize=8, color='#333333', zorder=3)
    return rect

def draw_arrow(ax, x1, y1, x2, y2, color='#666666', ls='-', head_w=0.1, head_l=0.15):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', 
                                color=color, 
                                lw=1.5,
                                ls=ls,
                                mutation_scale=15),
                zorder=1)

def draw_line(ax, x1, y1, x2, y2, color='#666666', ls='-'):
    ax.plot([x1, x2], [y1, y2], color=color, lw=1.5, ls=ls, zorder=1)

def generate_flowchart():
    fig, ax = plt.subplots(figsize=(12, 14), dpi=300)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Colors
    c_s1 = ('#DCEEFB', '#0D47A1')     # Sentinel
    c_gt = ('#DCEDC8', '#1B5E20')     # Ground truth
    c_anc = ('#ECEFF1', '#37474F')    # Ancillary
    c_stgmm = ('#EDE7F6', '#5C4DBF')  # ST-GMM
    c_out = ('#FBE9E7', '#BF360C')    # Open dataset
    
    # ==========================
    # 1. DATA INPUTS (y=11)
    # ==========================
    draw_box(ax, 2, 11, 2.5, 0.8, "Sentinel-1 SAR", "7,891 IW-GRD VV scenes", c_s1[0], c_s1[1])
    draw_box(ax, 5, 11, 2.5, 0.8, "Ground-truth reference", "4,310 stratified field obs.", c_gt[0], c_gt[1])
    draw_box(ax, 8, 11, 2.5, 0.8, "Ancillary data", "SRTM DEM • FAO GAUL • ERA5", c_anc[0], c_anc[1])
    
    # Separator 1
    ax.text(0.5, 10.2, "DATA INPUTS", rotation=90, fontsize=9, fontweight='bold', color='#888', ha='center', va='center')
    ax.plot([1, 9.5], [10.2, 10.2], color='#ccc', lw=1, ls='--')
    
    # ==========================
    # 2. CORE FRAMEWORK
    # ==========================
    ax.text(0.5, 6.5, "CORE FRAMEWORK", rotation=90, fontsize=9, fontweight='bold', color='#888', ha='center', va='center')
    
    # Preprocessing
    draw_box(ax, 2, 9, 2.5, 0.8, "SAR pre-processing", "Orbit • Calibration • Terrain", '#F5F5F5', '#37474F')
    draw_arrow(ax, 2, 10.6, 2, 9.4)
    
    draw_box(ax, 8, 9, 2.5, 0.8, "Topographic masking", "SRTM slope ≤ 5° filter", '#F5F5F5', '#37474F')
    draw_arrow(ax, 8, 10.6, 8, 9.4)
    
    # Ground truth path
    draw_line(ax, 5, 10.6, 5, 10.4, color=c_gt[1], ls='--')
    draw_line(ax, 5, 10.4, 0.8, 10.4, color=c_gt[1], ls='--')
    draw_line(ax, 0.8, 10.4, 0.8, 2, color=c_gt[1], ls='--')
    draw_arrow(ax, 0.8, 2.0, 1.3, 2.0, color=c_gt[1], ls='--')
    
    # Combine signals into ST-GMM
    draw_line(ax, 2, 8.6, 2, 8.2)
    draw_line(ax, 8, 8.6, 8, 8.2)
    draw_line(ax, 2, 8.2, 3.5, 8.2)
    draw_line(ax, 8, 8.2, 6.5, 8.2)
    draw_arrow(ax, 3.5, 8.2, 3.5, 7.8)
    draw_arrow(ax, 6.5, 8.2, 6.5, 7.8)
    
    # ST-GMM Box
    stgmm_bg = patches.FancyBboxPatch((2.2, 5.6), 5.6, 2.2, boxstyle="round,pad=0.1", fill=False, edgecolor=c_stgmm[1], lw=1.5, linestyle='--', zorder=0)
    ax.add_patch(stgmm_bg)
    
    stgmm_head = patches.FancyBboxPatch((2.6, 7.3), 4.8, 0.45, boxstyle="round,pad=0.05", facecolor='#EDE7F6', edgecolor=c_stgmm[1], lw=1.0, zorder=1)
    ax.add_patch(stgmm_head)
    
    ax.text(5, 7.55, "ST-GMM threshold calibration", ha='center', va='bottom', fontsize=11, fontweight='bold', color=c_stgmm[1], zorder=2)
    ax.text(5, 7.45, "Spatiotemporally Adaptive Gaussian Mixture Model", ha='center', va='top', fontsize=9, color=c_stgmm[1], zorder=2)
    
    draw_box(ax, 3.5, 6.5, 2.4, 0.7, "EM optimisation", "NDWI-bridged initialisation\n64 districts × 12 months", c_stgmm[0], c_stgmm[1])
    draw_box(ax, 6.5, 6.5, 2.4, 0.7, "Decision boundary", "P(W|x) = P(L|x)\n100% convergence", c_stgmm[0], c_stgmm[1])
    draw_arrow(ax, 4.7, 6.5, 5.3, 6.5, color=c_stgmm[1])
    
    draw_arrow(ax, 5, 5.8, 5, 5.2)
    
    draw_box(ax, 5, 4.8, 4.0, 0.8, "Monthly median VV composite", "Binary water mask W_dt per district-month", c_s1[0], c_s1[1])
    draw_arrow(ax, 5, 4.4, 5, 4.0)
    
    # Analytical Modules
    draw_line(ax, 5, 4.0, 1.5, 4.0)
    draw_line(ax, 5, 4.0, 8.5, 4.0)
    
    mods = [
        (1.5, "Occurrence", "frequency\nmapping"),
        (3.25, "Change", "detection\ngain / loss"),
        (5.0, "Seasonal", "footprint\n4 seasons"),
        (6.75, "Trend", "analysis\nMK • Sen's β"),
        (8.5, "Area", "calculation\nGEE pixels")
    ]
    ax.text(5, 4.25, "ANALYTICAL MODULES", ha='center', va='center', fontsize=9, fontweight='bold', color='#666', bbox=dict(facecolor='white', edgecolor='none', pad=2), zorder=2)
    for m in mods:
        draw_arrow(ax, m[0], 4.0, m[0], 3.6)
        draw_box(ax, m[0], 3.2, 1.5, 0.7, m[1], m[2], c_s1[0], c_s1[1])
        draw_arrow(ax, m[0], 2.85, m[0], 1.2)
        
    ax.plot([1, 9.5], [2.6, 2.6], color='#ccc', lw=1, ls='--')
    ax.text(0.5, 1.5, "OUTPUTS & VALID.", rotation=90, fontsize=9, fontweight='bold', color='#888', ha='center', va='center')

    # ==========================
    # 3. OUTPUTS & VALIDATION
    # ==========================
    draw_box(ax, 5, 2.0, 7.4, 0.8, "Independent accuracy assessment", "OA 92.55% • κ 0.85 • McNemar vs Otsu (p<0.001) • IoU 0.896 vs Sentinel-2\nBenchmarked: Random Forest • Otsu • JRC GSW", c_gt[0], c_gt[1])
    
    outs = [
        (1.5, "Water occur.", "Perm • semi • eph.", c_gt),
        (3.25, "Change det.", "2015–2025", c_gt),
        (5.0, "Seasonal atlas", "4-season comp.", c_gt),
        (6.75, "Decadal trend", "Div. • national", c_gt),
        (8.5, "Open dataset", "2015–2025", c_out)
    ]
    for m in outs:
        draw_box(ax, m[0], 0.8, 1.5, 0.7, m[1], m[2], m[3][0], m[3][1])
        
    # Info bottom
    ax.text(5, 0.2, "Processing platform: Google Earth Engine (GEE) • Statistical analysis: R v4.0+ • All 7,891 scenes processed cloud-based", ha='center', va='center', fontsize=8, color='#666', style='italic')

    # Save
    plt.tight_layout()
    pdf_out = os.path.join(FIGURES_DIR, "fig2_flowchart.pdf")
    png_out = os.path.join(FIGURES_DIR, "fig2_flowchart.png")
    
    plt.savefig(pdf_out, format='pdf', bbox_inches='tight')
    plt.savefig(png_out, format='png', bbox_inches='tight')
    plt.close()
    print(f"SUCCESS: Flowchart successfully generated:\n  - {pdf_out}\n  - {png_out}")

if __name__ == '__main__':
    generate_flowchart()
