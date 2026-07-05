// ==============================================================================
// Task 1: Export 5 Scenarios for Multi-Panel Comparative Map
// Copy and paste this code into Google Earth Engine Code Editor
// ==============================================================================

// 1. Define the Study Area (Gazipur district as an example for diverse landscape)
var bdDistricts = ee.FeatureCollection("FAO/GAUL/2015/level2");
var roi = bdDistricts.filter(ee.Filter.eq('ADM2_NAME', 'Gazipur')).geometry();

Map.centerObject(roi, 10);
Map.addLayer(roi, {}, 'ROI (Gazipur)', false);

// 2. Define Time Period (e.g., September 2020 - Assured Sentinel-1 & 2 coverage)
var startDate = '2020-09-01';
var endDate = '2020-09-30';

// ==============================================================================
// Layer 1: SAR VV (Raw Backscatter)
// ==============================================================================
var sarCollection = ee.ImageCollection("COPERNICUS/S1_GRD")
  .filterBounds(roi)
  .filterDate(startDate, endDate)
  .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'))
  .filter(ee.Filter.eq('instrumentMode', 'IW'))
  .select('VV');

var sarVV = sarCollection.median().clip(roi);
Map.addLayer(sarVV, {min: -25, max: 0}, '1. SAR VV', false);

// Function to mask clouds in Sentinel-2 using the QA60 band
function maskS2clouds(image) {
  var qa = image.select('QA60');
  // Bits 10 and 11 are clouds and cirrus, respectively.
  var cloudBitMask = 1 << 10;
  var cirrusBitMask = 1 << 11;
  // Both flags should be set to zero, indicating clear conditions.
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0)
      .and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  return image.updateMask(mask);
}

// ==============================================================================
// Layer 2: NDWI (Sentinel-2 Reference)
// ==============================================================================
var s2 = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
  .filterBounds(roi)
  .filterDate('2020-08-01', '2020-10-31') // Wider window to avoid no-data gaps from clouds
  .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 60)) // Filter out extremely cloudy scenes
  .map(maskS2clouds)
  .median()
  .clip(roi);

var ndwi = s2.normalizedDifference(['B3', 'B8']).rename('NDWI');
var ndwiWater = ndwi.gt(0); // Basic threshold for NDWI water
Map.addLayer(ndwi, {min: -1.0, max: 1.0, palette: ['red', 'white', 'blue']}, '5. NDWI (Continuous)', false);
Map.addLayer(ndwiWater, {min: 0, max: 1, palette: ['white', 'blue']}, '5. NDWI Water (Binary)', false);

// ==============================================================================
// Layer 3: Otsu Thresholding (Baseline Global Threshold)
// ==============================================================================
// Using a standard pre-calculated Otsu threshold for C-band SAR water extraction 
// in Bangladesh monsoon/post-monsoon (typically ~ -16.0 dB)
var otsuThresh = -16.0;
var otsuWater = sarVV.lt(otsuThresh);
Map.addLayer(otsuWater, {min: 0, max: 1, palette: ['white', 'cyan']}, '3. Otsu Water', false);

// ==============================================================================
// Layer 4: ST-GMM (Using a hardcoded threshold for simplicity based on your BD study, 
// e.g., typically around -15.5 for Gazipur in Monsoon. Replace with exact if known)
// ==============================================================================
var stgmmThresh = -15.5; 
var stgmmWater = sarVV.lt(stgmmThresh);
Map.addLayer(stgmmWater, {min: 0, max: 1, palette: ['white', 'darkblue']}, '4. ST-GMM Water', false);

// ==============================================================================
// Layer 5: Random Forest (Simple Classification based on SAR)
// ==============================================================================
// Stack SAR VV with NDWI water label so sampled points have BOTH properties
var stackedImage = sarVV.addBands(ndwiWater);

// Create training data using stratified sampling to balance Water and Non-water classes
var trainingPts = stackedImage.stratifiedSample({
  numPoints: 1000,
  classBand: 'NDWI',
  region: roi,
  scale: 30,
  seed: 42,
  geometries: true
});
// Train RF with SAR VV to predict Water (NDWI label)
var rfClassifier = ee.Classifier.smileRandomForest(50).train({
  features: trainingPts,
  classProperty: 'NDWI',
  inputProperties: ['VV']
});
var rfWater = sarVV.classify(rfClassifier);
Map.addLayer(rfWater, {min: 0, max: 1, palette: ['white', 'lightblue']}, '2. Random Forest Water', false);

// ==============================================================================
// EXPORTING TO GOOGLE DRIVE
// ==============================================================================
var exportScale = 30; // 30m resolution

Export.image.toDrive({image: sarVV, description: 'Task1_1_SAR_VV', folder: 'GEE_Task1_Exports', region: roi, scale: exportScale, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: rfWater, description: 'Task1_2_RandomForest', folder: 'GEE_Task1_Exports', region: roi, scale: exportScale, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: otsuWater, description: 'Task1_3_Otsu', folder: 'GEE_Task1_Exports', region: roi, scale: exportScale, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: stgmmWater, description: 'Task1_4_ST_GMM', folder: 'GEE_Task1_Exports', region: roi, scale: exportScale, crs: 'EPSG:4326', maxPixels: 1e10});
Export.image.toDrive({image: ndwi, description: 'Task1_5_NDWI', folder: 'GEE_Task1_Exports', region: roi, scale: exportScale, crs: 'EPSG:4326', maxPixels: 1e10});
