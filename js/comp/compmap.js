/*jslint eqeq: true, undef: true, sloppy: true, sub: true, todo: true, vars: true, white: true, browser: true, windows: true */
/*
 * (c) 2012 Commonwealth of Australia
 * Australian Bureau of Meteorology, COSPPac COMP
 * All Rights Reserved
 */

var ocean = ocean || {};
var map;

/* Define a $.cachedScript() method that allows fetching a cached script
 * Taken from the jQuery API docs */
jQuery.cachedScript = function(url, options) {

  /* allow user to set any option except for dataType, cache, and url */
  options = $.extend(options || {}, {
    dataType: "script",
    cache: true,
    url: url
  });

  /* Use $.ajax() since it is more flexible than $.getScript
   * Return the jqXHR object so we can chain callbacks */
  return jQuery.ajax(options);
};

/**
 * fatal_error:
 *
 * Show a fatal error (one that terminates the portal) with @msg.
 */
function fatal_error(msg)
{
    $('#error-dialog-content').html(msg);
    $('#error-dialog-request').hide();
    $('#error-dialog').dialog('option', { 'modal': true,
                                          'dialogClass': 'notitle',
                                          'closeOnEscape': false });
    $('#error-dialog').dialog('open');
}

/**
 * maybe_close_loading_dialog:
 *
 * Checks if all things have loaded and we can close the loading dialog.
 */
function maybe_close_loading_dialog()
{
    if (ocean.mapLoading || ocean.outputsLoading > 0)
        return;

    $('#loading-dialog').dialog('close');
}

window.onerror = function (msg, url, line) {
    fatal_error("Javascript error: " + msg + " &mdash; please " +
                '<a href="javascript:location.reload()">' +
                "reload</a> your browser." + "<br/><small>"
                + url + ":" + line + "</small>");
    return false;
}

$(document).ready(function() {
    /* initialise jQueryUI elements */
    $('.dialog').dialog({
        autoOpen: false,
        resizable: false
    });

    $('button').button();
    $('#enlargeDiv').hide();

    /* initialise and show the loading dialog */
    $('#loading-dialog')
        .dialog('option', { 'modal': true,
                            'dialogClass': 'notitle',
                            'closeOnEscape': false,
                            'height': 55,
                            'resizable': false })
        .dialog('open');

    /* work out which region file to load */
    if (location.search == '')
        ocean.config = 'pac';
    else
        ocean.config = location.search.slice(1);

    /* set up theme */
    $('.panel h1').addClass('ui-widget-header ui-state-default');
    $('.panel').addClass('border');

    /* set up toolbar */
    $('.toolbar a').addClass('ui-state-default ui-corner-all');
    $('.toolbar a').hover(function () {
        $(this).toggleClass('ui-state-active');
    });

    $(window).load(function () {
        /* layout functions for window resize */
        $(window).resize(function () {
            /* expand vertical */
            $('.expand-v').each(function () {
                var e = $(this);

                e.height(e.parent().innerHeight() - e.position().top);
            });
        }).resize().resize(); /* IE8 can't work out the height first time! */

        /* position centre layout */
        $('.layout-center')
            .css('left', $('.layout-west').outerWidth())
            .css('right', $('.layout-east').outerWidth());
    });

    $('#region').change(function () {
        var selected = $('#region option:selected');

        if (selected.length == 0) {
            return;
        }

        var bounds = selected.data('bounds');

        map.setCenter(bounds.getCenterLonLat(),
                      map.getZoomForExtent(bounds),
                      false, true);

        ocean.area = selected.val();
    });

    $.when(
        /* portals config */
        $.getJSON('config/comp/portals.json', function(data, status_, xhr) {
            ocean.configProps = data[ocean.config];

            if (!ocean.configProps) {
                fatal_error("No portal called '" + ocean.config + "'.");
                return;
            }

            document.title = ocean.configProps.name + " Ocean Maps Portal";
        }),

        /* regions config */
        $.getJSON('cgi/regions.py', { portal: ocean.config },
                  function(data, status_, xhr) {

            /* append the regions and their extents */
            $.each(data, function (i, region) {
                $('<option>', {
                    value: region.abbr,
                    text: region.name
                }).data('extent', region.extent)
                  .appendTo('#region');
            });
        }),

        /* load OpenLayers */
        $.cachedScript($('#map').attr('src')).done(function () {
            OpenLayers.ImgPath = "lib/OpenLayers/img/"
            createMap();
        }))

    .done(function () {
        var bounds = new OpenLayers.Bounds();

        /* iterate the region bounds to calculate the * restricted extent */
        $('#region option').each(function () {
            var e = $(this);
            var b = new OpenLayers.Bounds(e.data('extent'));

            e.data('bounds', b);
            bounds.extend(b);
        });

        /* compensate for the date line wrapping */
        if (bounds.right > 180) {
            bounds.left -= 360;
            bounds.right -= 360;
        }

        map.setOptions({ restrictedExtent: bounds });
        setValue('region', ocean.config);
    })
    .fail(function () {
        maybe_close_loading_dialog();
        fatal_error("Failed to load portal.");
    });
});

/**
 * createMap:
 *
 * Create the map component. Should only be called once.
 */
function createMap () {
    map = new OpenLayers.Map("map", {
        minResolution: 0.001373291,
        numZoomLevels: 8,
        maxExtent: new OpenLayers.Bounds(-180, -90, 180, 90),
        theme: null,
        controls: [
            new OpenLayers.Control.PanZoomBar(),
            new OpenLayers.Control.MousePosition(),
            new OpenLayers.Control.LayerSwitcher({
                div: document.getElementById('mapControlsLayers'),
                ascending: false,
                roundedCorner: false
            }),
            new OpenLayers.Control.ScaleLine({
                bottomOutUnits: '',
                bottomInUnits: ''
            }),
            new OpenLayers.Control.Navigation({
                dragPanOptions: { enableKinetic: true },
                documentDrag: true
            })
        ],
        eventListeners: {
            addlayer: _updateDisabled,
            removelayer: _updateDisabled,
            changelayer: _mapBaseLayerChanged
        }
    });

    /* add keyboard controls separately so we can disable them when required */
    var keyboardControls = new OpenLayers.Control.KeyboardDefaults();
    map.addControl(keyboardControls);

    $(':input').focusin(function () {
        keyboardControls.deactivate();
    });
    $(':input').focusout(function () {
        keyboardControls.activate();
    });

    ocean.mapObj = map;

    var bathymetryLayer = new OpenLayers.Layer.MapServer("Bathymetry",
        'cgi/map.py', {
            map: 'bathymetry',
            layers: ['bathymetry', 'land', 'maritime', 'capitals', 'countries']
        }, {
            transitionEffect: 'resize',
            wrapDateLine: true,
            eventListeners: {
                loadend: maybe_close_loading_dialog
            }
        });

    var outputLayer = new OpenLayers.Layer.MapServer("Output",
        'cgi/map.py', {
        map: 'raster',
        layers: ['raster', 'land', 'capitals', 'countries']
    }, {
        transitionEffect: 'resize',
        wrapDateLine: true,
        eventListeners: {
            loadstart: function () {
                ocean.mapLoading = true;
            },
            loadend: function () {
                ocean.mapLoading = false;
                maybe_close_loading_dialog();
            }
        }
    });

    map.addLayers([bathymetryLayer, outputLayer]);
    map.setBaseLayer(bathymetryLayer);

    function _mapBaseLayerChanged(evt) {
        var layerName;
        var legendDiv = $('#legendDiv');
        var enableOL = false;

        if (evt)
            layerName = evt.layer.name;

        if (layerName == null || layerName == 'Bathymetry') {
            legendDiv.html("<p><b>Bathymetry (m)</b></p><br/><img src='images/bathymetry_ver.png' height='180'/>");
        }
        else {
            if (ocean.map_scale)
                legendDiv.html('<p><img src="' + ocean.map_scale + '" />');
            else
                legendDiv.html('<p></p>');

            enableOL = true;
        }

        $('.outputgroup input[type=radio]').attr('disabled', !enableOL);
        _updateDisabled();
    }

    _mapBaseLayerChanged(null);
}

function _updateDisabled ()
{
    /* determine whether to disable Output
     * on a timeout because OpenLayers changes the DOM */
    window.setTimeout(function () {
        var disable = $('.outputgroup input[type=radio]').length < 1;
        var radio = $('#mapControls .baseLayersDiv input[value="Output"]');
        radio.attr('disabled', disable);
    }, 5);
}

/**
 * selectMapLayer:
 *
 * Select the map layer specified by @name.
 */
function selectMapLayer(name)
{
    var layer = map.getLayersByName(name)[0];

    map.setBaseLayer(layer);
    _updateDisabled();
}

/**
 * updateMap:
 *
 * Updates the output layer of the map with @data.
 */
function updateMap (data) {
    var layer = map.getLayersByName("Output")[0];

    ocean.map_scale = data.scale;

    map.setBaseLayer(layer);
    layer.params['raster'] = [data.mapeast, data.mapeastw, data.mapwest, data.mapwestw];
    ocean.mapLoading = true;
    layer.redraw(true);
}

/**
 * prependOutputSet:
 *
 * Prepends an output group to the output panel.
 */
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
                    .attr('checked', true)
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

ocean.outputsLoading = 0;
function _createOutput(image, dataURL, name, extras, data)
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
        /* Workaround in IE8 to deselect other radios */
        $('.outputLayerRadio').attr('checked', false);

        $('<input>', {
            type: 'radio',
            'class': 'outputLayerRadio',
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

    var params = '';

    /* this hack required to ensure IE8 always loads the image */
    if ($.browser.msie && $.browser.version == '8.0') {
        params = '?' + $.param({ time: $.now() });
    }

    var img = $('<img>', {
        src: image + params
    }).appendTo(a);

    div.hide();
    ocean.outputsLoading += 1;

    function outputLoaded () {
        div.slideDown(400, function () {
            ocean.outputsLoading -= 1;
            maybe_close_loading_dialog();
        });
    }

    img.load(outputLoaded)
       .error(outputLoaded);

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

/**
 * appendOutput:
 * @imageURL: URL for the image
 * @dataURL: optional URL for the data to download
 * @name: optional title for the output
 * @extras: optional extra HTML
 * @data: optional ref to the data object, so this output can be selected as
 *        the map base layer
 *
 * Appends a new output to the topmost output group.
 *
 * See Also: prependOutput()
 */
function appendOutput()
{
    _createOutput.apply(null, arguments).appendTo($('#outputDiv .outputgroup:first'));
}

/**
 * prependOutput:
 * @imageURL: URL for the image
 * @dataURL: optional URL for the data to download
 * @name: optional title for the output
 * @extras: optional extra HTML
 * @data: optional ref to the data object, so this output can be selected as
 *        the map base layer
 *
 * Prepends a new output to the topmost output group.
 *
 * See Also: appendOutput()
 */
function prependOutput()
{
    _createOutput.apply(null, arguments).prependTo($('#outputDiv .outputgroup:first'));
}

/**
 * enlargeImg:
 *
 * Shows or hides an enlarged version of the image within the map.
 */
function enlargeImg(img, show) {
    var enlargeDiv = $('#enlargeDiv');

    if (show) {
        enlargeDiv.stop(true, true);
        $('#enlargeDiv img').remove();
        var eimg = $('<img>', {
            src: img.src,
            'class' : 'imagepreview'
        }).appendTo(enlargeDiv);

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
