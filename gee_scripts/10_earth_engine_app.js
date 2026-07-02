/* ==================================================================================
   SAR-based Surface Water Explorer for Bangladesh (Dynamic GMM EM - No CSV)
   v4 — Error fixes: HAND asset removed, null guards added
   ---------------------------------------------------------------
   Fixes applied vs v1:
     FIX 1 — col.median() instead of col.first() for stable histogram sampling
     FIX 2 — Slope filter REMOVED for delta/coastal — replaced with HAND index
     FIX 3 — GMM initial means shifted: mu1=-20, mu2=-10 (broader separation)
     FIX 4 — Fallback threshold lowered -16.5 → -18.0 dB
     FIX 5 — SAR no-data gaps filled via temporal gap-fill (mosaic with prior month)
     FIX 6 — Threshold clamped to max -15.5 dB to prevent too-high GMM results
     FIX 7 — Slope mask replaced: use HAND (Height Above Nearest Drainage) ≤ 5m
================================================================================== */

/* -------------------- Datasets -------------------- */
var districts = ee.FeatureCollection('FAO/GAUL/2015/level2')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var divisions = ee.FeatureCollection('FAO/GAUL/2015/level1')
  .filter(ee.Filter.eq('ADM0_NAME', 'Bangladesh'));
var bdBoundary = districts.geometry();

/* -------------------- Parameters -------------------- */
var monthMap = {
  'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6,
  'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12
};
var monthStrMap = {
  'January': '01', 'February': '02', 'March': '03', 'April': '04', 'May': '05', 'June': '06',
  'July': '07', 'August': '08', 'September': '09', 'October': '10', 'November': '11', 'December': '12'
};
var monthEndDays = {
  'January': '31', 'February': '28', 'March': '31', 'April': '30', 'May': '31', 'June': '30',
  'July': '31', 'August': '31', 'September': '30', 'October': '31', 'November': '30', 'December': '31'
};

var yearList = ['2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'];

/* ==================== DYNAMIC GMM EM ALGORITHM ==================== */

function normPDF(x, mu, sigma) {
  var variance = Math.pow(sigma, 2);
  return Math.exp(-Math.pow(x - mu, 2) / (2 * variance)) / Math.sqrt(2 * Math.PI * variance);
}

function runGMM_EM(counts, means) {
  // Broader initial separation for coastal/delta areas
  var mu1 = -20, mu2 = -10;
  var sigma1 = 2, sigma2 = 2;
  var w1 = 0.5, w2 = 0.5;

  var n = counts.length;
  var totalCount = 0;
  for (var i = 0; i < n; i++) totalCount += counts[i];

  for (var iter = 0; iter < 10; iter++) {
    var resp1 = [], resp2 = [];
    var sumResp1 = 0, sumResp2 = 0;
    var newMu1 = 0, newMu2 = 0;

    // E-Step
    for (var i = 0; i < n; i++) {
      var p1 = w1 * normPDF(means[i], mu1, sigma1);
      var p2 = w2 * normPDF(means[i], mu2, sigma2);
      var total = p1 + p2 + 1e-10;
      var r1 = p1 / total;
      var r2 = p2 / total;
      resp1.push(r1); resp2.push(r2);
      var ec1 = r1 * counts[i];
      var ec2 = r2 * counts[i];
      sumResp1 += ec1; sumResp2 += ec2;
      newMu1 += ec1 * means[i]; newMu2 += ec2 * means[i];
    }

    // M-Step
    mu1 = newMu1 / sumResp1;
    mu2 = newMu2 / sumResp2;

    var newVar1 = 0, newVar2 = 0;
    for (var i = 0; i < n; i++) {
      newVar1 += resp1[i] * counts[i] * Math.pow(means[i] - mu1, 2);
      newVar2 += resp2[i] * counts[i] * Math.pow(means[i] - mu2, 2);
    }
    sigma1 = Math.sqrt(newVar1 / sumResp1 + 1e-5);
    sigma2 = Math.sqrt(newVar2 / sumResp2 + 1e-5);
    w1 = sumResp1 / totalCount;
    w2 = 1.0 - w1;
  }

  // Lowered fallback threshold (-18.0 dB) for coastal/delta safety
  var bestThreshold = -18.0;
  var minDiff = 1e10;
  for (var x = -30; x < -5; x += 0.1) {
    var p1 = w1 * normPDF(x, mu1, sigma1);
    var p2 = w2 * normPDF(x, mu2, sigma2);
    var diff = Math.abs(p1 - p2);
    if (diff < minDiff && x > mu1 && x < mu2) {
      minDiff = diff;
      bestThreshold = x;
    }
  }

  return { threshold: bestThreshold, mu: [mu1, mu2], sigma: [sigma1, sigma2], w: [w1, w2] };
}

function computeDynamicThreshold(geom, year, monthName, callback) {
  var monthStr = monthStrMap[monthName];
  var endDay   = monthEndDays[monthName];

  var col = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(
      year + '-' + monthStr + '-01',
      year + '-' + monthStr + '-' + endDay
    )
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .select('VV');

  col.size().evaluate(function(c) {
    if (c === 0) {
      print('[!] No S1 data for ' + monthName + ' ' + year + '. Using fallback -18.0 dB');
      callback(-18.0);
      return;
    }

    // Use 3-month window median for stable, gap-filled histogram
    var prevDate = ee.Date(year + '-' + monthStr + '-01').advance(-1, 'month');
    var nextDate = ee.Date(year + '-' + monthStr + '-' + endDay).advance(1, 'month');
    var s1Wide = ee.ImageCollection('COPERNICUS/S1_GRD')
      .filterBounds(geom)
      .filterDate(prevDate, nextDate)
      .filter(ee.Filter.eq('instrumentMode', 'IW'))
      .select('VV');
    var s1 = s1Wide.median();

    var sample = s1.sample({
      region: geom.bounds(),
      scale: 250,
      numPixels: 5000,
      seed: 42,
      geometries: false
    });

    var histResult = sample.reduceColumns({
      reducer: ee.Reducer.histogram(100),
      selectors: ['VV']
    });

    histResult.evaluate(function(res) {
      var h = (res && res.histogram) ? res.histogram : null;
      if (!h || !h.histogram || h.histogram.length === 0) {
        print('[!] Empty histogram. Using fallback -18.0 dB');
        callback(-18.0);
        return;
      }
      var gmmResult = runGMM_EM(h.histogram, h.bucketMeans);
      // Clamp threshold to max -15.5 dB to prevent under-detection
      var finalThreshold = Math.min(gmmResult.threshold, -15.5);
      print('Dynamic GMM Threshold: ' + gmmResult.threshold.toFixed(2) + ' dB → clamped to: ' + finalThreshold.toFixed(2) + ' dB');
      callback(finalThreshold);
    });
  });
}

function buildWaterMask(regionFeat, year, monthName, threshold) {
  var geom = regionFeat.geometry();
  var monthStr = monthStrMap[monthName];
  var endDay   = monthEndDays[monthName];

  // Gap-fill: merge target month with +/-1 month window to fill no-data holes
  var prevDate = ee.Date(year + '-' + monthStr + '-01').advance(-1, 'month');
  var nextDate = ee.Date(year + '-' + monthStr + '-' + endDay).advance(1, 'month');

  var s1Core = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(year + '-' + monthStr + '-01', year + '-' + monthStr + '-' + endDay)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .select('VV');

  var s1Fill = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(prevDate, nextDate)
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .select('VV');

  // Primary: target month median. Fallback: 3-month window median for gap pixels
  var s1Primary  = s1Core.median();
  var s1Fallback = s1Fill.median();
  var s1 = s1Primary.unmask(s1Fallback).clip(geom);  // fills no-data holes

  // Clamp threshold: GMM must not exceed -15.5 dB (prevents under-detection)
  var clampedThreshold = Math.min(threshold, -15.5);

  // Terrain mask using publicly available layers only
  // Strategy: pixel is "flat enough for water" if ANY of these are true:
  //   (a) JRC GSW has ever recorded water here (occurrence > 0)
  //   (b) SRTM slope ≤ 8° (relaxed from v2's 10° but still permissive for delta)
  //   (c) JRC GSW seasonality > 0 (ever wet)
  // This avoids the unavailable HAND asset entirely.
  var jrc = ee.Image('JRC/GSW1_4/GlobalSurfaceWater');
  var jrcOccurrence  = jrc.select('occurrence').unmask(0);
  var jrcSeasonality = jrc.select('seasonality').unmask(0);
  var slope = ee.Terrain.slope(ee.Image('CGIAR/SRTM90_V4')).clip(geom);

  // Include pixel if: slope ≤ 8° OR was ever historically wet per JRC
  var flatMask = slope.lte(8).or(jrcOccurrence.gt(0)).or(jrcSeasonality.gt(0));

  return s1.lte(clampedThreshold).and(flatMask);
}

/* ================== S1 GREY BACKGROUND HELPER ================== */
function addS1Background(geom, year) {
  var s1Bg = ee.ImageCollection('COPERNICUS/S1_GRD')
    .filterBounds(geom)
    .filterDate(year + '-01-01', year + '-12-31')
    .filter(ee.Filter.eq('instrumentMode', 'IW'))
    .select('VV')
    .median()
    .clip(geom);
  Map.addLayer(s1Bg, { min: -25, max: 0 }, 'S1 VV Median', true);
}

/* -------------------- Export Format Options -------------------- */
var exportFormats = ['Multi-band (Single File)', 'Single-band Split (13 Files)', 'Single-band with ColorMap'];
var multiBandMonthlyImage = null;
var multiBandOccurrenceImage = null;
var lastExportYear = null;

/* -------------------- Color Palettes -------------------- */
var occurrenceColors = ['#F7FBFF', '#CFEFF6', '#93CFE0', '#5EA6C1', '#2E7A9A', '#174F80', '#08306B'];

/* -------------------- Map settings -------------------- */
Map.setOptions('ROADMAP');

/* ==================== UI ==================== */
var mainPanel = ui.Panel({
  style: {
    position: 'top-right', padding: '6px', backgroundColor: '#ffffff',
    color: '#000000', width: '550px', height: '680px', border: '1px solid #d0d0d0'
  },
  layout: ui.Panel.Layout.flow('vertical')
});

function greyRow() {
  return ui.Panel({
    layout: ui.Panel.Layout.flow('vertical'),
    style: { width: '100%', backgroundColor: '#ececec', padding: '2px 3px', margin: '3px 0' }
  });
}
function contentRow() {
  return ui.Panel({ layout: ui.Panel.Layout.flow('horizontal'), style: { width: '100%' } });
}

var selectStyle = { color: 'black', fontSize: '13px', padding: '2px 3px', margin: '2px' };
var buttonStyle = { backgroundColor: '#f3f3f3', color: 'black', fontSize: '13px', padding: '4px 6px', border: '0px' };

// Title
var titleRow = greyRow();
titleRow.add(ui.Label('SAR Surface Water Explorer — Bangladesh (Dynamic GMM EM)', { fontWeight: 'bold', fontSize: '14px', margin: '2px' }));
mainPanel.add(titleRow);

// Division / District
var regionRow = greyRow();
var regionContent = contentRow();
var divisionSelect = ui.Select({
  items: divisions.aggregate_array('ADM1_NAME').getInfo().sort(),
  placeholder: 'Division', style: selectStyle
});
var districtSelect = ui.Select({ items: [], placeholder: 'District', style: selectStyle });
divisionSelect.style().set({ width: '250px', margin: '2px' });
districtSelect.style().set({ width: '250px', margin: '2px' });
regionContent.add(divisionSelect);
regionContent.add(districtSelect);
regionRow.add(regionContent);
mainPanel.add(regionRow);

// Result box
var resultRow = ui.Panel({
  layout: ui.Panel.Layout.flow('horizontal'),
  style: { width: '100%', backgroundColor: '#ececec', padding: '2px 3px', margin: '3px 0' }
});
resultRow.add(ui.Label('Result', { width: '140px' }));
var resultBox = ui.Label('', { width: '440px' });
resultRow.add(resultBox);

// Monthly row
var monthlyRow = greyRow();
var monthlyContent = contentRow();
var yearSelect = ui.Select({ items: yearList, value: '2023', style: selectStyle });
var monthsWithTotal = Object.keys(monthMap).slice(); monthsWithTotal.push('Total Occurrence');
var monthSelect = ui.Select({ items: monthsWithTotal, placeholder: 'Month/Total', style: selectStyle });
var monthlyBtn = ui.Button({ label: 'Monthly Surface Water', style: buttonStyle });
yearSelect.style().set({ width: '150px', margin: '2px' });
monthSelect.style().set({ width: '150px', margin: '2px' });
monthlyBtn.style().set({ width: '170px', margin: '2px' });
monthlyContent.add(yearSelect); monthlyContent.add(monthSelect); monthlyContent.add(monthlyBtn);
monthlyRow.add(monthlyContent);
mainPanel.add(monthlyRow);

// Change detection row
var changeRow = greyRow();
var changeContent = contentRow();
var visYear1 = ui.Select({ items: yearList, value: '2019', style: selectStyle });
var visYear2 = ui.Select({ items: yearList, value: '2023', style: selectStyle });
var visMonthSelect = ui.Select({ items: Object.keys(monthMap), placeholder: 'Month', style: selectStyle });
var changeBtn = ui.Button({ label: 'Change Intensity', style: buttonStyle });
visYear1.style().set({ width: '120px', margin: '2px' });
visYear2.style().set({ width: '120px', margin: '2px' });
visMonthSelect.style().set({ width: '100px', margin: '2px' });
changeBtn.style().set({ width: '140px', margin: '2px' });
changeContent.add(visYear1); changeContent.add(visYear2); changeContent.add(visMonthSelect); changeContent.add(changeBtn);
changeRow.add(changeContent);
mainPanel.add(changeRow);

// Seasonal row
var seasonRow = greyRow();
var seasonContent = contentRow();
var seasonalYear = ui.Select({ items: yearList, value: '2023', style: selectStyle });
var seasonSelect = ui.Select({
  items: ['Dry Winter (Dec–Feb)', 'Pre-Monsoon (Mar–May)', 'Monsoon (Jun–Sep)', 'Post-Monsoon (Oct–Nov)'],
  placeholder: 'Season', style: selectStyle
});
var seasonalBtn = ui.Button({ label: 'Seasonal Variance', style: buttonStyle });
seasonalYear.style().set({ width: '130px', margin: '2px' });
seasonSelect.style().set({ width: '180px', margin: '2px' });
seasonalBtn.style().set({ width: '130px', margin: '2px' });
seasonContent.add(seasonalYear); seasonContent.add(seasonSelect); seasonContent.add(seasonalBtn);
seasonRow.add(seasonContent);
mainPanel.add(seasonRow);

// Actions row
var actionsRow = greyRow();
var actionsContent = contentRow();
var genChartBtn = ui.Button({ label: 'Generate Chart', style: buttonStyle });
var geoBtn = ui.Button({ label: 'GeoTIFF Download', style: buttonStyle });
var aboutBtn = ui.Button({ label: 'About', style: buttonStyle });
var resetBtn = ui.Button({ label: 'Reset', style: buttonStyle });
genChartBtn.style().set({ width: '140px', margin: '2px' });
geoBtn.style().set({ width: '160px', margin: '2px' });
aboutBtn.style().set({ width: '100px', margin: '2px' });
resetBtn.style().set({ width: '100px', margin: '2px' });
actionsContent.add(genChartBtn); actionsContent.add(geoBtn); actionsContent.add(aboutBtn); actionsContent.add(resetBtn);
actionsRow.add(actionsContent);
mainPanel.add(actionsRow);

// Export row
var exportRow = greyRow();
var exportContent = contentRow();
exportContent.add(ui.Label('Export Format:', { fontSize: '12px', margin: '4px 4px 4px 2px' }));
var exportFormatSelect = ui.Select({ items: exportFormats, value: 'Multi-band (Single File)', style: selectStyle });
exportFormatSelect.style().set({ width: '200px', margin: '2px' });
exportContent.add(exportFormatSelect);
exportContent.add(ui.Label('Resolution:', { fontSize: '12px', margin: '4px 4px 4px 8px' }));
var resolutionSelect = ui.Select({ items: ['10m', '30m', '100m'], value: '10m', style: selectStyle });
resolutionSelect.style().set({ width: '70px', margin: '2px' });
exportContent.add(resolutionSelect);
exportRow.add(exportContent);
mainPanel.add(exportRow);

mainPanel.add(resultRow);

var chartPanel = ui.Panel({
  style: {
    width: '100%', height: '200px', padding: '6px 6px 0 6px',
    backgroundColor: '#fff', border: '1px solid #e8e8e8', margin: '6px 0 0 0'
  },
  layout: ui.Panel.Layout.flow('vertical')
});
mainPanel.add(chartPanel);

/* -------------------- Legends -------------------- */
function makeOccurrenceRamp(title, colors) {
  var p = ui.Panel({
    style: { position: 'bottom-left', padding: '6px', backgroundColor: 'rgba(255,255,255,0.95)', border: '1px solid rgba(0,0,0,0.15)' }
  });
  p.add(ui.Label(title, { fontWeight: 'bold' }));
  var ramp = ui.Panel({ layout: ui.Panel.Layout.Flow('horizontal'), style: { margin: '6px 0 0 0' } });
  colors.forEach(function(c) {
    ramp.add(ui.Label('', { width: '18px', height: '12px', margin: '0 1px 0 0', backgroundColor: c }));
  });
  var wrapper = ui.Panel({ layout: ui.Panel.Layout.Flow('horizontal') });
  wrapper.add(ramp);
  wrapper.add(ui.Label('Low → High', { margin: '6px 0 0 6px', fontSize: '11px' }));
  p.add(wrapper);
  return p;
}
var legendS1 = makeOccurrenceRamp('Occurrence', occurrenceColors);

function makeLegendPanel(title, entries) {
  var p = ui.Panel({
    style: { position: 'bottom-left', padding: '6px', backgroundColor: 'rgba(255,255,255,0.95)', border: '1px solid rgba(0,0,0,0.15)' }
  });
  p.add(ui.Label(title, { fontWeight: 'bold' }));
  entries.forEach(function(e) {
    var r = ui.Panel({ layout: ui.Panel.Layout.flow('horizontal') });
    r.add(ui.Label('', { width: '14px', height: '12px', margin: '0 6px 0 0', backgroundColor: e.color }));
    r.add(ui.Label(e.label));
    p.add(r);
  });
  return p;
}
var legendChange = makeLegendPanel('Change Intensity', [
  { color: '#FF0000', label: 'Lost' },
  { color: '#0000FF', label: 'Stable' },
  { color: '#00FF00', label: 'Gained' }
]);

function hideAllLegends() {
  try { Map.remove(legendS1); } catch(e) {}
  try { Map.remove(legendChange); } catch(e) {}
}

/* -------------------- Region Helpers -------------------- */
function drawRegionBoundaryOnly(regionFeat, label) {
  var styled = ee.FeatureCollection([ee.Feature(regionFeat)]).style({
    color: 'FF0000', width: 3, fillColor: '00000000'
  });
  Map.addLayer(styled, {}, label || 'Boundary', true);
}

function getRegionFeature(selDistrict) {
  return {
    feature: districts.filter(ee.Filter.eq('ADM2_NAME', selDistrict)).first(),
    name: selDistrict + '_District'
  };
}

divisionSelect.onChange(function(v) {
  if (!v) { districtSelect.items().reset([]); return; }
  districtSelect.items().reset(
    districts.filter(ee.Filter.eq('ADM1_NAME', v))
      .aggregate_array('ADM2_NAME').getInfo().sort()
  );
  var divFeat = divisions.filter(ee.Filter.eq('ADM1_NAME', v)).first();
  Map.clear(); Map.add(mainPanel);
  drawRegionBoundaryOnly(divFeat, v + ' Division');
  Map.centerObject(divFeat.geometry(), 8);
});

districtSelect.onChange(function(v) {
  if (!v) return;
  var distFeat = districts.filter(ee.Filter.eq('ADM2_NAME', v)).first();
  Map.clear(); Map.add(mainPanel);
  drawRegionBoundaryOnly(distFeat, v + ' District');
  Map.centerObject(distFeat.geometry(), 9);
});

/* ==================== MAIN LOGIC ==================== */

/* ---------- Monthly Surface Water ---------- */
function runMonthly() {
  chartPanel.clear(); hideAllLegends(); resultBox.setValue('');
  var selDist = districtSelect.getValue();
  var selYear = yearSelect.getValue();
  var selMonth = monthSelect.getValue();

  if (!selDist) { resultBox.setValue('[!] Select a District first.'); return; }
  if (!selMonth) { resultBox.setValue('[!] Select a Month or Total Occurrence.'); return; }

  var regionInfo = getRegionFeature(selDist);
  var geom = regionInfo.feature.geometry();
  lastExportYear = selYear;

  var refMonth = (selMonth === 'Total Occurrence') ? 'August' : selMonth;

  resultBox.setValue('Computing Dynamic GMM threshold...');

  computeDynamicThreshold(geom, selYear, refMonth, function(threshold) {
    resultBox.setValue('GMM Threshold: ' + threshold.toFixed(2) + ' dB — Rendering...');

    Map.clear(); Map.add(mainPanel);
    Map.centerObject(geom, 9);

    addS1Background(geom, selYear);

    if (selMonth === 'Total Occurrence') {
      var occ = ee.Image(0);
      Object.keys(monthMap).forEach(function(m) {
        occ = occ.add(buildWaterMask(regionInfo.feature, selYear, m, threshold).unmask(0));
      });
      multiBandOccurrenceImage = occ;
      Map.addLayer(occ.updateMask(occ.gt(0)), { min: 1, max: 12, palette: occurrenceColors }, 'GMM Occurrence ' + selYear);
      Map.add(legendS1);
      resultBox.setValue('OK: Total Occurrence | Threshold: ' + threshold.toFixed(2) + ' dB [' + selDist + ']');
    } else {
      var water = buildWaterMask(regionInfo.feature, selYear, selMonth, threshold);

      var areaStats = water.multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(),
        geometry: geom,
        scale: 250,
        bestEffort: true
      });
      areaStats.evaluate(function(stats, err) {
        if (err || !stats) {
          resultBox.setValue('Threshold: ' + threshold.toFixed(2) + ' dB | Area: (compute error) [' + selDist + ']');
          return;
        }
        var areaKm2 = (stats['VV'] || 0) / 1e6;
        resultBox.setValue(
          'Threshold: ' + threshold.toFixed(2) + ' dB | Water Area: ' + areaKm2.toFixed(2) + ' km² [' + selDist + ']'
        );
      });

      Map.addLayer(water.updateMask(water), { palette: ['0000FF'] }, 'GMM Water ' + selMonth + ' ' + selYear);

      chartPanel.clear();
      // Use 3-month window for gap-filled histogram in chart
      var s1Img = ee.ImageCollection('COPERNICUS/S1_GRD')
        .filterBounds(geom)
        .filterDate(
          ee.Date(selYear + '-' + monthStrMap[selMonth] + '-01').advance(-1, 'month'),
          ee.Date(selYear + '-' + monthStrMap[selMonth] + '-' + monthEndDays[selMonth]).advance(1, 'month')
        )
        .filter(ee.Filter.eq('instrumentMode', 'IW'))
        .select('VV').median().clip(geom);
      var histChart = ui.Chart.image.histogram({
        image: s1Img, region: geom, scale: 150, minBucketWidth: 0.5
      }).setOptions({
        title: 'SAR VV Histogram — ' + selDist + ' (' + selMonth + ' ' + selYear + ')',
        hAxis: { title: 'Backscatter (dB)', viewWindow: { min: -30, max: 0 } },
        vAxis: { title: 'Pixel Count' },
        series: { 0: { color: 'steelblue' } }
      });
      chartPanel.add(histChart);
      chartPanel.add(ui.Label('▲ GMM Threshold: ' + threshold.toFixed(2) + ' dB', { fontSize: '11px', color: 'red' }));
    }

    drawRegionBoundaryOnly(regionInfo.feature, regionInfo.name);
  });
}

/* ---------- Change Detection ---------- */
function runChange() {
  chartPanel.clear(); hideAllLegends(); resultBox.setValue('');
  var selDist = districtSelect.getValue();
  var y1 = visYear1.getValue();
  var y2 = visYear2.getValue();
  var m = visMonthSelect.getValue();

  if (!selDist || !m) { resultBox.setValue('[!] Select District and Month.'); return; }

  var regionInfo = getRegionFeature(selDist);
  var geom = regionInfo.feature.geometry();

  resultBox.setValue('Computing GMM threshold for Year 1 (' + y1 + ')...');

  computeDynamicThreshold(geom, y1, m, function(threshold1) {
    resultBox.setValue('Computing GMM threshold for Year 2 (' + y2 + ')...');

    computeDynamicThreshold(geom, y2, m, function(threshold2) {
      var mask1 = buildWaterMask(regionInfo.feature, y1, m, threshold1);
      var mask2 = buildWaterMask(regionInfo.feature, y2, m, threshold2);

      var changeClass = ee.Image(0)
        .where(mask1.and(mask2.not()), 1)   // Lost (Red)
        .where(mask1.and(mask2), 2)          // Stable (Blue)
        .where(mask2.and(mask1.not()), 3)    // Gained (Green)
        .toUint8();

      Map.clear(); Map.add(mainPanel);

      addS1Background(geom, y2);

      Map.addLayer(
        changeClass.updateMask(changeClass.gt(0)),
        { min: 1, max: 3, palette: ['FF0000', '0000FF', '00FF00'] },
        'Change ' + y1 + '→' + y2 + ' [' + m + ']'
      );
      Map.add(legendChange);

      drawRegionBoundaryOnly(regionInfo.feature, regionInfo.name);
      Map.centerObject(geom, 9);

      resultBox.setValue(
        'Change: T1=' + threshold1.toFixed(2) + ' dB | T2=' + threshold2.toFixed(2) + ' dB [' + selDist + ']'
      );
    });
  });
}

/* ---------- Seasonal Analysis ---------- */
function runSeasonal() {
  chartPanel.clear(); hideAllLegends(); resultBox.setValue('');
  var selDist = districtSelect.getValue();
  var y = seasonalYear.getValue();
  var s = seasonSelect.getValue();

  if (!selDist || !s) { resultBox.setValue('[!] Select District and Season.'); return; }

  var regionInfo = getRegionFeature(selDist);
  var geom = regionInfo.feature.geometry();

  var seasonMonths = {
    'Dry Winter (Dec–Feb)':   ['December', 'January', 'February'],
    'Pre-Monsoon (Mar–May)':  ['March', 'April', 'May'],
    'Monsoon (Jun–Sep)':      ['June', 'July', 'August', 'September'],
    'Post-Monsoon (Oct–Nov)': ['October', 'November']
  };

  var months = seasonMonths[s];
  var refMonth = months[Math.floor(months.length / 2)];

  resultBox.setValue('Computing GMM threshold for ' + s + '...');

  computeDynamicThreshold(geom, y, refMonth, function(threshold) {
    var union = ee.Image(0);
    months.forEach(function(m) {
      union = union.max(buildWaterMask(regionInfo.feature, y, m, threshold).unmask(0));
    });

    Map.clear(); Map.add(mainPanel);

    addS1Background(geom, y);

    Map.addLayer(union.updateMask(union), { palette: ['0000FF'] }, s + ' ' + y);

    drawRegionBoundaryOnly(regionInfo.feature, regionInfo.name);
    Map.centerObject(geom, 9);

    resultBox.setValue(
      'Seasonal: ' + s + ' | Threshold: ' + threshold.toFixed(2) + ' dB [' + selDist + ']'
    );
  });
}

/* ---------- Generate Chart ---------- */
function runGenerateChart() {
  chartPanel.clear(); resultBox.setValue('');
  var selDist = districtSelect.getValue();
  var selYear = yearSelect.getValue();

  if (!selDist) { resultBox.setValue('[!] Select a District first.'); return; }

  var regionInfo = getRegionFeature(selDist);
  var geom = regionInfo.feature.geometry();

  resultBox.setValue('Computing GMM threshold for chart...');

  computeDynamicThreshold(geom, selYear, 'August', function(threshold) {
    resultBox.setValue('Building monthly water area chart...');

    var monthNames = Object.keys(monthMap);
    var areaList = [];
    var processed = 0;

    monthNames.forEach(function(m) {
      var water = buildWaterMask(regionInfo.feature, selYear, m, threshold);
      var areaStats = water.multiply(ee.Image.pixelArea()).reduceRegion({
        reducer: ee.Reducer.sum(),
        geometry: geom,
        scale: 250,
        bestEffort: true
      });
      areaStats.evaluate(function(stats, err) {
        var area = (!err && stats && stats['VV']) ? stats['VV'] / 1e6 : 0;
        areaList.push({ month: m, area: area });
        processed++;
        if (processed === monthNames.length) {
          areaList.sort(function(a, b) { return monthMap[a.month] - monthMap[b.month]; });
          var labels = areaList.map(function(d) { return d.month.substring(0, 3); });
          var values = areaList.map(function(d) { return d.area; });

          chartPanel.clear();
          var chart = ui.Chart.array.values({ array: ee.Array(values), axis: 0, xLabels: labels })
            .setChartType('ColumnChart')
            .setOptions({
              title: 'Monthly Water Area — ' + selDist + ' (' + selYear + ')',
              hAxis: { title: 'Month' },
              vAxis: { title: 'Water Area (km²)' },
              colors: ['#2171b5'],
              legend: { position: 'none' }
            });
          chartPanel.add(chart);
          resultBox.setValue(
            'Chart ready | Threshold: ' + threshold.toFixed(2) + ' dB [' + selDist + ']'
          );
        }
      });
    });
  });
}

/* ---------- GeoTIFF Export ---------- */
function runExport() {
  var selDist = districtSelect.getValue();
  var selYear = yearSelect.getValue();
  var selMonth = monthSelect.getValue();
  var resStr = resolutionSelect.getValue();
  var scale = parseInt(resStr.replace('m', ''), 10);

  if (!selDist) { resultBox.setValue('[!] Select a District for export.'); return; }
  if (!selMonth) { resultBox.setValue('[!] Select a Month for export.'); return; }

  var regionInfo = getRegionFeature(selDist);
  var geom = regionInfo.feature.geometry();
  var refMonth = (selMonth === 'Total Occurrence') ? 'August' : selMonth;

  resultBox.setValue('Computing GMM threshold for export...');

  computeDynamicThreshold(geom, selYear, refMonth, function(threshold) {
    if (selMonth === 'Total Occurrence') {
      var occ = ee.Image(0);
      Object.keys(monthMap).forEach(function(m) {
        occ = occ.add(buildWaterMask(regionInfo.feature, selYear, m, threshold).unmask(0));
      });
      Export.image.toDrive({
        image: occ,
        description: 'GMM_Occurrence_' + selDist + '_' + selYear,
        region: geom,
        scale: scale,
        fileFormat: 'GeoTIFF'
      });
      resultBox.setValue('Export task submitted: Total Occurrence GeoTIFF');
    } else {
      var water = buildWaterMask(regionInfo.feature, selYear, selMonth, threshold);
      Export.image.toDrive({
        image: water.toUint8(),
        description: 'GMM_Water_' + selDist + '_' + selMonth + '_' + selYear,
        region: geom,
        scale: scale,
        fileFormat: 'GeoTIFF'
      });
      resultBox.setValue('Export task submitted: ' + selMonth + ' ' + selYear + ' GeoTIFF');
    }
  });
}

/* ==================== Wire Buttons ==================== */
monthlyBtn.onClick(runMonthly);
changeBtn.onClick(runChange);
seasonalBtn.onClick(runSeasonal);
genChartBtn.onClick(runGenerateChart);
geoBtn.onClick(runExport);
aboutBtn.onClick(function() {
  alert('SAR Surface Water Explorer — Bangladesh v4\nDynamic GMM EM (No CSV required)\nv4: HAND replaced with JRC GSW + SRTM slope, null guards on area stats.');
});
resetBtn.onClick(function() {
  chartPanel.clear(); hideAllLegends(); resultBox.setValue('');
  Map.clear(); Map.add(mainPanel); Map.centerObject(bdBoundary, 7);
});

Map.add(mainPanel);
Map.centerObject(bdBoundary, 7);
