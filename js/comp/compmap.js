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

$(function() {
    /* initialise jQueryUI elements */
    $('.dialog').dialog({
        autoOpen: false,
        resizable: false
    });

/////    $('button').button();
//    $('#enlargeDiv, #subregion').hide();

    /* initialise and show the loading dialog */
    $('#loading-dialog')
        .dialog('option', { 'modal': true,
                            'dialogClass': 'notitle',
                            'closeOnEscape': false,
                            'height': 55,
                            'resizable': false });
//        .dialog('open');

    /* work out which region file to load */
////    if (location.search == '')
////        ocean.config = 'pac';
////    else
////        ocean.config = location.search.slice(1);

    /* set up theme */
////    $('.panel h1').addClass('ui-widget-header ui-state-default');
//    $('.panel').addClass('border');

    /* set up toolbar */
////    $('.toolbar a').addClass('ui-state-default ui-corner-all');
////    $('.toolbar a').hover(function () {
////        $(this).toggleClass('ui-state-active');
////    });

////    $(window).load(function () {
        /* layout functions for window resize */
////        $(window).resize(function () {
            /* expand vertical */
////            $('.expand-v').each(function () {
////                var e = $(this);

////                e.height(e.parent().innerHeight() - e.position().top);
////            });
////        }).resize().resize(); /* IE8 can't work out the height first time! */

        /* position centre layout */
////        $('.layout-center').css({
////            left: $('.layout-west').outerWidth(),
////            right: $('.layout-east').outerWidth(),
//            height: '100%'
////        });

//        if (map) {
            /* poke the map to resize */
//            map.updateSize();
//        }
////    });

//    $.when(
        /* portals config */
//        $.getJSON('config/comp/portals.json', function(data, status_, xhr) {
//            ocean.configProps = data[ocean.config];

//            if (!ocean.configProps) {
//                fatal_error("No portal called '" + ocean.config + "'.");
//                return;
//            }

//            document.title = ocean.configProps.name + " Ocean Application";
//        }),
//        })
 
        /* load OpenLayers */
//        $.cachedScript($('#map').attr('src')).done(function () {
//            OpenLayers.ImgPath = "lib/OpenLayers/img/"
//            createMap();
//        }))
//)
//    .done(function () {
        createMap();
        resetLegend();
//        var bounds = new OpenLayers.Bounds();

        /* iterate the region bounds to calculate the * restricted extent */
 //       $('#region option').each(function () {
//            var e = $(this);
//            var b = new OpenLayers.Bounds(e.data('extent'));

//            e.data('bounds', b);
//            bounds.extend(b);
//        });

        /* compensate for the date line wrapping */
//        if (bounds.right > 180) {
//            bounds.left -= 360;
//            bounds.right -= 360;
//        }

//        map.setOptions({ restrictedExtent: bounds });
//        var bounds;

        /* iterate the region bounds to calculate the * restricted extent */
//        $('#region option').each(function () {
//            var e = $(this);
//            var b = new OpenLayers.Bounds(e.data('extent'));

//            e.data('bounds', b);
//            if (!bounds) {
//                bounds = b;
//            }
//            else {
//                bounds.extend(b);
//            }
//        });
//        map.fitBounds(bounds);        
//        setValue('region', ocean.config);
//    })
//    .fail(function () {
//        maybe_close_loading_dialog();
//        fatal_error("Failed to load portal.");
//    });
});

/**
 * createMap:
 *
 * Create the map component. Should only be called once.
 */
function createMap () {
    var southWest = L.latLng(-60, 90),
        northEast = L.latLng(60, 320),
        bounds =  L.latLngBounds(southWest, northEast);

    map = L.map('map', {
        center: L.latLng(0, 205),
 //       maxBounds: bounds,
        minZoom: 3,
        maxZoom: 8,
        zoom: 3,
        zoomAnimation: true,
        crs: L.CRS.EPSG4326
    });
   
    ocean.bathymetryLayer = L.tileLayer.wms("cgi/map.py?map=bathymetry", {
       layers: 'bathymetry,land,maritime,capitals,countries',
       format: 'image/png',
       transparent: true,
       attribution: '<a href="http://www.naturalearthdata.com/about/" title="About Natural Earth">Made with Natural Earth</a>, <a href="http://www.marineregions.org/disclaimer.php" title="EEZ boundaries">Marineregions</a>'
    }).addTo(map);
/**
    ocean.countriesLayer = L.tileLayer.wms("cgi/map.py?map=bathymetry", {
       layers: 'capitals,countries',
       format: 'image/png',
       transparent: true,
       attribution: '<a href="http://www.naturalearthdata.com/about/" title="About Natural Earth">Made with Natural Earth</a>'
    })

    ocean.overlayGroup = L.layerGroup([ocean.countriesLayer]).addTo(map);
*/
    L.control.scale({imperial: false}).addTo(map);

    ocean.mapObj = map;
    ocean.overlayGroup = L.layerGroup().addTo(map);
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
//    var layer = map.getLayersByName(name)[0];

//    map.setBaseLayer(layer);
    _updateDisabled();
}

/**
 * updateMap:
 *
 * Updates the output layer of the map with @data.
 */
function updateMap(data) {
    var imageUrl = data.mapimg,
        imageBounds = [[-90, 0], [90, 360]]

    if(ocean.imageOverlay) {
        ocean.imageOverlay.setUrl(imageUrl);
    }
    else {
        ocean.imageOverlay = L.imageOverlay(imageUrl, imageBounds);
        ocean.overlayGroup.addLayer(ocean.imageOverlay);
        ocean.imageOverlay.setOpacity(1.0);
    }
}

/**
 * Reset map to bathymetry basemap.
 */
function resetMap() {
  ocean.overlayGroup.clearLayers();

}

/**
 * Reset legend to the bathymetry.
 */
function resetLegend() {
    //set legend
    ocean.map_scale = 'images/bathymetry_ver.png';
    $('#legendDiv').empty().append($('<img>', {src: ocean.map_scale, alt: 'Legend'}));
}

function setLegend(legendUrl) {
     $('#legendDiv img').attr('src', legendUrl);
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
//                selectMapLayer("Bathymetry");
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

