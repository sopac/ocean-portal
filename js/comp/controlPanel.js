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
    'date',
    'month',
    'year',
    'tidalgauge',
    'latitude',
    'longitude',
    'dataset',
    'dshelp'
];

ocean.compare = { limit: 24 };
ocean.processing = false;
ocean.date = new Date();

/* set up JQuery UI elements */
$(document).ready(function() {

    hideControls();

    /* set up the date picker */
    $(".datepicker").datepicker({
        dateFormat: 'd MM yy',
        changeMonth: true,
        changeYear: true
    }).mousedown(function() {
        $(this).datepicker('show');
    });

    /* UI handlers */
    $('#submit').click(function () {
        updatePage();

        return false; /* don't propagate event */
    });

    /* Variable */
    $('#variable').change(function () {
        var varid = getValue('variable');

        if (varid == '--') {
            hideControls();
            ocean.variable = null;
            return;
        }

        if (!(varid in ocean.variables)) {
            return;
        }

        updateVisibilities('variable', ocean.variable, varid)
        ocean.variable = varid;

        /* filter the options list */
        var plots = ocean.variables[varid].plots;

        filterOpts('plottype', plots);
        showControls('plottype');
        selectFirstIfRequired('plottype');

        selectMapLayer("Bathymetry");
    });

    /* Plot Type */
    $('#plottype').change(function () {
        var plottype = getValue('plottype');

        if (!(plottype in ocean.variables[ocean.variable].plots)) {
            return;
        }

        updateVisibilities('plottype', ocean.plottype, plottype);
        ocean.plottype = plottype;

        /* filter the period list */
        var periods = ocean.variables[ocean.variable].plots[plottype];

        filterOpts('period', periods);
        showControls('period');
        selectFirstIfRequired('period');

        /* plot specific controls -
         * Note: do not call showControls or hideControls here, control
         * visibility based on plottype should be specified in controlvars.css
         */
        switch (plottype) {
            case 'xsections':
            case 'histogram':
            case 'waverose':
            case 'ts':
                if (ocean.variable == 'gauge') {
                    /* really the default case */
                    removePointLayer();
                    break;
                }

                addPointLayer();
                break;

            default:
                removePointLayer();
                break;
        }

        selectMapLayer("Bathymetry");
    });

    /* Period */
    $('#period').change(function () {
        var period = getValue('period');

        if (!(period in ocean.variables[ocean.variable].plots[ocean.plottype])) {
            return;
        }

        updateVisibilities('period', ocean.period, period)
        ocean.period = period;

        showControls('dataset');

        /* FIXME: is this strictly correct? it would collapse for datasets
         * with holes in them. That's fine for the year combo, but not the
         * datepicker */
        var range = getCombinedDateRange();

        if ($('#year').is(':visible')) {
            /* populate year */
            var year = $('#year');

            year.find('option').remove();

            for (y = range.min.getFullYear();
                 y <= range.max.getFullYear();
                 y++) {
                $('<option>', {
                    value: y,
                    text: y
                }).appendTo(year);
            }

            var y = ocean.date.getFullYear();

            if (y < range.min.getFullYear()) {
                selectFirstIfRequired('year');
            } else if (y > range.max.getFullYear()) {
                year.find('option:last').attr('selected', true);
                year.change();
            } else {
                setValue('year', y);
            }
        } else if ($('#month').is(':visible')) {
            /* if year is shown, we populate month based on the selected year
             * (see below) */
            updateMonths();
        } else if ($('#date').is(':visible')) {
            var date_ = $('#date');

            /* set range on datepicker */
            date_.datepicker('option', {
                minDate: range.min,
                maxDate: range.max,
                yearRange: range.min.getFullYear() + ':' + range.max.getFullYear()
            });

            /* automatically clamps the date to the available range */
            date_.datepicker('setDate', ocean.date).change();
        } else {
            /* datasets are not date dependent */
            updateDatasets();
        }
    });

    /* Year */
    $('#year').change(function () {
        /* populate month */
        var range = getCombinedDateRange();

        /* calculate the possible month range */
        var selectedyear = getValue('year');
        var minMonth = null;
        var maxMonth = null;

        if (selectedyear == range.min.getFullYear()) {
            minMonth = range.min.getMonth();
        } else if (selectedyear == range.max.getFullYear()) {
            maxMonth = range.max.getMonth();
        }

        updateMonths(minMonth, maxMonth);
    });

    /* Date range is changed */
    $('#date, #month, #year').change(function () {

        if (!(ocean.variable in ocean.variables) ||
            !(ocean.plottype in ocean.variables[ocean.variable].plots) ||
            !(ocean.period in ocean.variables[ocean.variable].plots[ocean.plottype])) {
            return;
        }

        /* determine the chosen date */
        var date_;

        switch (ocean.period) {
            case 'daily':
            case 'weekly':
                date_ = $('#date').datepicker('getDate');
                break;

            case 'monthly':
            case '3monthly':
            case '6monthly':
            case '12monthly':
            case 'yearly':
                var year = getValue('year') || 0;
                var month = getValue('month') || 0;

                date_ = new Date(year, month, 1);
                break;

            default:
                console.error("ERROR: should not be reached");
                break;
        }

        if (!date_ ||
            isNaN(date_.getTime())) {
            return;
        }

        ocean.date = date_;

        var filter;

        if ($('#date').is(':visible') || $('#year').is(':visible')) {
            filter = function(dataset) {
                var range = getDateRange(dataset, ocean.variable, ocean.period);

                if (!range)
                    return true; /* no date range defined */

                return (ocean.date >= range.min) && (ocean.date <= range.max);
            };
        }

        updateDatasets(filter);
    });

    /* Dataset */
    $('#dataset').change(function () {
        var datasetid = getValue('dataset');

        if (!datasetid || datasetid == ocean.datasetid) {
            return;
        }

        ocean.datasetid = datasetid;

        var backendid = getBackendId(datasetid);

        if (!(backendid in ocean.dsConf)) {
            return;
        }

        if (ocean.dataset && ocean.dataset.onDeselect) {
            ocean.dataset.onDeselect();
        }

        ocean.dataset = ocean.dsConf[backendid];

        /* update about file */
        showControls('dshelp');
        $('#dshelp').attr('href', ocean.datasets[datasetid].help);
        $('#dshelp span').html(ocean.datasets[datasetid].name);

        if (ocean.dataset.onSelect) {
            ocean.dataset.onSelect();
        }
    });

    /* show the tidal gauge name in the title text */
    $('#tidalgauge').hover(function () {
        /* copy the value into the title */
        this.title = this.value;
    });

    var groupings = {};

    /* load JSON configuration */
    $.when(
        /* Load and parse vargroups.json */
        $.getJSON('config/comp/vargroups.json').success(function(data) {
            $.each(data, function(k, v) {
                $('<optgroup>', {
                    id: k,
                    label: v.name
                }).appendTo('#variable');

                $.each(v.vars, function(i, var_) {
                    groupings[var_] = k;
                });
            });
        }),

        /* Load and parse datasets.json */
        $.getJSON('config/comp/datasets.json').success(function(data) {
            ocean.datasets = {};
            ocean.variables = {};

            $.each(data, function(i, dataset) {
                ocean.datasets[dataset.id] = dataset;

                $.each(dataset.variables, function(k, variable) {
                    if (!ocean.variables[variable.id]) {
                        ocean.variables[variable.id] = {
                            name: variable.name,
                            plots: {},
                            variable: variable
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
        })
    )
    /* Successfully fetched all JSON */
    .done(function() {
        $.each(ocean.variables, function (k, v) {
            var parent_;

            if (k in groupings) {
                parent_ = $('#variable optgroup#' + groupings[k]);

                if (parent_.length == 0) {
                    parent_ = $('#variable');
                }
            } else {
                parent_ = $('#variable');
            }

            $('<option>', {
                text: v.name,
                value: k
            }).appendTo(parent_);
        });
    })

    /* Failed to load some JSON */
    .fail(function() {
        fatal_error("Failed to load portal configuration.");
    });

});

/**
 * getBackendId:
 * @datasetid: a dataset frontend id
 * @varid: optional variable frontend id
 *
 * Get the backend id for a given frontend id.
 *
 * Returns: the backend id for the given frontend id
 */
function getBackendId(datasetid, varid) {
    var dataset = ocean.datasets[datasetid];

    if (varid) {
        var variable = $.grep(dataset.variables, function (var_) {
            return (var_.id == varid);
        });

        if (variable.length == 1 && 'bid' in variable[0]) {
            return variable[0].bid;
        } else {
            return ocean.variables[varid].variable.id;
        }
    } else {
        if ('bid' in dataset) {
            return dataset.bid;
        } else {
            return dataset.id;
        }
    }
}

/**
 * getDateRange:
 *
 * Get the date range for a variable.
 *
 * Returns: { minDate, maxDate }
 */
function getDateRange(datasetid, varid, period)
{
    var dataset = ocean.datasets[datasetid];
    var variable = $.grep(dataset.variables, function (var_) {
        return (var_.id == varid);
    });
    var range;
    var month_delta = 0;

    /* multi-month periods decrease the available start date range */
    switch (period) {
        case '3monthly':
            month_delta = 2;
            break;
        case '6monthly':
            month_delta = 5;
            break;
        case '12monthly':
            month_delta = 11;
            break;
    }

    if (variable.length == 1 && 'dateRange' in variable[0]) {
        range = variable[0].dateRange;
    /* else use the dataset dateRange */
    } else if ('dateRange' in dataset) {
        range = dataset.dateRange;
    } else {
        return null;
    }

    /* 'yy' is correct, believe it or not, see
     * http://docs.jquery.com/UI/Datepicker/parseDate */
    var mindate = $.datepicker.parseDate('yymmdd', range.minDate);
    var maxdate = $.datepicker.parseDate('yymmdd', range.maxDate);

    mindate.setMonth(mindate.getMonth() + month_delta);

    return { min: mindate, max: maxdate };
}

/**
 * getCombinedDateRange:
 *
 * Gets the combined date ranges for all of the selected datasets.
 *
 * Returns: minDate: maxDate
 */
function getCombinedDateRange() {
    var datasets = ocean.variables[ocean.variable].plots[ocean.plottype][ocean.period];
    var minDate = Number.MAX_VALUE;
    var maxDate = Number.MIN_VALUE;

    $.each(datasets, function(i, datasetid) {
        var range = getDateRange(datasetid, ocean.variable, ocean.period);

        if (!range)
            return; /* continue */

        minDate = Math.min(minDate, range.min);
        maxDate = Math.max(maxDate, range.max);
    });
    return ( min: new Date(minDate), max: new Date() };
/*    return { min: new Date(minDate), max: new Date(maxDate) };
}

/**
 * updateMonths:
 *
 * Update the months displayed in the months combo.
 */
function updateMonths(minMonth, maxMonth) {
    var selectedyear = getValue('year') || 0;
    var fmt;

    if (minMonth == null) {
        minMonth = 0;
    }

    if (maxMonth == null) {
        maxMonth = 11;
    }

    function _dateRange(year, range) {
        range -= 1;

        if ($('#year').is(':visible')) {
            return function (m) {
                return $.datepicker.formatDate('M y',
                        new Date(selectedyear, m - range)) + ' &ndash; ' +
                    $.datepicker.formatDate('M y',
                        new Date(selectedyear, m));
            }
        } else {
            return function (m) {
                return $.datepicker.formatDate('M',
                        new Date(selectedyear, m - range)) + ' &ndash; ' +
                    $.datepicker.formatDate('M',
                        new Date(selectedyear, m));
            }
        }
    }

    switch (ocean.period) {
        case 'monthly':
            fmt = function (m) {
                return $.datepicker.formatDate('MM',
                    new Date(selectedyear, m));
            };
            break;

        case '3monthly':
            fmt = _dateRange(selectedyear, 3);
            break;

        case '6monthly':
            fmt = _dateRange(selectedyear, 6);
            break;

        case '12monthly':
            fmt = _dateRange(selectedyear, 12);
            break;

        case 'yearly':
            /* ignore */
            return;

        default:
            console.error("ERROR: should not be reached");
            return;
    }

    var month = $('#month');

    month.find('option').remove();

    for (m = minMonth; m <= maxMonth; m++) {
        $('<option>', {
            value: m,
            html: fmt(m)
        }).appendTo(month);
    }

    var selectedmonth = ocean.date.getMonth();

    if (selectedmonth < minMonth) {
        selectFirstIfRequired('month');
    } else if (selectedmonth > maxMonth) {
        month.find('option:last').attr('selected', true);
        month.change();
    } else {
        setValue('month', selectedmonth);
    }
}

/**
 * updateDatasets:
 *
 * Updates the datasets displayed in the datasets combo.
 */
function updateDatasets(filter) {
    var datasets = ocean.variables[ocean.variable].plots[ocean.plottype][ocean.period];

    if (filter) {
        datasets = $.grep(datasets, filter);
    }

    /* sort by rank */
    datasets.sort(function (a, b) {
        var ar = 'rank' in ocean.datasets[a] ? ocean.datasets[a].rank : 0;
        var br = 'rank' in ocean.datasets[b] ? ocean.datasets[b].rank : 0;

        return br - ar;
    });

    /* FIXME: check if the datasets have changed */

    var dataset = getValue('dataset');
    $('#dataset option').remove();

    $.each(datasets, function (i, dataset) {
        $('<option>', {
            value: dataset,
            text: ocean.datasets[dataset].name
        }).appendTo('#dataset');
    });

    /* select first */
    setValue('dataset', dataset);
    selectFirstIfRequired('dataset');
}

/**
 * filterOpts:
 *
 * Filter @comboid so that it only contains options with the ids given in
 * @keys.
 */
function filterOpts(comboid, keys) {
    var select = $('#' + comboid);

    if (!keys) {
        console.warn("filterOpts was provided no keys for " + comboid);
        select.find('optgroup, option').show();
        return;
    }

    select.find('optgroup').hide();
    select.find('option').each(function () {
        var opt = $(this);

        if (opt.val() in keys) {
            opt.parent('optgroup').show();
            opt.show()
               .attr('disabled', false);
        } else {
            opt.hide()
               .attr('disabled', true);
        }
    });
}

/**
 * getValue:
 *
 * Returns: the selected value for a combo box
 */
function getValue(comboid) {
    return $('#' + comboid + ' option:selected').val();
}

/**
 * setValue:
 *
 * Sets the value for @comboid to @value.
 */
function setValue(comboid, value) {
    $('#' + comboid + ' option[value=' + value + ']').attr('selected', true);
    $('#' + comboid).change();
}

/**
 * selectFirstIfRequired:
 *
 * Select the first <option> of a <select> if there is no visible option
 * selected at the moment.
 */
function selectFirstIfRequired(comboid) {
    var combo = $('#' + comboid);

    /* the :visible selector does not work in WebKit */
    function _visible() {
        var e = $(this);
        return e.is(':visible') || e.css('display') != 'none';
    }

    if (combo.find('option:selected').filter(_visible).length == 0) {
        combo.find('option').filter(_visible).eq(0).attr('selected', true);
        combo.change();
    }
}

/**
 * addPointLayer:
 *
 * Adds a point selection layer to the map.
 */
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

                /* correct for wrapping issues from OpenLayers */
                if (feature.geometry.x < -180.) {
                    feature.geometry.x += 360.;
                } else if (feature.geometry.x > 180.) {
                    feature.geometry.x -= 360.;
                }
            },
            onFeatureInsert: function(feature) {
                var geometry = feature.geometry;
                var lon = geometry.x;
                var lat = geometry.y;

                lon = lon.toFixed(3);
                lat = lat.toFixed(3);

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

/**
 * removePointLayer:
 *
 * Removes a point selection layer from the map.
 */
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

function _controlVarParent(control) {
    return $('#' + control).parent('.controlvar');
}

/**
 * showControls:
 *
 * Shows a div.controlvar based on the id of the field within it.
 *
 * Be aware that control visibility is also affected by controlvars.css
 *
 * See Also: hideControls()
 */
function showControls() {
    var controls = arguments;

    if (controls.length == 0) {
        controls = ocean.controls;
    }

    $.each(controls, function (i, control) {
        var parent = _controlVarParent(control);

        parent.show();
        parent.parent('.controlgroup').show();

        $('#' + control).change();
    });
}

/**
 * hideControls:
 *
 * Hides a div.controlvar based on the id of the field within it.
 *
 * See Also: showControls()
 */
function hideControls() {
    /* FIXME: integrate with controlvars.css so all visibility is controlled
     * through a series of CSS rules */
    var controls = arguments;

    if (controls.length == 0) {
        controls = ocean.controls;
    }

    $.each(controls, function (i, control) {
        var parent = _controlVarParent(control);
        var group = parent.parent('.controlgroup');

        parent.hide();

        /* hide control group if required */
        if (group.children('.controlvar:visible').length == 0) {
            group.hide();
        }
    });
}

/**
 * updateVisibilities:
 *
 * Update the visibility of the controls by applying the rules in
 * controlvars.css
 */
function updateVisibilities(controlvar, old, new_) {
    /* update the classes */
    $('.controlvar').removeClass(controlvar + '-' + old)
                    .addClass(controlvar + '-' + new_);

    /* show any control groups that now need showing */
    $('.controlgroup .controlvar .field').each(function () {
        var field = $(this);

        if (field.css('display') != 'none') {
            field.closest('.controlvar').show();
            field.closest('.controlgroup').show();
        } else {
            field.closest('.controlvar').hide();
        }
    });

    /* hide any empty controlgroups */
    $('.controlgroup').each(function () {
        var group = $(this);

        if (group.children('.controlvar:visible').length == 0) {
            group.hide();
        }
    });
}

/**
 * updatePage:
 *
 * Make a request to the backend based on the currently selected controls.
 */
function updatePage() {
    if (!ocean.processing) {

        if (!ocean.dataset)
            return;

        if (!ocean.variable)
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
                    if (data.error) {
                        show_error(ocean.dataset.params(), data.error);
                    } else {
                        ocean.dataset.callback(data);
                    }
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                if (textStatus == 'parsererror') {
                    show_error(ocean.dataset.params(),
                               "Unable to parse server response.");
                } else {
                    show_error(ocean.dataset.params(), errorThrown);
                }
            },
            complete: function(jqXHR, textStatus) {
                ocean.processing = false;
                maybe_close_loading_dialog();
            }
        });
    }
}
