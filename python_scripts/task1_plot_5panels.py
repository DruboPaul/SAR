import os
import matplotlib.pyplot as plt
import rasterio
import numpy as np

# Set working directories relative to script location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
RASTER_DIR = os.path.join(BASE_DIR, "data", "Task1_Rasters")
OUTPUT_DIR = os.path.join(BASE_DIR, "results")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Expected filenames
FILES = {
    'SAR_VV': os.path.join(RASTER_DIR, 'Task1_1_SAR_VV.tif'),
    'RF': os.path.join(RASTER_DIR, 'Task1_2_RandomForest.tif'),
    'Otsu': os.path.join(RASTER_DIR, 'Task1_3_Otsu.tif'),
    'ST_GMM': os.path.join(RASTER_DIR, 'Task1_4_ST_GMM.tif'),
    'NDWI': os.path.join(RASTER_DIR, 'Task1_5_NDWI.tif')
}

def plot_5panel_map():
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
        "(a) Sentinel-1 SAR VV\n(Raw Backscatter)", 
        "(b) Random Forest\n(Supervised)", 
        "(c) Otsu Thresholding\n(Global Unsupervised)", 
        "(d) ST-GMM\n(Proposed Method)", 
        "(e) Sentinel-2 NDWI\n(Optical Reference)"
    ]
    
    cmap_binary = plt.cm.colors.ListedColormap(['#e0e0e0', '#004c99']) # Light gray for land, dark blue for water
    keys = ['SAR_VV', 'RF', 'Otsu', 'ST_GMM', 'NDWI']
    
    for i, key in enumerate(keys):
        ax = axes[i]
        
        with rasterio.open(FILES[key]) as src:
            img = src.read(1)
            img = np.ma.masked_where(img < -9999, img)
            
            if key == 'SAR_VV':
                ax.imshow(img, cmap='gray', vmin=-25, vmax=0)
            else:
                ax.imshow(img, cmap=cmap_binary, vmin=0, vmax=1)
                
        ax.set_title(titles[i], fontsize=14, pad=15, fontweight='bold')
        ax.axis('off')
        
        for spine in ax.spines.values():
            spine.set_visible(True)
            spine.set_color('black')
            spine.set_linewidth(1.5)

    plt.tight_layout(pad=3.0)
    
    output_path = os.path.join(OUTPUT_DIR, 'Figure_5Panel_Comparative_Map.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Successfully generated publication-ready figure: {output_path}")

if __name__ == "__main__":
    plot_5panel_map()
