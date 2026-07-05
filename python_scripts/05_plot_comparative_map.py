import os
import matplotlib.pyplot as plt
import rasterio
import numpy as np

# Set working directories (go 3 levels up to reach workspace root)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RASTER_DIR = os.path.join(BASE_DIR, "data", "Task1_Rasters")
OUTPUT_DIR = os.path.join(BASE_DIR, "Reviewer_Revisions")

# The expected filenames from GEE export
FILES = {
    'SAR_VV': os.path.join(RASTER_DIR, 'Task1_1_SAR_VV.tif'),
    'RF': os.path.join(RASTER_DIR, 'Task1_2_RandomForest.tif'),
    'Otsu': os.path.join(RASTER_DIR, 'Task1_3_Otsu.tif'),
    'ST_GMM': os.path.join(RASTER_DIR, 'Task1_4_ST_GMM.tif'),
    'NDWI': os.path.join(RASTER_DIR, 'Task1_5_NDWI.tif')
}

def plot_5panel_map():
    # Check if all files exist
    missing_files = [f for name, f in FILES.items() if not os.path.exists(f)]
    if missing_files:
        print("Error: The following downloaded GeoTIFFs are missing:")
        for mf in missing_files:
            print(f" - {mf}")
        print("\nPlease create the 'data/Task1_Rasters' folder and put the 5 downloaded GeoTIFFs there.")
        return

    print("All GeoTIFFs found. Generating 5-panel figure...")

    fig, axes = plt.subplots(1, 5, figsize=(25, 6))
    titles = [
        "(a) Sentinel-1 SAR VV\n(Raw Backscatter - Sept 2020)", 
        "(b) Random Forest\n(Supervised - Sept 2020)", 
        "(c) Otsu Thresholding\n(Global Unsupervised - Sept 2020)", 
        "(d) ST-GMM\n(Proposed Method - Sept 2020)", 
        "(e) Sentinel-2 NDWI\n(Optical Reference - Sept 2020)"
    ]
    
    cmap_binary = plt.cm.colors.ListedColormap(['#e0e0e0', '#004c99']) # Light gray for land, dark blue for water
    
    keys = ['SAR_VV', 'RF', 'Otsu', 'ST_GMM', 'NDWI']
    
    for i, key in enumerate(keys):
        ax = axes[i]
        
        with rasterio.open(FILES[key]) as src:
            img = src.read(1)
            
            # Mask out no-data values if any (GEE usually uses extremely small or large numbers for NoData)
            img = np.ma.masked_where(img < -9999, img)
            
            if key == 'SAR_VV':
                # SAR backscatter is continuous (usually -25 to 0 dB)
                im = ax.imshow(img, cmap='gray', vmin=-25, vmax=0)
            elif key == 'NDWI':
                # NDWI is continuous (range -1 to 1)
                im = ax.imshow(img, cmap='RdBu', vmin=-1.0, vmax=1.0)
            else:
                # Water masks are binary (0=Land, 1=Water)
                im = ax.imshow(img, cmap=cmap_binary, vmin=0, vmax=1)
                
        ax.set_title(titles[i], fontsize=14, pad=15, fontweight='bold')
        ax.axis('off') # Hide axes ticks for a cleaner map look
        
        # Add a subtle border around each map panel
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1.5)

    plt.tight_layout(pad=3.0)
    
    # Save the figure
    output_path = os.path.join(OUTPUT_DIR, 'Figure_5Panel_Comparative_Map.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated publication-ready figure: {output_path}")

if __name__ == "__main__":
    plot_5panel_map()
