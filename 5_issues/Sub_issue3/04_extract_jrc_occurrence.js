// ==============================================================================
// GEE Script: Extract JRC Water Occurrence for 4,310 Validation Points
// Copy and paste this into Google Earth Engine Code Editor.
// ==============================================================================

// 1. Load the JRC Global Surface Water Occurrence dataset (1984-2021)
var jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select('occurrence');

// 2. Load the 4,310 Validation Points as a GEE Asset
var validationPoints = ee.FeatureCollection("users/drubothedon/GEE_Upload_Ready_LatLon");

// 3. Extract the JRC occurrence value at each point location
var validationWithOccurrence = jrc.reduceRegions({
  collection: validationPoints,
  reducer: ee.Reducer.first(),
  scale: 30
});

// 4. Rename the default reducer output ('first') to 'occurrence'
var finalCollection = validationWithOccurrence.map(function(feature) {
  // If the point is on land (0 occurrence), JRC is masked and returns null. 
  // We explicitly set nulls to 0.
  var occ = feature.get('first');
  var finalOcc = ee.Algorithms.If(ee.Algorithms.IsEqual(occ, null), 0, occ);
  return feature.set('occurrence', finalOcc);
});

// 5. Export the resulting FeatureCollection as a CSV to Google Drive
Export.table.toDrive({
  collection: finalCollection,
  description: 'Validation_Points_With_Occurrence',
  fileFormat: 'CSV',
  selectors: ['class', 'Field_Truth', 'Month', 'Year', 'occurrence']
});
