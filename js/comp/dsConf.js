/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

/* Dataset specific overrides */

var ocean = ocean || {};

ocean.sliderdownloadlink = '';

var location_missing_msg = "Please click on the map to select a location.";

function override(paramsfunc) {
    return function () {
        /* default parameters */
        out = {
            dataset: getBackendId(ocean.datasetid),
            variable: getBackendId(ocean.datasetid, ocean.variable),
            plot: ocean.plottype,
            date: $.datepick.formatDate('yyyymmdd', ocean.date),
            period: ocean.period,
            area: ocean.area,
            timestamp: $.now()
        };

        if (paramsfunc) {
            $.extend(out, paramsfunc(ocean.dataset));
        }

        return out;
    };
}

ocean.dsConf = {
    reynolds: {
        params: override(function (dataset) { return {
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        beforeSend: function() {
            valid = true;
            if (!ocean.date) {
                valid = false;
            }
            return valid; 
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            if (ocean.variable == 'sstanom' &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data);
            }
            else if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: null,
        onDeselect: function() {
            resetMap();
            resetLegend();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
        },
        onRegionChange: function() {}
    },
    ersst: {
        params: override(function (dataset) { return {
            baseYear: 1950,
            average: dataset.aveCheck.average,
            trend: dataset.aveCheck.trend,
            runningAve: dataset.aveCheck.runningAve,
            runningInterval: dataset.runningInterval
        };}),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        aveCheck: {},
        mainCheck: 'average',
        runningInterval: 2,
        callback: function(data) {
            prependOutputSet();

            if (ocean.variable == 'sstanom' &&
                this.aveCheck.average && data.aveImg != null)
            {
                appendOutput(data.aveImg, data.aveData,
                             "Average(1981-2010)",
                             Math.round(data.mean*100)/100 + '\u00B0C',
                             data
                             );

            }
            else if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: null,
        onDeselect: function() {
            resetMap();
            resetLegend();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
        },
        onRegionChange: function() {}


    },
    bran: {
        params: override(function (dataset) {
            switch (ocean.plottype) {
              case 'xsections':
                  return { lat: $('#latitude').val(),
                           lon: $('#longitude').val() };
                  break;

              default:
                  return {};
            }

            return params;
        }),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            var plottype = ocean.plottype;
            if ((["salt", "temp"].indexOf(variable) != -1) && (["xsections"].indexOf(plottype) != -1)){
                valid = isLocationPointValid();
                if (!valid){
                    text = location_missing_msg;
                }
            }

            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid;
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img != null) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: null,
        onDeselect: function() {
            resetMap();
            resetLegend();
        }, 
        onVariableChange: function(){
            selectMonthsForNearRealTimeDatasets();
        },
        onRegionChange: function() {}
    },
    ww3: {
        params: override(function (dataset) { return {
            lllat: $('#latitude').val(),
            lllon: $('#longitude').val(),
            urlat: $('#latitude').val(),
            urlon: $('#longitude').val(),
            step: $('#hour').val()
        };}),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            if (["atlas"].indexOf(variable) == -1 && ocean.dataset.params().plot != 'map') { //All variables under ww3 except wave atlas
                valid = isLocationPointValid();
                if (!valid){
                    text = location_missing_msg;
                }
            }

            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid;
        },
        callback: function(data) {
            prependOutputSet();
            periodStr = ocean.dataset.params()["period"];

            if (periodStr == "monthly"){
                if(data.ext != null) {
                    appendOutput(data.img, data.ext);
                }
            } else if  (periodStr == "hourly"){
              if (data.img != null && data.scale != null){
                    prependOutputSet();
                    appendOutput(data.img, null, null, null, data);
                    updateMap(data.mapimg);
                    setLegend(data.scale);
                }
            }
        },
        onSelect: function(){
            $('#plottype').change();
            showSpanForControl('month');
        },
        onDeselect: null, 
        onVariableChange: function(){},
        onRegionChange: function() {}

    },
    ww3forecast: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime + 'UTC');
                    //display local time
                    var dt = forecast[this.getStep()[0] - 1].datetime
                    var local = getLocalTime(dt);
                    $('.slider-hint').text(local.toString());
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
        },
        onVariableChange: function() {
            updatePage();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:''
    },
    waveatlas: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
        },
        onSelect: function(){
            if (ocean.variable == 'atlas'){
                hideControls('plottype');
                hideControls('dataset');
                hideControls('period');

                ocean.dsConf.ww3.overlay = new L.FeatureGroup();

                //Read file
                $.getScript( "js/comp/data_points_to_load.js")

                  .done(function( script, textStatus ) {
                    //Load the markers
                    for (var i = 0; i < points.length; i++) {
                        var marker = new L.marker([points[i][1],points[i][2]])
                                    .bindPopup("<b>Location: "+points[i][0] + "</b><br>" + "<a href=http://gsd.spc.int/wacop/" + points[i][4].trim() + " target=_blank>See wave climate report</a>");
                        ocean.dsConf.ww3.overlay.addLayer(marker);
                    }
                    return false;
                  })

                  .fail(function( jqxhr, settings, exception ) {
                    fatal_error("Failed to load location points to show WACOP wave atlas report.");
                  });

                ocean.mapObj.addLayer(ocean.dsConf.ww3.overlay);

                if (map.hasLayer(map.intersecMarker)){
                    disableIntersecMarker();
                }
            }
        },
        onDeselect: function(){
            if (map.hasLayer(ocean.dsConf.ww3.overlay)){
                ocean.mapObj.removeLayer(ocean.dsConf.ww3.overlay);
            }
        },
        onVariableChange: function(){},
        onRegionChange: function() {}

    },
    tideforecast: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
            ocean.dsConf.tideforecast.overlay = new L.FeatureGroup();

            //Current year
            year_0 = (new Date()).getFullYear();
            year_1 = year_0 + 1;
            year_2 = year_1 + 1;

            //Load the markers
            base_pdf_url = "http://www.bom.gov.au/ntc/IDO59001/IDO59001_";
            high_tide_content = ""
            low_tide_content = ""

            points = data;

            for (var key in points){
                var point = points[key];

                web_url =  "http://www.bom.gov.au/australia/tides/#!/offshore-" + point.short_name.trim();
                pdf_url_0 =  base_pdf_url  + year_0 + "_" + point.station_number.trim() + ".pdf";
                pdf_url_1 =  base_pdf_url  + year_1 + "_" + point.station_number.trim() + ".pdf";
                pdf_url_2 =  base_pdf_url  + year_2 + "_" + point.station_number.trim() + ".pdf";

                if (point.high_tide_time && point.current_time){
                    nextHighTide = point.high_tide_time - point.current_time;
                    high_hour = Math.floor(nextHighTide/(60*60));
                    high_min = Math.floor((nextHighTide % (60 * 60)) / 60);
                    high_tide_content = "Next high tide in: <b>" + high_hour + "  hrs " + high_min + "  min ("+ point.high_tide_height + " m)</b><br>";
                }

                if (point.low_tide_time && point.current_time){
                    nextLowTide = point.low_tide_time - point.current_time;
                    low_hour = Math.floor(nextLowTide/(60*60));
                    low_min = Math.floor((nextLowTide % (60 * 60)) / 60);
                    low_tide_content =  "Next low tide in: <b>" + low_hour + "  hrs " + low_min + "  min (" + point.low_tide_height + " m)</b><br>";
                }

                popup_content = "<h4>"+ key + "</h4>"
                       + high_tide_content
                       + low_tide_content
                       + "<br>Tide forecast reports:<br>"
                       + "<a href=" + pdf_url_0 + " target=_blank>" + year_0 + "</a>  "
                       + "<a href=" + pdf_url_1 + " target=_blank>" + year_1 + "</a>  "
                       + "<a href=" + pdf_url_2 + " target=_blank>" + year_2 + "</a>" + "<br><br>"
                       + "<a href=" + web_url + " target=_blank>Go to Tide Prediction website</a>";

                var marker = new L.marker(point.latlng).bindPopup(popup_content);
                ocean.dsConf.tideforecast.overlay.addLayer(marker);
            }

            ocean.mapObj.addLayer(ocean.dsConf.tideforecast.overlay);
        },
        onSelect: function(){
            if (ocean.variable == 'tide'){
                hideControls('plottype');
                hideControls('dataset');
                hideControls('period');

                if (map.hasLayer(map.intersecMarker)){
                    disableIntersecMarker();
                }
            }

            updatePage();
        },
        onDeselect: function(){
            hideSpanForControl('date');
            if (map.hasLayer(ocean.dsConf.tideforecast.overlay)){
                ocean.mapObj.removeLayer(ocean.dsConf.tideforecast.overlay);
            }
        },
        onVariableChange: function(){
            hideControls('period');
        },
        onRegionChange: function() {}

    },
    msla: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function(){
            valid = true;
            return valid;
        },
        callback: function(data) {
            if (data.img != null && data.scale != null){
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            showSpanForControl('date');
        },
        onDeselect: function(){
            resetMap();
            resetLegend();
        },
        onVariableChange: function() {
        },
        onRegionChange: function() {}
    },
    poamasla: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime);
                    $('.slider-hint').text('');
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }
                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
        },
        onVariableChange: function() {
            updatePage();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:''
    },
    poamassta: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.downloadimg = data.img;
                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[this.getStep()[0] - 1].datetime);
                    $('.slider-hint').text('');
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }

                    if (data.scale) {
                        data.scale = data.scale.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        setLegend(data.scale);
                    }
                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        updateMap(data.mapimg);
                    }

                    if (data.scale) {
                        data.scale = data.scale.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
                        setLegend(data.scale);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
        },
        onVariableChange: function() {
            updatePage();
        },
        onRegionChange: function() {
            this.updateDownloadImg();
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
                 this.selectedRegion = ocean.area;
             }
        },
        selectedRegion: ocean.area,
        downloadimg:''
    },
    currentforecast: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if(data.forecast) {
                var forecast = $.parseJSON(data.forecast);
                this.mapimg = data.mapimg;
                this.downloadimg = data.img;

                slider.options.steps = forecast.length;
                slider.options.snap = true;
                slider.stepRatios = slider.calculateStepRatios();
                slider.options.animationCallback = function(x, y) {
                    $('.handle-text').text(forecast[Math.round(this.getStep()[0]) - 1].datetime  + 'UTC');//Math.round is to fix a problem found when getStep returns somthing like 30.000000000000004.
                    //display local time
                    var dt = forecast[this.getStep()[0] - 1].datetime
                    var local = getLocalTime(dt);
                    $('.slider-hint').text(local.toString());
//                    if (data.mapimg) {
//                        ocean.dataset.mapimg = data.mapimg;
                        ocean.dataset.updateMapImg();
//                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
//                        if self.selectedRegion !== ocean.area
//                        bounds = $('#subregion option:selected').data('bounds');
//                        updateMap(data.mapimg, bounds);
//                    }

                      //Sets the download image link for the datasets having slider option.
                      ocean.dataset.updateDownloadImg();
                };
                slider.options.callback = function(x, y) {
                    if (data.mapimg) {
                        ocean.dataset.updateMapImg();
//                        data.mapimg = data.mapimg.replace(/_\d\d/, '_' + pad(this.getStep()[0] - 1, 2));
//                        updateMap(data.mapimg);
                    }

                    //Sets the download image link for the datasets having slider option.
                    ocean.dataset.updateDownloadImg();
                };
                slider.value.prev = [-1, -1];
                slider.animate(false, true);
                setLegend(data.scale);
            }
            prependOutputSet();

            if(data.ext != null) {
                appendOutput(data.img, data.ext);
            }
        },
        onSelect: function() {
            updatePage();
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
        },
        onVariableChange: function() {
            updatePage();
        },
        updateMapImg: function() {
            mapimg = this.mapimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
            if (!this.selectedRegion) {
                this.selectedRegion = ocean.area;
            }
            if (this.selectedRegion !== ocean.area) {
                mapimg = mapimg.replace('_' + this.selectedRegion, '_' + ocean.area);
                this.mapimg = mapimg;
                this.selectedRegion = ocean.area;
            }
            bounds = $('#subregion option:selected').data('bounds');
            if ($('#subregion option:selected').val() === 'pac') {
                bounds = null;
            }
            updateMap(mapimg, bounds);
        },
        onRegionChange: function() {
            this.updateDownloadImg();
            this.updateMapImg(this.mapimg);
        },
        updateDownloadImg:  function() {
             if (typeof(this.downloadimg) != 'undefined') {
                 img = this.downloadimg.replace(/_\d\d/, '_' + pad((Math.round(slider.getStep()[0]) - 1), 2));
                 img = img.replace('_' + this.selectedRegion, '_' + ocean.area);
                 this.downloadimg = img;
                 ocean.sliderdownloadlink = img;
             }
        },
        selectedRegion: ocean.area,
        mapimg: '',
        downloadimg:''
    },
    sealevel: {
        params: override(function (dataset) { return {
            lat: $('#latitude').val(),
            lon: $('#longitude').val(),
            tidalGaugeId: $('#tgId').val()
        };}),
        beforeSend: function() {
            valid = true;
            var text = "";
            var variable = getBackendId(ocean.datasetid, ocean.variable);
            if (ocean.plottype === "ts") {
                if (["rec", "alt"].indexOf(variable) != -1) {
                    valid = isLocationPointValid();
                    if (!valid){
                        text = location_missing_msg;
                    }
                }
                else if (ocean.variable === "gauge" && $('#tgId').val().trim() === "") {
                    text = "Please select a tide gauge from the map.";
                    valid = false;
                }
            }
            if (text != ""){
                show_feedback(text, "Missing Input:");
                return valid;
            }

            return valid; 
        },
        callback: function(data) {
            prependOutputSet();

            if (data.img) {
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
            }

            if (data.tidimg)
                appendOutput(data.tidimg, data.tidtxt, "Tide Gauge");

            if (data.altimg)
                appendOutput(data.altimg, data.alttxt, "Altimetry");

            if (data.recimg)
                appendOutput(data.recimg, data.rectxt, "Reconstruction");

            setLegend(data.scale);
        },
        selectTideGauge: function(){
            seaLevelModel.selectTideGuage(feature.properties.ID)
        },
        onSelect: function() {
            var seaLevelModel = new $.SeaLevelModel();
            if (ocean.variable != 'gauge') {
                return;
            }
            $.when(
                seaLevelModel.getData()
            ).done(function(tideGauges) { 
                ocean.dsConf.sealevel.overlay = L.geoJson(tideGauges.features, {
                    style: function(feature) {
                        return {color: '#000'};
                    },
                    onEachFeature: function(feature, layer) {
                        layer.bindPopup('<b>' + feature.properties.Description + ' (' + feature.properties.ID + ')</b> <br/><p>' + 'Latitude: ' + feature.geometry.coordinates[1] + ' Longitude: ' + feature.geometry.coordinates[0] + '</p>');
                        layer.on('popupopen', function() {
                            $("#tidalgauge").val(feature.properties.Description);
                            $("#tgId").val(feature.properties.ID);
                        });
                        layer.on('popupclose', function() {
                            $("#tidalgauge").val('');
                            $("#tgId").val('');
                        });
                    },
                    filter: function(feature, layer) {
                        return feature.properties.Region == ocean.configProps.tidalGaugeRegions;
                    }
                }).addTo(map)
            }).fail(function() {
                fatal_error("Failed to load tide gauges.");
            });

//
 //                   $('#tidalgauge').val('');
  //                  $('#tgId').val('');
   //                 $('#latitude').val('');
    //                $('#longitude').val('');
        },
        onDeselect: function() {
//            var control;
            if (map.hasLayer(ocean.dsConf.sealevel.overlay)) {
                map.removeLayer(ocean.dsConf.sealevel.overlay);
            }
            resetLegend();
//            var controls = map.getControlsByClass(
//                'OpenLayers.Control.SelectFeature');

//            for (control in controls) {
//                map.removeControl(controls[control]);
//                controls[control].deactivate();
//                controls[control].destroy();
//            }
        }, 
        onVariableChange: function(){
            resetMap();
            resetLegend();
        },
        onRegionChange: function() {}

    },
    coral: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
            updateInfo(data.dial, 'Alert level');

        },
        onSelect: null,
        onDeselect: function() {
            resetMap();
            resetLegend();
            updateInfo(null, '');
        }, 
        onVariableChange: function(){
            resetMap();
            resetLegend();
            updateInfo(null, '');
        },
        onRegionChange: function() {
            resetMap();
            updateInfo(null, '');
        }
    },
    chlorophyll: {
        params: override(function (dataset) { return {
            };
        }),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }

        },
        onSelect: function() {
            if ($('#tunafishing').parent('.fishery').size() == 1) {
                showControls('tunafishing');
            }
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            if ($('#tunafishing').parent('.fishery').size() == 1) {
                hideControls('tunafishing');
            }
        }, 
        onVariableChange: function(){},
        onRegionChange: function() {}
    },
    convergence: {
        params: override(function (dataset) { return {
        };}),
        beforeSend: function() {
            valid = true;
            return valid; 
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
        },
        onSelect: function() {
            showControls('tunafishing');
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
            hideControls('tunafishing');
        }, 
        onVariableChange: function(){
            updateDatasetForSST();
        },
        onRegionChange: function(){
            updateDatasetForSST();
        }
    },
    mur: {
        params: override(function (dataset) { return {
        };}),
        beforeSend: function() {
            valid = true;
            return valid;
        },
        callback: function(data) {
            if (data.img != null && data.scale != null) {
                prependOutputSet();
                appendOutput(data.img, null, null, null, data);
                updateMap(data.mapimg);
                setLegend(data.scale);
            }
            if (data.mapimg) {
                this.mapimg = data.mapimg;
                ocean.dataset.updateMapImg();
            }
        },
        onSelect: function() {
        },
        onDeselect: function() {
            resetMap();
            resetLegend();
        },
        updateMapImg: function() {
            bounds = $('#subregion option:selected').data('bounds');
            if ($('#subregion option:selected').val() === 'pac') {
                bounds = null;
            }
            updateMap(this.mapimg, bounds);
        },
        onVariableChange: function(){
            updateDatasetForSST();
        },
        onRegionChange: function(){
            resetMap();
            updateDatasetForSST();
        }
    }

};

function appendOutput(image, dataURL, name, extras, data){
    var captionText = ""
    if (dataURL) {
        captionText = "<a class='download-data' href=" + dataURL+ " target='_blank'><span class='ui-icon ui-icon-arrowreturnthick-1-s'></span>Download Data</a>"
    }
    if (extras) {
        captionText = captionText + extras
    }
    //Check if the img is already in the gallery. If not, then add the img.
    var index = -1;
    if (fotorama.data){
        for (var i=0; i<fotorama.data.length; i++){
            if (fotorama.data[i].img == image){
                index = i;
                i = fotorama.data.length;
            }
        }
    }

    if (index == -1){
        fotorama.push({img: image, caption: captionText});
    }

    if (fotorama.size > 20) {//TODO extract 20 to the config
        fotorama.shift();
    }

    if (index == -1){
        fotorama.show(fotorama.size - 1);
    } else {
        fotorama.show(index);
    }

    if (name) {
        $('<h2>', {
            text: name
        }).appendTo(captionText);
    }

    if (data) {
        updateMap(data);
    }
}

/**
 * Pad number with leading zeros
 * https://gist.github.com/aemkei/1180489
 */
function pad(a,b){
    return([1e15]+a).slice(-b)
}

function updateInfo(image, altText){
    if (image != null) {
        $('#additionalInfoDiv').empty().append($('<img>', {src: image, alt: altText}));
    }
    else {
        $('#additionalInfoDiv').empty();
    }
}


/**
 * Opens the download image link in a new window for the datasets having slider option.
 */
function openDownloadImageLink(){
    if (ocean.sliderdownloadlink != ""){
        appendOutput(ocean.sliderdownloadlink);
    }
}


/**
 * Merge the Reynolds daily sst product in fisheries with the MUR.
 * http://tuscany/redmine/issues/729
 */

function updateDatasetForSST(){
    if (getValue('region') == 'pac'){
        addOption('dataset', 'convergence', 'Reynolds');
        ocean.variable = 'mean';
    } else { //for subregions
        addOption('dataset', 'mur', 'MUR');
        ocean.variable = 'mursst';
    }

    //Updates the available date.
    updateDatepicker();
}

//gets local time
function getLocalTime(dt){
    //Example datetime string
    //"26-01-2015 12:00"
    local = new Date(dt.slice(6,10),dt.slice(3,5)-1,dt.slice(0,2),dt.slice(11,13),dt.slice(14));
    var hourOffset = local.getTimezoneOffset() / 60;
    local.setHours(local.getHours() - hourOffset);
    return local;
}

function isLocationPointValid(){
    var valid = true;
    if (($('#latitude').val().trim() === "") || ($('#longitude').val().trim() === "")){
        valid = false;
    }

    return valid;
}