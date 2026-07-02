/* ==================================================================================
   Export February Water Masks (2015-2025) as Multi-band GeoTIFF
   ---------------------------------------------------------------
   Purpose:
     Generates surface water classification for February of each year (2015–2025)
     using district-specific GMM thresholds from the pre-computed CSV asset.
     
   Output:
     A single 11-band GeoTIFF (one band per year) exported to Google Drive.
     Band names: Feb_2015, Feb_2016, ..., Feb_2025
     Pixel values: 1 = water, 0 = non-water
     
   Asset Required:
     "projects/ee-drubopaul/assets/Master_GMM_Thresholds_BD" (CSV with
     district_name, month, threshold columns)
================================================================================== */

// ─── USER CONFIGURATION ────────────────────────────────────────────────────────
var THRESHOLD_ASSET = 'projects/ee-drubopaul/assets/Master_GMM_Thresholds_BD';
var EXPORT_SCALE    = 30;       // Export resolution in meters (10, 30, or 100)
var EXPORT_FOLDER   = 'GEE_Exports';  // Google Drive folder

// ─── DATASETS ──────────────────────────────────────────────────────────────────
var districts = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));

// FAO Bangladesh boundary (level0) — simpler geometry to avoid payload issues
var bdBoundary = ee.FeatureCollection('FAO/GAUL/2015/level0')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var exportRegion = bdBoundary.geometry().simplify(100);

var gmmThresholds = ee.FeatureCollection(THRESHOLD_ASSET);

// Validate threshold asset
var thresholdCount = gmmThresholds.size();
print('GMM Threshold records loaded:', thresholdCount);

// ─── PARAMETERS ────────────────────────────────────────────────────────────────
var FEBRUARY_MONTH = 2;
var years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025];

// Terrain / flat mask (consistent with App_code_final.js methodology)
var jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater');
var jrcOccurrence  = jrc.select('occurrence').unmask(0);
var jrcSeasonality = jrc.select('seasonality').unmask(0);
var srtmSlope = ee.Terrain.slope(ee.Image('CGIAR/SRTM90_V4'));
var flatMask = srtmSlope.lte(8).or(jrcOccurrence.gt(0)).or(jrcSeasonality.gt(0));

// ─── HELPER: Build per-district threshold image ────────────────────────────────
// Rasterizes the CSV thresholds so each district gets its own threshold value
function buildThresholdImage(monthNum) {
  // Filter CSV to February only
  var febThresholds = gmmThresholds.filter(ee.Filter.eq('month', monthNum));
  
  // Join thresholds to district geometries by matching district_name → ADM2_NAME
  var joinFilter = ee.Filter.equals({
    leftField:  'ADM2_NAME',
    rightField: 'district_name'
  });
  
  var joined = ee.Join.saveFirst('threshold_feature').apply({
    primary:   districts,
    secondary: febThresholds,
    condition: joinFilter
  });
  
  // Paint each district with its threshold value
  var withThreshold = joined.map(function(f) {
    var thresholdFeat = ee.Feature(f.get('threshold_feature'));
    return f.set('gmm_threshold', thresholdFeat.get('threshold'));
  });
  
  // Rasterize: each pixel gets the threshold of the district it falls in
  var thresholdImage = withThreshold
    .reduceToImage(['gmm_threshold'], ee.Reducer.first())
    .rename('threshold');
  
  return thresholdImage;
}

// ─── HELPER: Build February water mask for a given year ────────────────────────
function buildFebWaterMask(year, thresholdImage) {
  var yearStr = String(year);
  
  // Primary: February imagery
  var s1Core = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(exportRegion)
    .filterDate(yearStr + '-02-01', yearStr + '-02-28')
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .select('VV');
  
  // Gap-fill: ±1 month window (Jan–Mar) for data-sparse areas
  var s1Fill = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(exportRegion)
    .filterDate(yearStr + '-01-01', yearStr + '-03-31')
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
    .select('VV');
  
  var s1Primary  = s1Core.median();
  var s1Fallback = s1Fill.median();
  var s1 = s1Primary.unmask(s1Fallback).clip(exportRegion);
  
  // Apply district-specific threshold: water where VV ≤ threshold
  var waterMask = s1.lte(thresholdImage).and(flatMask).selfMask().unmask(0).toUint8();
  
  return waterMask.rename('Feb_' + yearStr);
}

// ─── BUILD MULTI-BAND IMAGE ───────────────────────────────────────────────────
var thresholdImage = buildThresholdImage(FEBRUARY_MONTH);
print('February threshold image built');

// Use ee.Image.cat() instead of loop to reduce serialization size
var allBands = years.map(function(year) {
  return buildFebWaterMask(year, thresholdImage);
});

var multiBand = ee.Image.cat(allBands);
print('Multi-band image band names:', multiBand.bandNames());

// ─── VISUALIZE (optional — preview the latest year) ────────────────────────────
Map.centerObject(exportRegion, 7);
Map.addLayer(multiBand.select('Feb_2025').selfMask(), {palette: ['0000FF']}, 'Feb 2025 Water');
Map.addLayer(multiBand.select('Feb_2020').selfMask(), {palette: ['00BFFF']}, 'Feb 2020 Water', false);
Map.addLayer(multiBand.select('Feb_2015').selfMask(), {palette: ['1E90FF']}, 'Feb 2015 Water', false);

// Show district boundaries
Map.addLayer(districts.style({color: 'red', width: 1, fillColor: '00000000'}), {}, 'Districts', false);

// ─── EXPORT TO GOOGLE DRIVE ────────────────────────────────────────────────────
Export.image.toDrive({
  image: multiBand,
  description: 'February_Water_Masks_GMM_2015_2025',
  folder: EXPORT_FOLDER,
  fileNamePrefix: 'February_Water_Masks_GMM_2015_2025',
  region: exportRegion,
  scale: EXPORT_SCALE,
  maxPixels: 1e13,
  shardSize: 256,
  fileFormat: 'GeoTIFF'
});

print('─────────────────────────────────────────────');
print('Export task created: "February_Water_Masks_GMM_2015_2025"');
print('Resolution: ' + EXPORT_SCALE + 'm');
print('Bands: 11 (Feb_2015 → Feb_2025)');
print('Values: 1 = Water, 0 = Non-water');
print('─────────────────────────────────────────────');
print('→ Go to the TASKS tab and click RUN to start export.');
