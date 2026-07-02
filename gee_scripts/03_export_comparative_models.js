// ==============================================================================
// GEE Script: Export 5 Scenarios for Multi-Panel Comparative Map
// Copy and paste this code into Google Earth Engine Code Editor.
// Study Area: Gazipur District, Bangladesh | Period: September 2020
// ==============================================================================

// 1. Define the Study Area (Gazipur district - diverse urban/water landscape)
var bdDistricts = ee.FeatureCollection("FAO/GAUL/2015/level2");
var roi = bdDistricts.filter(ee.Filter.eq('ADM2_NAME', 'Gazipur')).geometry();

Map.centerObject(roi, 10);
Map.addLayer(roi, {color: 'red'}, 'ROI (Gazipur)', false);

// 2. Define Time Period (September 2020 - assured Sentinel-1 & 2 coverage)
var startDate = '2020-09-01';
var endDate   = '2020-09-30';

// ==============================================================================
// Layer 1: SAR VV (Raw Sentinel-1 Backscatter)
// ==============================================================================
var sarVV = ee.ImageCollection("COPERNICUS/S1_GRD")
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .select('VV')
  .median()
  .clip(roi);

Map.addLayer(sarVV, {min: -25, max: 0}, '1. SAR VV', false);

// ==============================================================================
// Layer 2: NDWI Water (Sentinel-2 Optical Reference)
// FIX: Added cloud filter (CLOUDY_PIXEL_PERCENTAGE) to avoid cloud-corrupted pixels
// ==============================================================================
var s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))  // FIX: cloud filter added
  .median()
  .clip(roi);

var ndwi = s2.normalizedDifference(['B3', 'B8']).rename('NDWI');
var ndwiWater = ndwi.gt(0).rename('NDWI_Water');
Map.addLayer(ndwiWater, {min: 0, max: 1, palette: ['white', 'blue']}, '5. NDWI Water', false);

// ==============================================================================
// Layer 3: Otsu Thresholding (Fixed Global Threshold Baseline)
// Using pre-calculated Otsu threshold for C-band SAR in Bangladesh monsoon (~-16 dB)
// ==============================================================================
var otsuThresh = -16.0;
var otsuWater  = sarVV.lt(otsuThresh).rename('otsu_water');
Map.addLayer(otsuWater, {min: 0, max: 1, palette: ['white', 'cyan']}, '3. Otsu Water', false);

// ==============================================================================
// Layer 4: ST-GMM Water (Seasonal-Adaptive GMM Threshold for Gazipur, Sep 2020)
// Threshold approximately -15.5 dB for this district/season combination
// ==============================================================================
var stgmmThresh = -15.5;
var stgmmWater  = sarVV.lt(stgmmThresh).rename('stgmm_water');
Map.addLayer(stgmmWater, {min: 0, max: 1, palette: ['white', 'darkblue']}, '4. ST-GMM Water', false);

// ==============================================================================
// Layer 5: Random Forest (SAR-based supervised classification)
// FIX: Stack SAR VV with NDWI_Water BEFORE sampling so both bands are accessible
// FIX: classProperty changed to 'NDWI_Water' to match the renamed band
// ==============================================================================
var stackedImage = sarVV.addBands(ndwiWater);  // Stack: VV + NDWI_Water

var trainingPts = stackedImage.sample({
  region: roi,
  scale: 30,
  numPixels: 2000,
  seed: 42,
  geometries: true
});

// Train Random Forest: use SAR VV to predict NDWI-derived water label
var rfClassifier = ee.Classifier.smileRandomForest(50).train({
  features: trainingPts,
  classProperty: 'NDWI_Water',   // FIX: must match the renamed band above
  inputProperties: ['VV']
});

var rfWater = sarVV.classify(rfClassifier).rename('rf_water');
Map.addLayer(rfWater, {min: 0, max: 1, palette: ['white', 'lightblue']}, '2. Random Forest Water', false);

// ==============================================================================
// EXPORT TO GOOGLE DRIVE (5 separate GeoTIFFs)
// Click "Run" then go to Tasks tab → click Run on each export task
// ==============================================================================
var exportParams = {
  folder: 'GEE_Task1_Exports',
  region: roi,
  scale: 30,
  crs: 'EPSG:4326',
  maxPixels: 1e10
};

Export.image.toDrive({image: sarVV,     description: 'Task1_1_SAR_VV',       folder: 'GEE_Task1_Exports', region: roi, scale: 30, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: rfWater,   description: 'Task1_2_RandomForest',  folder: 'GEE_Task1_Exports', region: roi, scale: 30, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: otsuWater, description: 'Task1_3_Otsu',          folder: 'GEE_Task1_Exports', region: roi, scale: 30, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: stgmmWater,description: 'Task1_4_ST_GMM',        folder: 'GEE_Task1_Exports', region: roi, scale: 30, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: ndwiWater, description: 'Task1_5_NDWI',          folder: 'GEE_Task1_Exports', region: roi, scale: 30, crs: 'EPSG:4326', maxPixels: 1e10});
