/*jslint eqeq: true, forin: true, plusplus: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
ocean.controls = [
    'plottype',
    'period',
    'datepicker',
    'month',
    'year',
    'tidalgauge',
    'latitude',
    'longitude',
    'dataset' /* always last */
];

ocean.compare = { limit: 24 };
ocean.processing = false;
ocean.dateFormat = 'yyyymmdd';
ocean.date = new Date();

/* set up JQuery UI elements */
$(document).ready(function() {

    /* initialise jQueryUI elements */
    // $('#controlPanel :enabled').attr('disabled', 'disabled');
    $('.dialog').dialog({
        autoOpen: false,
        resizable: false
    });
    $('button').button();

    $('#enlargeDiv').hide();
    hideControls();

    /* set up the loading dialog */
    $('#loading-dialog').dialog('option', { 'modal': true,
                                            'dialogClass': 'notitle',
                                            'closeOnEscape': false,
                                            'height': 55,
                                            'resizable': false });

    /* UI handlers */
    $('#submit').click(function () {
        console.log("CLICKED");
    });

    /* Variable */
    $('#variable').change(function () {
        var varid = $('#variable option:selected').val();
        console.log('variable:', varid);

        if (varid == '--') {
            hideControls();
            return;
        }

        /* filter the options list */
        var plots = ocean.variables[varid].plots;
        console.log("plots", plots);

        filterOpts('plottype', plots);
        selectFirstIfRequired('plottype');
        showControl('plottype');
    });

    /* Plot Type */
    $('#plottype').change(function () {
        var varid = $('#variable option:selected').val();
        var plottype = $('#plottype option:selected').val();

        console.log('plottype:', plottype);

        /* filter the period list */
        var periods = ocean.variables[varid].plots[plottype];
        console.log(periods);

        filterOpts('period', periods);
        selectFirstIfRequired('period');
        showControl('period');
        showControl('dataset');

        switch (plottype) {
            case 'xsections':
            case 'histogram':
            case 'waverose':
                showControl('latitude');
                showControl('longitude');
                addPointLayer();
                break;

            default:
                hideControl('latitude');
                hideControl('longitude');
                removePointLayer();
                break;
        }
    });

    /* Period */
    $('#period').change(function () {
        var varid = $('#variable option:selected').val();
        var plottype = $('#plottype option:selected').val();
        var period = $('#period option:selected').val();

        console.log('period:', period);

        /* FIXME: consider exposing these in CSS ? */
        /* period specific date controls */
        switch (period) {
            case 'daily':
                showControl('datepicker');
                hideControl('month');
                hideControl('year');
                break;

            default:
                hideControl('datepicker');
                showControl('month');
                showControl('year');
                break;
        }

        /* plot specific date controls */
        switch (plottype) {
            case 'histogram':
            case 'waverose':
                hideControl('year');
                break;

            default:
                /* pass */
                break;
        }
    });

    /* Date range is changed */
    $('#datepicker, #month, #year').change(function () {
        var varid = $('#variable option:selected').val();
        var plottype = $('#plottype option:selected').val();
        var period = $('#period option:selected').val();

        console.log('Update datasets');

        /* FIXME: rank these */
        var datasets = ocean.variables[varid].plots[plottype][period];

        console.log(datasets);

        /* clear previous choices */
        $('#dataset option').remove();

        $.each(datasets, function (i, dataset) {
            $('<option>', {
                value: dataset,
                text: ocean.datasets[dataset].name
            }).appendTo('#dataset');
        });

        selectFirstIfRequired('dataset');
    });

    /* show the tidal gauge name in the title text */
    $('#tidalgauge').hover(function () {
        /* copy the value into the title */
        this.title = this.value;
    });

    $.getJSON('config/comp/datasets.json')
        .success(function(data) {
            var dialog = $('#about-datasets');

            ocean.datasets = {};
            ocean.variables = {};

            $.each(data, function(i, dataset) {
                /* Add to the datasets dialog */
                $('<h1>', { text: dataset.name }).appendTo(dialog);

                var ul = $('<ul>').appendTo(dialog);

                ocean.datasets[dataset.id] = dataset;

                $.each(dataset.variables, function(k, variable) {
                    $('<li>', { text: variable.name }).appendTo(ul);

                    if (!ocean.variables[variable.id]) {
                        ocean.variables[variable.id] = {
                            name: variable.name,
                            plots: {}
                        };
                    }

                    $.each(variable.plottypes, function(k, plottype) {
                        if (!ocean.variables[variable.id].plots[plottype]) {
                            ocean.variables[variable.id].plots[plottype] = {};
                        }

                        $.each(variable.periods, function(k, period) {
                            if (!ocean.variables[variable.id].plots[plottype][period]) {
                                ocean.variables[variable.id].plots[plottype][period] = [];
                            }

                            ocean.variables[variable.id].plots[plottype][period].push(dataset.id);
                        });
                    });
                });

            });

            /* FIXME: hardcoded groupings */
            var groupings = {
                meansst: 'sst',
                sstanom: 'sst',
                sstdec: 'sst',
                Hs: 'waves',
                Tm: 'waves',
                Dm: 'waves',
                alt: 'sealevel',
                rec: 'sealevel',
                gauge: 'sealevel',
                eta: 'sealevel',
                uvtemp: 'currents',
                uveta: 'currents',
                salt: 'salinity'
            }

            $.each(ocean.variables, function (k, v) {
                var parent_;

                if (k in groupings) {
                    parent_ = $('#variable optgroup#' + groupings[k]);

                    if (parent_.length == 0) {
                        parent_ = varcombo;
                    }
                } else {
                    parent_ = ('#variable');
                }

                $('<option>', {
                    text: v.name,
                    value: k
                }).appendTo(parent_);
            });
        })
        .error(function() {
            // FIXME
            console.log("ERROR");
        });

});

Date.prototype.getMonthString = function() {
    var calMonth = String(this.getMonth() + 1);
    return (calMonth < 10) ?  ('0' + calMonth) : calMonth;
};

function prependOutputSet()
{
    while ($('#outputDiv div.outputgroup').length >= ocean.compare.limit) {
        $('#outputDiv div.outputgroup:last').remove();
    }

    var div = $('<div>', {
        'class': 'outputgroup'
    }).prependTo($('#outputDiv'));

    /* remove button */
    $('<span>', {
        'class': 'close-button ui-icon ui-icon-close',
        title: "Remove",
        click: function () {
            /* if this is the selected layer, switch back to Bathymetry */
            if (div.find(':checked').length > 0) {
                /* remove this now, so that selectMapLayer() disables
                 * appropriately */
                div.find(':checked').remove();
                /* select a new layer in case it isn't disabled */
                $('.outputgroup input[type=radio]:first')
                    .attr('checked', 'checked')
                    .change();
                selectMapLayer("Bathymetry");
            }

            div.fadeTo('fast', 0);
            div.slideUp('fast', function () {
                div.remove();
            });
        }
    }).appendTo(div);

    $('<p>', {
        'class': 'date',
        text: new Date().toLocaleTimeString()
    }).appendTo(div);


    /* scroll to the top of the output div */
    $('#outputDiv').animate({ scrollTop: 0 }, 75);
}

function createOutput(image, dataURL, name, extras, data)
{
    var div = $('<div>', {
        'class': 'thumbnail'
    });

    if (name) {
        $('<h2>', {
            text: name
        }).appendTo(div);
    }

    if (data) {
        $('<input>', {
            type: 'radio',
            name: 'outputLayer',
            title: "Set as map layer",
            checked: true
        })
        .appendTo(div)
        .change(function () {
            updateMap(data);
        });
    }

    var a = $('<a>', {
        'class': 'raster',
        href: image,
        title: "Click to open in a new window",
        target: '_blank'
    }).appendTo(div);

    var img = $('<img>', {
        src: image + '?' + $.param({ time: $.now() })
    }).appendTo(a);

    div.hide();
    img.load(function () {
        /* this kludge is required for IE7, where it turns out you can't do
         * slideDown on a block contained in a relative positioned parent
         * unless that block has a defined height */
        if ($.browser.msie && $.browser.version == '7.0')
            div.css('height', div.height());

        div.slideDown();
    });

    img.hover(
        function (e) {
            enlargeImg(this, true);
        },
        function (e) {
            enlargeImg(this, false);
        });

    $('<div>', {
        'class': 'overlay ui-icon ui-icon-newwin'
    }).appendTo(div);

    if (dataURL)
        $('<a>', {
            'class': 'download-data',
            href: dataURL,
            target: '_blank',
            html: '<span class="ui-icon ui-icon-arrowreturnthick-1-s"></span>Download Data'
        }).appendTo(div);

    if (extras)
        $('<span>', {
            html: extras
        }).appendTo(div);

    return div;
}

function appendOutput()
{
    createOutput.apply(null, arguments).appendTo($('#outputDiv .outputgroup:first'));
}

function prependOutput()
{
    createOutput.apply(null, arguments).prependTo($('#outputDiv .outputgroup:first'));
}

function filterOpts(select, keys) {
    var select = $('#' + select);

    if (!keys) {
        console.warn("filterOpts was provided no keys for " + select);
        select.find('optgroup, option').show();
        return;
    }

    select.find('optgroup').hide();
    select.find('option').each(function () {
        var opt = $(this);

        if (opt.val() in keys) {
            opt.parent('optgroup').show();
            opt.show();
        } else {
            opt.hide();
        }
    });
}

function selectFirstIfRequired(comboid) {
    var combo = $('#' + comboid);

    if (combo.find('option:selected:visible').length == 0) {
        combo.find('option:visible:first').attr('selected', true);
        combo.change();
    }
}

function addPointLayer () {
    var layer = new OpenLayers.Layer.Vector("point-layer",
        {
            wrapDateLine: true,
            style: {
                graphicName: 'cross',
                pointRadius: 10,
                stroke: false
            },
            preFeatureInsert: function(feature) {
                this.removeAllFeatures();
            },
            onFeatureInsert: function(feature) {
                var geometry = feature.geometry;
                var lon = Math.round(geometry.x * 1000) / 1000;
                var lat = Math.round(geometry.y * 1000) / 1000;

                /* correct for wrapping issues from OpenLayers */
                if (lon < -180)
                    lon += 360;

                $('#latitude').val(lat);
                $('#longitude').val(lon);
            }
        });

    ocean.mapObj.addLayer(layer);

    this.panelControls = [
        new OpenLayers.Control.DrawFeature(layer,
            OpenLayers.Handler.Point, {
                displayClass: 'olControlDrawFeaturePoint',
                title: "Select a point on the map"
            }),
        new OpenLayers.Control.Navigation({
                title: "Zoom and pan the map"
            })
    ];

    this.toolbar = new OpenLayers.Control.Panel({
        displayClass: 'olControlEditingToolbar',
        defaultControl: this.panelControls[0],
        div: document.getElementById('mapControlsToolbar')
    });

    this.toolbar.addControls(this.panelControls);
    ocean.mapObj.addControl(this.toolbar);

    /* track changes to the lat/lon and move the feature */
    $('#latitude, #longitude').change(function () {
        var lat = $('#latitude').val();
        var lon = $('#longitude').val();

        layer.removeAllFeatures();

        if (lat != '' && lon != '')
            layer.addFeatures([
                new OpenLayers.Feature.Vector(
                    new OpenLayers.Geometry.Point(lon, lat))
            ]);
    });

    /* update the map with the initial lat/lon */
    $('#latitude').change();
}

function removePointLayer () {
    var layers = map.getLayersByName("point-layer");

    if (layers.length == 0)
        return;

    for (layer in layers) {
        map.removeLayer(layers[layer]);
    }

    if (this.toolbar) {
        map.removeControl(this.toolbar);
        this.toolbar.deactivate();
        this.toolbar.destroy();
    }

    for (control in this.panelControls) {
        map.removeControl(this.panelControls[control]);
        this.panelControls[control].deactivate();
        this.panelControls[control].destroy();
    }

    /* remove event handlers */
    $('#latitude, #longitude').unbind();

    this.toolbar = null;
    this.panelControls = null;
}

function enlargeImg(img, show) {
    var enlargeDiv = $('#enlargeDiv');

    if (show) {
        enlargeDiv.stop(true, true);
        $('#enlargeDiv img').remove();
        var eimg = $('<img>', {
            src: img.src,
            'class' : 'imagepreview'
        }).appendTo(enlargeDiv);

        /* fix broken positioning in IE7 */
        if ($.browser.msie && $.browser.version == '7.0') {
            var eimgraw = eimg.get(0);

            var offset = eimg.offset();
            eimg.offset({
                top: offset.top + enlargeDiv.height() / 2 - eimgraw.height / 2,
                left: offset.left + enlargeDiv.width() / 2 - eimgraw.width / 2
            });
        }

        enlargeDiv.fadeIn(100);
        enlargeDiv.show();
    }
    else {
        enlargeDiv.stop(true, true);
        enlargeDiv.delay(100);
        enlargeDiv.fadeOut(150, function () {
            enlargeDiv.html('');
            enlargeDiv.hide();
        });
    }
}

function createCheckBoxes(store, records, result, operation, eOpt) {
    data = [];
    records = store.getById('reynolds').variables().getById('anom').get('average').checkboxes; 
    Ext.each(records, function(rec) {
        var name = rec.name;
        ocean.dsConf['reynolds'].aveCheck[name] = false; 
        Ext.create('Ext.form.field.Checkbox', {
            boxLabel: rec.boxLabel,
            renderTo: 'toggleDiv',
            width: 155,
            name: name,
            id: rec.name,
            handler: function(checkbox, checked) {
                if (checkbox.id == ocean.dataset.mainCheck) {
                    var checkboxId;

                    ocean.dataset.aveCheck[checkbox.id] = checked;
                    this.setValue(checked);
                    for (checkboxId in (ocean.dataset.aveCheck)) {
                        if( checkboxId != checkbox.id) {
                            var checkboxCmp = Ext.getCmp(checkboxId);
                            checkboxCmp.setDisabled(!checked);
                            checkboxCmp.setValue(ocean.dataset.aveCheck[checkboxId]);
                        }
                    }

                    var periodCombo = Ext.getCmp('periodCombo');
                    periodCombo.clearValue();
                    var store = periodCombo.store;
                    store.clearFilter(true);
                    if(checked) {
                        store.filter([avePeriodFilter]);
                    }
                    else {
                        store.filter([periodFilter]);
                    }
                    if (store.find('id', ocean.period) != -1) {
                        periodCombo.select(ocean.period);
                    }
                    else {
                        periodCombo.select(store.data.keys[0]);
                        ocean.period = store.data.keys[0];
                    } 
////                    updateCalDiv();
                }
                else {
                    ocean.dsConf['reynolds'].aveCheck[checkbox.id] = checked;
                    for (checkboxId in ocean.dsConf['reynolds'].aveCheck) {
                        if( checkboxId != checkbox.id && checkboxId != ocean.dsConf['reynolds'].mainCheck) {
                            checkboxCmp = Ext.getCmp(checkboxId);
//                            checkboxCmp.setDisabled(!checked);
                            if (checked) {
                                ocean.dsConf['reynolds'].aveCheck[checkboxId] = !checked;
                                checkboxCmp.setValue(!checked);
                            }
                        }
                    }

                }
            },
            listeners: {
                'beforeshow' : function(event, args) {
                    if (this.id == ocean.dsConf['reynolds'].mainCheck) {
                        this.setValue(ocean.dsConf['reynolds'].aveCheck[this.id]);
                    }
                    else {
                        if (ocean.dsConf['reynolds'].aveCheck[ocean.dsConf['reynolds'].mainCheck]){
                            this.setValue(ocean.dsConf['reynolds'].aveCheck[this.id]);
                        }
                        else {
                            this.setDisabled(true);
//                            Ext.getCmp('runningAveSlider').setDisabled(true);
                        }
                    }
                }
            }
        });
    });

    dataArray = new Array();

    var i;
    for (i=0; i<records.length; i++) {
        thisItem = new Array();
        thisItem["boxLabel"] = records[i].boxLabel;
        thisItem["name"] = records[i].name;
        dataArray.push(thisItem);
    }

    return data;
}

function selectDataset(event, args) {
    var selection = event.getValue();
    var record = ocean.datasets.getById(selection);
    ocean.dsConf[selection].setData(record);

    if (ocean.dataset != null) {
        ocean.dataset.onDeselect();
    }

    ocean.dataset = ocean.dsConf[selection];
    $('#dstitle').html(record.get('title'));
    $('#dshelp').html('About File');
    $('#dshelp').attr('href', record.get('help'));
    varCombo = Ext.getCmp('variableCombo');
    varCombo.setDisabled(false);
    varCombo.bindStore(record.variables());
    varCombo.clearValue();

    selectMapLayer("Bathymetry");
    ocean.dataset.onSelect();
}

function configCalendar() {
    if(ocean.calendar) {
        var dateRange = ocean.dataset.data.get('dateRange');
        var minDate = ocean.dataset.data.get('dateRange').minDate;
        ocean.calendar.datepick('option', {'minDate': dateRange.minDate,
                                           'maxDate': dateRange.maxDate,
                                           'yearRange': dateRange.minYear + ":" + dateRange.maxYear
                                });
    }
    else {
        createCalendars();
    }
}

//Lazy creation of datepick and month and year combobox.
function createCalendars() {
    var dateRange = ocean.dataset.data.get('dateRange');
    var minDate = ocean.dataset.data.get('dateRange').minDate;

    ocean.calendar = $("#datepicker").datepick({
        minDate: dateRange.minDate,
        maxDate: dateRange.maxDate,
        yearRange: dateRange.minYear + ":" + dateRange.maxYear,
        dateFormat: ocean.dateFormat,
        firstDay: 1,
        showTrigger: '#calImg',
        renderer: $.extend({},
                  $.datepick.weekOfYearRenderer,
                      {picker: $.datepick.defaultRenderer.picker.
                      replace(/\{link:clear\}/, '').
                      replace(/\{link:close\}/, '')
                   }),
        showOtherMonths: true,
        onSelect: function (dateObj) {
            ocean.date = dateObj.length? dateObj[0] : null
        },
        showOnFocus: false
    });
    $( "#datepicker" ).mousedown(function() {
        $(this).datepick('show');
    });
}

function selectVariable(event, args) {
    var selection = event.getValue();
    var record = ocean.dataset.data.variables().getById(selection);
    ocean.dataset.variable = record;
    ocean.dataset.selectVariable(selection);

}

function selectPeriod(event, args) {
    if (event.getValue() != null) {
        ocean.period = event.getValue();
        updateCalDiv();
    }
}

function range(start, end) {
    var rangeArray = [];
    while(start <= end){
        rangeArray.push(start++);
    }
    return rangeArray
}

function updateYearCombo(yearFilter) {
    var yearCombo = Ext.getCmp('yearCombo');
    //yearCombo.setAutoScroll('auto');
//    yearCombo.getPicker().setAutoScroll(true);
    yearCombo.clearValue();
    var store = yearCombo.store;
    store.clearFilter(true);
    store.filter([yearFilter]);
//    yearCombo.picker.height = 300;
//    yearCombo.updateLayout();
    //yearCombo.getPicker().doComponentLayout();
//    yearCombo.doComponentLayout();
}

function updatePeriodCombo() {
    var periodCombo = Ext.getCmp('periodCombo');
    periodCombo.clearValue();
    var store = periodCombo.store;
    store.clearFilter(true);
    store.filter([periodFilter]);
    if (store.find('id', ocean.period) != -1) {
        periodCombo.setValue(ocean.period)
    }
    else {
        periodCombo.setValue(store.data.keys[0])
    } 
}

function updateCalDiv() {
    if (ocean.period == 'daily' || ocean.period == 'weekly') {
        showControl('datepickerDiv');
        hideControl('yearMonthDiv');
        $("#datepicker").datepick('setDate', new Date(ocean.date));
    }
    else {
        hideControl('datepickerDiv');
        showControl('yearMonthDiv');

        if (ocean.period == 'yearly')
            hideControl('monthDiv');
        else /* monthly, 3 monthly, 6 monthly */
            showControl('monthDiv');

        ocean.monthCombo.select(ocean.date.getMonthString());
        ocean.yearCombo.select(ocean.date.getFullYear());
    }
}

function selectRunningInterval(slider, value, thumb, args) {
    ocean.dataset.runningInterval = value;
}

function _controlVarParent(control) {
    return $('#' + control).parent('.controlvar');
}

function _showhideControlGroups() {
}

/*
 * showControl:
 *
 * Shows a div.controlvar based on the id of the field within it.
 */
function showControl(control) {
    var parent = _controlVarParent(control);

    parent.show();
    parent.parent('.controlgroup').show();

    $('#' + control).change();
}

function hideControl(control) {
    var parent = _controlVarParent(control)
    var group = parent.parent('.controlgroup');

    parent.hide();

    /* hide control group if required */
    if (group.children('.controlvar:visible').length == 0) {
        group.hide();
    }
}

function hideControls() {
    $.each(ocean.controls, function (i, control) {
        hideControl(control);
    });
}

function updatePage() {
    if (!ocean.processing) {

        if (!ocean.dataset)
            return;

        if (!ocean.dataset.variable)
            return;

        function show_error(params, text)
        {
            var url = 'cgi/portal.py?' + $.param(params);

            $('#error-dialog-content').html(text);
            $('#error-dialog-request').prop('href', url);
            $('#error-dialog').dialog('open');
        }

        $.ajax({
            url: 'cgi/portal.py',
            data: ocean.dataset.params(),
            dataType: 'json',
            beforeSend: function(jqXHR, settings) {
                ocean.processing = true;
                $('#loading-dialog').dialog('open');
                $('#error-dialog').dialog('close');
            },
            success: function(data, textStatus, jqXHR) {
                if (data == null || $.isEmptyObject(data))
                {
                    show_error(ocean.dataset.params(), "returned no data");
                }
                else
                {
                    if (data.error)
                        show_error(ocean.dataset.params(), data.error);
                    else
                        ocean.dataset.callback(data);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == 'parsererror')
                    show_error(ocean.dataset.params(),
                               "Unable to parse server response.");
                else
                    show_error(ocean.dataset.params(), errorThrown);
            },
            complete: function(jqXHR, textStatus) {
                ocean.processing = false;
                $('#loading-dialog').dialog('close');
            }
        });
    }
}
