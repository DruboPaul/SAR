# -*- coding: utf-8 -*-
"""
Publication Figure Generator — HydroSAR GMM Paper
==================================================
Reads from: data/GEE_data/computed_results/
Outputs to: figures/

Generates: fig4, fig5_july_peak_trend, fig6_divisional_heatmap,
           fig7_annual_mean_trend, fig8_monthly_boxplot, fig9_top10_districts

Run: py -3 scripts/generate_all_figures.py
"""

import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import os
from scipy import stats as scipy_stats

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS_DIR = os.path.join(BASE_DIR, "data", "GEE_data", "computed_results")
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

# --- LOAD DATA ---
print("Loading computed data...")
national_df = pd.read_csv(os.path.join(RESULTS_DIR, "national_monthly_water_area_2015_2025.csv"))
district_df = pd.read_csv(os.path.join(RESULTS_DIR, "district_monthly_water_area_2015_2025.csv"))
division_july_df = pd.read_csv(os.path.join(RESULTS_DIR, "division_july_water_area_2015_2025.csv"))
monthly_stats_df = pd.read_csv(os.path.join(RESULTS_DIR, "table4_monthly_water_stats.csv"))
seasonal_df = pd.read_csv(os.path.join(RESULTS_DIR, "table5_seasonal_water_area.csv"))

# --- GLOBAL STYLE ---
matplotlib.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 15,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 11,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

MONTH_LABELS = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
BD_AREA = 147570  # km2


# =====================================================================
# FIG 4: Seasonal Ribbon — Monthly Water Area with SD Band
# =====================================================================
def fig4_seasonal_ribbon():
    stats = national_df.groupby('month')['water_area_calibrated_km2'].agg(
        ['mean','std','min','max']).sort_index()

    x = np.arange(12)
    mean_v = stats['mean'].values
    std_v = stats['std'].values
    min_v = stats['min'].values
    max_v = stats['max'].values

    fig, ax = plt.subplots(figsize=(11, 5.5))

    # Season background
    seasons = [(0, 2, '#E8F4FD', 'Dry Winter'), (2, 5, '#FFF8E1', 'Pre-Monsoon'),
               (5, 9, '#FFEBEE', 'Monsoon'), (9, 11, '#E8F5E9', 'Post-Monsoon')]
    ymax = max(max_v) * 1.15
    for s, e, c, n in seasons:
        ax.axvspan(s-0.5, e-0.5, alpha=0.15, color=c, zorder=0)
        ax.text((s+e)/2 - 0.5, ymax*0.97, n, ha='center', fontsize=8, fontstyle='italic', color='#666')

    # Min-max range
    ax.fill_between(x, min_v, max_v, alpha=0.12, color='#1f77b4', label='Min-Max range (11 yr)')
    # +/- 1 SD
    ax.fill_between(x, mean_v - std_v, mean_v + std_v,
                    alpha=0.25, color='#1f77b4', label='Mean +/- 1 SD')
    # Mean line
    ax.plot(x, mean_v, 'o-', color='#1f77b4', lw=2.2, ms=7,
            mfc='white', mew=2, label='11-year Mean', zorder=5)

    # Peak annotation
    peak_idx = np.argmax(mean_v)
    ax.annotate("Peak: {:,.0f} km2\n({:.1f}% of land)".format(mean_v[peak_idx], mean_v[peak_idx]/BD_AREA*100),
                xy=(peak_idx, mean_v[peak_idx]), xytext=(peak_idx+1.5, mean_v[peak_idx]+2000),
                fontsize=9, ha='center',
                arrowprops=dict(arrowstyle='->', color='#333'),
                bbox=dict(boxstyle='round,pad=0.3', fc='#fff3e0', ec='#e65100'))

    ax.set_xticks(x)
    ax.set_xticklabels(MONTH_LABELS)
    ax.set_ylabel('Surface Water Area (km2)')
    ax.set_xlabel('Month')
    ax.set_title('Mean Monthly Surface Water Area in Bangladesh (2015-2025)')
    ax.legend(loc='lower left', framealpha=0.9)
    ax.grid(True, alpha=0.2, ls='--')
    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig4_seasonal_ribbon.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# FIG 5: July Peak Trend (National)
# =====================================================================
def fig5_july_peak_trend():
    july = national_df[national_df['month'] == 7].sort_values('year')
    years = july['year'].values.astype(float)
    area = july['water_area_calibrated_km2'].values.astype(float)

    slope, intercept, r_val, p_val, _ = scipy_stats.linregress(years, area)
    trend_line = slope * years + intercept

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(years, area, '-', color='#1f77b4', alpha=0.4, lw=1.5)
    ax.scatter(years, area, color='#1f77b4', s=90, zorder=5, edgecolors='white', lw=1.5)
    ax.plot(years, trend_line, '--', color='#d62728', lw=2.5,
            label='Linear trend: {:+.1f} km2/yr (R2={:.3f}, p={:.3f})'.format(slope, r_val**2, p_val))

    mean_val = np.mean(area)
    ax.axhline(y=mean_val, color='#666', ls=':', alpha=0.5, lw=1)
    ax.text(2025.3, mean_val, 'Mean: {:,.0f} km2'.format(mean_val), fontsize=9, color='#666', va='center')

    # Highlight flood years
    for yr, val in zip(years, area):
        if val > mean_val + np.std(area):
            ax.annotate('{:.0f}'.format(val), xy=(yr, val), xytext=(0, 12),
                       textcoords='offset points', fontsize=8, ha='center', color='#d62728')

    ax.set_xlabel('Year')
    ax.set_ylabel('Peak Water Area - July (km2)')
    ax.set_title('Decadal Trend in Peak Monsoon Water Extent (July, 2015-2025)')
    ax.legend(loc='upper left', fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.2, ls='--')
    ax.set_xticks(years)
    ax.set_xticklabels([str(int(y)) for y in years])
    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig5_july_peak_trend.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# FIG 6: Divisional Heatmap (July, 2015-2025)
# =====================================================================
def fig6_divisional_heatmap():
    pivot = division_july_df.pivot_table(index='division', columns='year', values='water_area_km2')
    pivot = pivot.sort_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(int(c)) for c in pivot.columns])
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index)

    # Cell labels
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i, j]
            color = 'white' if val > np.median(pivot.values) else 'black'
            ax.text(j, i, '{:,.0f}'.format(val), ha='center', va='center',
                    fontsize=8, color=color, fontweight='bold')

    plt.colorbar(im, ax=ax, label='Water Area (km2)', shrink=0.8)
    ax.set_title('Divisional Peak Monsoon Water Extent (July, 2015-2025)')
    ax.set_xlabel('Year')

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig6_divisional_heatmap.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# FIG 7: Annual Mean Trend
# =====================================================================
def fig7_annual_mean_trend():
    annual = national_df.groupby('year')['water_area_calibrated_km2'].mean().reset_index()
    years = annual['year'].values.astype(float)
    area = annual['water_area_calibrated_km2'].values.astype(float)

    slope, intercept, r_val, p_val, _ = scipy_stats.linregress(years, area)
    trend_line = slope * years + intercept

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.bar(years, area, color='#4393c3', edgecolor='#333', lw=0.5, width=0.7, zorder=3)
    ax.plot(years, trend_line, '--', color='#d62728', lw=2.5, zorder=4,
            label='Linear trend: {:+.1f} km2/yr (R2={:.3f}, p={:.3f})'.format(slope, r_val**2, p_val))

    mean_val = np.mean(area)
    ax.axhline(y=mean_val, color='#666', ls=':', alpha=0.5, lw=1)

    for yr, val in zip(years, area):
        ax.text(yr, val + 200, '{:,.0f}'.format(val), ha='center', va='bottom', fontsize=7, rotation=45)

    ax.set_xlabel('Year')
    ax.set_ylabel('Annual Mean Water Area (km2)')
    ax.set_title('Annual Mean Surface Water Area in Bangladesh (2015-2025)')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(axis='y', alpha=0.2, ls='--', zorder=0)
    ax.set_xticks(years)
    ax.set_xticklabels([str(int(y)) for y in years])
    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig7_annual_mean_trend.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# FIG 8: Monthly Boxplot (11-year distribution for each month)
# =====================================================================
def fig8_monthly_boxplot():
    monthly_data = []
    for m in range(1, 13):
        vals = national_df[national_df['month'] == m]['water_area_calibrated_km2'].values
        monthly_data.append(vals)

    fig, ax = plt.subplots(figsize=(11, 5.5))

    bp = ax.boxplot(monthly_data, labels=MONTH_LABELS, patch_artist=True,
                    widths=0.6, showfliers=True, zorder=3,
                    medianprops=dict(color='#d62728', lw=2),
                    flierprops=dict(marker='o', ms=5, markerfacecolor='#999'))

    # Color by season
    season_colors = ['#4393c3','#4393c3','#92c5de','#92c5de','#92c5de',
                     '#d6604d','#d6604d','#d6604d','#d6604d','#fdae61','#fdae61','#4393c3']
    for patch, color in zip(bp['boxes'], season_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    # Season backgrounds
    seasons = [(0.5, 2.5, '#E8F4FD', 'Dry Winter'), (2.5, 5.5, '#FFF8E1', 'Pre-Monsoon'),
               (5.5, 9.5, '#FFEBEE', 'Monsoon'), (9.5, 11.5, '#E8F5E9', 'Post-Monsoon')]
    for s, e, c, n in seasons:
        ax.axvspan(s, e, alpha=0.1, color=c, zorder=0)

    ax.set_ylabel('Surface Water Area (km2)')
    ax.set_xlabel('Month')
    ax.set_title('Monthly Surface Water Area Distribution (2015-2025, n=11)')
    ax.grid(axis='y', alpha=0.2, ls='--', zorder=0)
    ax.get_yaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig8_monthly_boxplot.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# FIG 9: Top 10 Most Flood-Prone Districts
# =====================================================================
def fig9_top10_districts():
    july_dist = district_df[district_df['month'] == 7]
    mean_july = july_dist.groupby('district')['water_area_calibrated_km2'].mean().sort_values(ascending=False)
    top10 = mean_july.head(10)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = plt.cm.RdYlBu_r(np.linspace(0.2, 0.8, 10))
    bars = ax.barh(range(len(top10)), top10.values, color=colors, edgecolor='#333', lw=0.5, zorder=3)

    ax.set_yticks(range(len(top10)))
    ax.set_yticklabels(top10.index)
    ax.invert_yaxis()
    ax.set_xlabel('Mean July Water Area (km2)')
    ax.set_title('Top 10 Most Flood-Prone Districts (Mean July Water Area, 2015-2025)')
    ax.grid(axis='x', alpha=0.2, ls='--', zorder=0)

    for i, (bar, val) in enumerate(zip(bars, top10.values)):
        ax.text(val + 20, i, '{:,.0f} km2'.format(val), va='center', fontsize=9, fontweight='bold')

    ax.get_xaxis().set_major_formatter(mticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    plt.tight_layout()
    path = os.path.join(FIGURES_DIR, 'fig9_top10_districts.png')
    plt.savefig(path)
    plt.close()
    print("  Saved: " + path)


# =====================================================================
# MAIN
# =====================================================================
if __name__ == '__main__':
    print("=" * 60)
    print("  HydroSAR GMM Paper — Figure Generator (Python)")
    print("  Data source: computed_results/")
    print("=" * 60)

    fig4_seasonal_ribbon()
    fig5_july_peak_trend()
    fig6_divisional_heatmap()
    fig7_annual_mean_trend()
    fig8_monthly_boxplot()
    fig9_top10_districts()

    print("")
    print("=" * 60)
    print("  6 figures saved to: " + FIGURES_DIR)
    print("")
    print("  Still need (GEE/QGIS):")
    print("    fig1_study_area.png        - QGIS/ArcGIS")
    print("    fig3_july_water_maps.png   - GEE export")
    print("    fig5_occurrence_2023.png   - GEE export")
    print("    fig6_seasonal_maps.png     - GEE export")
    print("    fig8_change_detection.png  - GEE export")
    print("=" * 60)
