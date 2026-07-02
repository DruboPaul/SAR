/* ==================================================================================
   11-Year District-Wise VV Histogram Exporter (2015-2025)
   
   This script extracts the VV backscatter distribution for districts of
   Bangladesh for every month from 2015 to 2025.
   
   Modes:
   - 'ALL':    Exports all 64 districts in one master CSV (Recommended for paper).
   - 'SINGLE': Exports only the one district named in TARGET_DISTRICT.
   
   Output: A CSV file in Google Drive.
================================================================================== */

// ─── USER CONFIGURATION ────────────────────────────────────────────────────────
var EXPORT_MODE = 'ALL';             // Options: 'ALL' or 'SINGLE'
var TARGET_DISTRICT = 'Sunamganj';   // Only used if EXPORT_MODE is 'SINGLE'

var startYear = 2015;
var endYear = 2025;

// ─── INITIALIZATION ─────────────────────────────────────────────────────────────
var bdBoundary = ee.FeatureCollection('projects/ee-mbokshi45/assets/bdshp');
var years = ee.List.sequence(startYear, endYear);
var months = ee.List.sequence(1, 12);
var bdGeom = bdBoundary.geometry();

// Filter districts based on mode
var districtColl = ee.FeatureCollection("FAO/GAUL/2015/level2")
                  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));

if (EXPORT_MODE === 'SINGLE') {
  districtColl = districtColl.filter(ee.Filter.eq('ADM2_NAME', TARGET_DISTRICT));
}

var districtList = districtColl.toList(districtColl.size());

print('Selected Mode:', EXPORT_MODE);
if (EXPORT_MODE === 'SINGLE') print('Target District:', TARGET_DISTRICT);
print('Districts to process:', districtColl.size());

// ─── MAIN LOOP: Year → Month → District ─────────────────────────────────────────
var histogramData = years.map(function(y) {
  return months.map(function(m) {
    var start = ee.Date.fromYMD(y, m, 1);
    var end = start.advance(1, 'month');
    
    var s1_col = ee.ImageCollection('COPERNICUS/S1_GRD')
      .filterBounds(bdGeom)
      .filterDate(start, end)
      .filter(ee.Filter.eq('instrumentMode', 'IW'))
      .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV'));
    
    var imgCount = s1_col.size();
    
    var medianImg = ee.Image(ee.Algorithms.If(
      imgCount.gt(0),
      s1_col.select('VV').median(),
      null
    ));
    
    return districtList.map(function(distFeature) {
      var dist = ee.Feature(distFeature);
      var distName = dist.get('ADM2_NAME');
      
      var histDict = ee.Dictionary(ee.Algorithms.If(
        medianImg,
        medianImg.reduceRegion({
          reducer: ee.Reducer.histogram({
            maxBuckets: 200,
            minBucketWidth: 0.15
          }),
          geometry: dist.geometry(),
          scale: 100,
          bestEffort: true,
          maxPixels: 1e13,
          tileScale: 16
        }),
        ee.Dictionary({VV: ee.Dictionary({histogram: [], bucketMeans: []})})
      ));
      
      var vvHist = ee.Dictionary(histDict.get('VV', 
        ee.Dictionary({histogram: [], bucketMeans: []})
      ));
      
      return ee.Feature(null, {
        'year': y,
        'month': m,
        'district_name': distName,
        'histogram_counts': vvHist.get('histogram', []),
        'histogram_means': vvHist.get('bucketMeans', []),
        'img_count': imgCount
      });
    });
  });
}).flatten();

var histogramCollection = ee.FeatureCollection(histogramData);

// ─── EXPORT ──────────────────────────────────────────────────────────────────────
var exportName = EXPORT_MODE === 'ALL' 
  ? 'Bangladesh_District_VV_Histograms_2015_2025'
  : 'Histogram_' + TARGET_DISTRICT + '_2015_2025';

Export.table.toDrive({
  collection: histogramCollection,
  description: exportName,
  fileFormat: 'CSV'
});

print('Export task created named: ' + exportName);
print('Go to the "Tasks" tab and click RUN.');
