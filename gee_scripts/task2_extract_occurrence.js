// ==============================================================================
// GEE Script: Extract JRC Water Occurrence for 4,310 Validation Points
// Copy and paste this into Google Earth Engine Code Editor.
// ==============================================================================

// 1. Load the JRC Global Surface Water Occurrence dataset (1984-2021)
var jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select('occurrence');

// 2. Load the 4,310 Validation Points 
// Note: You must upload 'Final_Binary_Field_Validation_2025.csv' as a GEE Asset first.
// Replace 'users/your_username/Final_Binary_Field_Validation_2025' with your actual Asset ID.
var validationPoints = ee.FeatureCollection("users/drubothedon/Final_Binary_Field_Validation_2025");

// 3. Extract the JRC occurrence value at each point location
var validationWithOccurrence = jrc.reduceRegions({
  collection: validationPoints,
  reducer: ee.Reducer.first().rename(['occurrence']),
  scale: 30
});

// 4. Export the resulting FeatureCollection as a CSV to Google Drive
Export.table.toDrive({
  collection: validationWithOccurrence,
  description: 'Validation_Points_With_Occurrence',
  fileFormat: 'CSV',
  selectors: ['class', 'Field_Truth', 'Month', 'Year', 'occurrence', '.geo']
});
