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
    'dshelp',
    'hour-slider',
    'reef',
    'alertdial',
    'marine',
    'tunafishing',
    'waveatlas'
];

ocean.compare = { limit: 24 };
ocean.processing = false;
ocean.date = new Date();

//Set up the view, model and controller instances
/**$.DropdownView.prototype = new $.View();
$.VariableModel.prototype = new $.Model();

var variableDropdownView = new $.DropdownView("variable");
var variableModel = new $.VariableModel();
var controller = new $.Controller(variableModel, variableDropdownView);
**/

var intersecIcon = L.icon({
    iconUrl: 'lib/leaflet-0.7.3/images/marker-icon.png',
    shadowUrl: 'lib/leaflet-0.7.3/images/cross.png',
    iconSize: [25, 41],
    shadowSize: [36, 36],
    iconAnchor: [12, 41],
    shadowAnchor: [17, 18]
});

var slider;
/* set up JQuery UI elements */
$(function() {
    /* work out which region file to load */
    if (location.search == '')
        ocean.config = 'pac';
    else
        ocean.config = location.search.slice(1);

    hideControls();
    assignAppClass();

    /* set up the date picker */
    $("#date").datepick({
        dateFormat: 'd MM yyyy',
        renderer: $.datepick.themeRollerRenderer,
        changeMonth: true,
       // alignment: 'bottom'
        showAnim: 'clip',
        showSpeed: 'fast',
        nextText: 'M >',
        prevText: '< M',
        todayText: 'dd M yy',
        commandsAsDateFormat: true,
        onSelect: dateSelection
    });

    slider = new Dragdealer('hour-slider', {
        slide: false
    });

    /* UI handlers */
    $('#submit').click(function () {
        updatePage();

        return false; /* don't propagate event */
    });

    /* Variable */
    $('#variable').change(function () {
        var currentApp = ocean.app.new;
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

        updateDatasets();
        ocean.dataset.onVariableChange();
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
                    disableIntersecMarker();
                    break;
                }

                enableIntersecMarker();
                break;

            default:
                disableIntersecMarker();
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
            date_.datepick('option', {
                minDate: range.min,
                maxDate: range.max,
                yearRange: range.min.getFullYear() + ':' + range.max.getFullYear()
            });


            /*Bug#790, initialise date*/
            if (range.max.getTime() < ocean.date.getTime()) {
                ocean.date = range.max;
            }
            /* automatically clamps the date to the available range */
            date_.datepick('setDate', ocean.date).change();
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
        } 
        if (selectedyear == range.max.getFullYear()) {
            maxMonth = range.max.getMonth();
        }

        updateMonths(minMonth, maxMonth);
    });

    /* Date range is changed */
//    $('#date, #month, #year').change(function () {
    $('#date, #month, #year').change(function () {

        if (!(ocean.variable in ocean.variables) ||
            !(ocean.plottype in ocean.variables[ocean.variable].plots) ||
            !(ocean.period in ocean.variables[ocean.variable].plots[ocean.plottype])) {
            return;
        }

        // determine the chosen date 
        var date_;

        switch (ocean.period) {
            case 'daily':
            case 'weekly':
                date_ = $('#date').datepick('getDate')[0];
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
                    return true; // no date range defined 

//                return (ocean.date >= range.min) && (ocean.date <= range.max);
                return true;//(ocean.date >= range.min) && (ocean.date <= range.max);
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

    $('#reef').change(function() {
        if(this.checked) {
            ocean.reefLayer = L.tileLayer.wms("cgi/map.py?map=bathymetry", {
               layers: 'reeflocations',
               format: 'image/png',
               transparent: true,
               attribution: '<a href="http://www.reefbase.org/gis_maps/datasets.aspx" title="Reef Base">Reef Base</a>'
            }).addTo(ocean.mapObj);
        }
        else {
            ocean.mapObj.removeLayer(ocean.reefLayer);
        }
    });

    $('#alertdial').change(function() {
        if(this.checked) {
            ocean.alertDialLayer = L.tileLayer.wms("cgi/map.py?map=bathymetry", {
               layers: 'alertdial',
               format: 'image/png',
               transparent: true,
               attribution: '',
               continuousWorld: true
            }).addTo(ocean.mapObj);
        }
        else {
            ocean.mapObj.removeLayer(ocean.alertDialLayer);
        }
    });

    $('#marine').change(function() {
        if(this.checked) {
            ocean.marineLayer = L.tileLayer.wms("cgi/map.py?map=bathymetry", {
               layers: 'marineparks',
               format: 'image/png',
               transparent: true,
               attribution: '<a href="http://www.sprep.org/" title="Marine Park Areas">Marine Park Areas</a>'
            }).addTo(ocean.mapObj);
        }
        else {
            ocean.mapObj.removeLayer(ocean.marineLayer);
        }
    });

    var points = [
        ['Pago Pago', -14.296000, 189.334000, 0, ' Atlas/Regional/Pdf/AS/PagoPago.pdf'],
        ['Tau Island',-14.213200, 190.580200, 0, ' Atlas/Regional/Pdf/AS/TauIs.pdf'],
        ['Arutanga', -18.850000, 200.187000, 0, ' Atlas/Regional/Pdf/CK/Arutanga.pdf'],
        ['Ngatangiia passage', -21.243860, 200.276910, 0, ' Atlas/Regional/Pdf/CK/Ngatangiia_passage.pdf'],
        ['Avarua passage', -21.203690, 200.224790, 0, ' Atlas/Regional/Pdf/CK/Avarua_passage.pdf'],
        ['Rutaki passage', -21.264650, 200.194750, 0, ' Atlas/Regional/Pdf/CK/Rutaki_passage.pdf'],
        ['Avaavaroa passage', -21.272420, 200.219690, 0, ' Atlas/Regional/Pdf/CK/Avaavaroa_passage.pdf'],
        ['Black Rock', -21.205240, 200.175040, 0, ' Atlas/Regional/Pdf/CK/Black_Rock.pdf'],
        ['Wave energy hotspot', -21.262550, 200.180620, 0, ' Atlas/Regional/Pdf/CK/Rarotongan_Hotspot.pdf'],
        ['Tupapa', -21.215910, 200.268190, 0, ' Atlas/Regional/Pdf/CK/Tupapa.pdf'],
        ['Pue', -21.201080, 200.246280, 0, ' Atlas/Regional/Pdf/CK/Pue.pdf'],
        ['Titikaveka', -21.279370, 200.243180, 0, ' Atlas/Regional/Pdf/CK/Titikaveka.pdf'],
        ['Fuel Pipeline', -21.196370, 200.203530, 0, ' Atlas/Regional/Pdf/CK/Oil_Pipeline.pdf'],
        ['Wave Bouy location 1', -21.272000, 200.274000, 0, ' Atlas/Regional/Pdf/CK/RaroWB1.pdf'],
        ['Wave Bouy location 2', -21.25600, 200.292200, 0, ' Atlas/Regional/Pdf/CK/RaroWB2.pdf'],
        ['Papua passage', -21.266990, 200.200230, 0, ' Atlas/Regional/Pdf/CK/Papua_passage.pdf'],
        ['Avatiu passage', -21.202240, 200.215710, 0, ' Atlas/Regional/Pdf/CK/Avatiu_passage.pdf'],
        ['Labasa Channel', -16.290000, 179.268600, 0, ' Atlas/Regional/Pdf/FJ/Labasa.pdf'],
        ['Levuka', -17.680000, 178.850000, 0, ' Atlas/Regional/Pdf/FJ/Levuka.pdf'],
        ['Savusavu', -16.775000, 179.323900, 0, ' Atlas/Regional/Pdf/FJ/Savusavu.pdf'],
        ['Suva', -18.145400, 178.395300, 0, ' Atlas/Regional/Pdf/FJ/Suva.pdf'],
        ['Bora Bora', -16.493500, 208.220000, 0, ' Atlas/Regional/Pdf/PF/BoraBora.pdf'],
        ['Papeete', -17.513000, 210.420000, 0, ' Atlas/Regional/Pdf/PF/Papeete.pdf'],
        ['Chuuk', 7.513800, 151.979600, 0, ' Atlas/Regional/Pdf/FM/Chuuk.pdf'],
        ['Kosrae', 5.369300, 162.931300, 0, ' Atlas/Regional/Pdf/FM/Kosrae.pdf'],
        ['Pohnpei', 7.027200, 158.183800, 0, ' Atlas/Regional/Pdf/FM/Pohnpei.pdf'],
        ['Yap', 9.486500, 138.134400, 0, ' Atlas/Regional/Pdf/FM/Yap.pdf'],
        ['Guam', 13.450000, 144.610000, 0, ' Atlas/Regional/Pdf/GM/Guam.pdf'],
        ['Betio', 1.413500, 172.900000, 0, ' Atlas/Regional/Pdf/KB/Betio.pdf'],
        ['Kwajalein', 8.815000, 167.592500, 0, ' Atlas/Regional/Pdf/MA/Kwajalein.pdf'],
        ['Majuro', 7.178600, 171.186400, 0, ' Atlas/Regional/Pdf/MA/Majuro.pdf'],
        ['Nauru', -0.530200, 166.904400, 0, ' Atlas/Regional/Pdf/NA/Nauru.pdf'],
        ['Poum', -20.258600, 163.829500, 0, ' Atlas/Regional/Pdf/NC/Poum.pdf'],
        ['Poindimie', -20.875400, 165.485000, 0, ' Atlas/Regional/Pdf/NC/Poindimie.pdf'],
        ['Kouaoua', -21.252800, 165.923700, 0, ' Atlas/Regional/Pdf/NC/Kouaoua.pdf'],
        ['Nepoui', -21.416100, 164.922200, 0, ' Atlas/Regional/Pdf/NC/Nepoui.pdf'],
        ['Noumea', -22.374100, 166.241200, 0, ' Atlas/Regional/Pdf/NC/Noumea.pdf'],
        ['Thio', -21.505800, 166.313800, 0, ' Atlas/Regional/Pdf/NC/Thio.pdf'],
        ['Koror', 7.259600, 134.493300, 0, ' Atlas/Regional/Pdf/PL/Koror.pdf'],
        ['Alotau', -10.318200, 150.452500, 0, ' Atlas/Regional/Pdf/PG/Alotau.pdf'],
        ['Arawa', -6.111000, 155.594700, 0, ' Atlas/Regional/Pdf/PG/Arawa.pdf'],
        ['Bialla', -5.295000, 150.983200, 0, ' Atlas/Regional/Pdf/PG/Bialla.pdf'],
        ['Kavieng', -2.560200, 150.781000, 0, ' Atlas/Regional/Pdf/PG/Kavieng.pdf'],
        ['Kimbe', -5.540500, 150.148700, 0, ' Atlas/Regional/Pdf/PG/Kimbe.pdf'],
        ['Lorengau', -1.949400, 147.302300, 0, ' Atlas/Regional/Pdf/PG/Lorengau.pdf'],
        ['Daru', -9.059500, 143.240400, 0, ' Atlas/Regional/Pdf/PG/Daru.pdf'],
        ['Rabaul', -4.286700, 152.240000, 0, ' Atlas/Regional/Pdf/PG/Rabaul.pdf'],
        ['Samarai', -10.611800, 150.659000, 0, ' Atlas/Regional/Pdf/PG/Samarai.pdf'],
        ['Vanimo', -2.650500, 141.295300, 0, ' Atlas/Regional/Pdf/PG/Vanimo.pdf'],
        ['Wewak', -3.540200, 143.662100, 0, ' Atlas/Regional/Pdf/PG/Wewak.pdf'],
        ['Apia', -13.820400, 188.234700, 0, ' Atlas/Regional/Pdf/WS/Apia.pdf'],
        ['Ghizo', -8.135300, 156.843400, 0, ' Atlas/Regional/Pdf/SO/Ghizo.pdf'],
        ['Honiara', -9.413400, 159.982600, 0, ' Atlas/Regional/Pdf/SO/Honiara.pdf'],
        ['Nuku alofa', -21.008600, 184.815500, 0, ' Atlas/Regional/Pdf/TO/Nukualofa.pdf'],
        ['Pangai', -19.777900, 185.596700, 0, ' Atlas/Regional/Pdf/TO/Pangai.pdf'],
        ['Neiafu', -18.761700, 185.893200, 0, ' Atlas/Regional/Pdf/TO/Neiafu.pdf'],
        ['Port Vila', -17.741500, 168.291400, 0, ' Atlas/Regional/Pdf/VU/PortVila.pdf'],
        ['Leava', -14.299800, 181.833400, 0, ' Atlas/Regional/Pdf/WF/Leava.pdf'],
        ['Honikulu Passage', -13.395000, 183.779600, 0, ' Atlas/Regional/Pdf/WF/Honikulu.pdf'],
        ['Hiva Oa', -9.826500, 220.973300, 0, ' Atlas/Regional/Pdf/PF/HivaOa.pdf'],
        ['Nuku Hiva', -8.954400, 219.898400, 0, ' Atlas/Regional/Pdf/PF/NukuHiva.pdf'],
        ['Rikitea', -23.308200, 225.137500, 0, ' Atlas/Regional/Pdf/PF/Rikitea.pdf'],
        ['Rangiroa', -14.841400, 212.362800, 0, ' Atlas/Regional/Pdf/PF/Rangiroa.pdf'],
        ['Fakarava', -16.664200, 214.385400, 0, ' Atlas/Regional/Pdf/PF/Fakarava.pdf'],
        ['Tubuai', -23.307300, 210.520200, 0, ' Atlas/Regional/Pdf/PF/Tubuai.pdf'],
        ['Kiritimati', 1.963600, 202.437900, 0, ' Atlas/Regional/Pdf/KB/Kiritimati.pdf'],
        ['Canton Is.', -2.827000, 188.237100, 0, ' Atlas/Regional/Pdf/KB/Canton.pdf'],
        ['Kapingamarangi', 1.124900, 154.753200, 0, ' Atlas/Regional/Pdf/FM/Kapingamarangi.pdf'],
        ['Penrhyn', -8.960200, 201.926300, 0, ' Atlas/Regional/Pdf/CK/Penrhyn.pdf'],
        ['Niue', -19.044600, 190.026800, 0, ' Atlas/Regional/Pdf/NI/Niue.pdf'],
        ['Kadavu', -19.222600, 178.320700, 0, ' Atlas/Regional/Pdf/FJ/Kadavu.pdf'],
        ['Taveuni', -17.059300, 179.874100, 0, ' Atlas/Regional/Pdf/FJ/Taveuni.pdf'],
        ['Tanna', -19.566800, 169.247100, 0, ' Atlas/Regional/Pdf/VU/Tanna.pdf'],
        ['Nukunonu', -9.235100, 188.118700, 0, ' Atlas/Regional/Pdf/TK	/Nukunonu.pdf'],
        ['Bonriki', 1.441900, 173.295800, 0, ' Atlas/Regional/Pdf/KB/Bonriki.pdf'],
        ['Malau', -16.357800, 179.365000, 0, ' Atlas/Regional/Pdf/FJ/Malau.pdf'],
        ['Lautoka', -17.594400, 177.414100, 0, ' Atlas/Regional/Pdf/FJ/Lautoka.pdf'],
        ['Luganville', -15.575300, 167.378700, 0, ' Atlas/Regional/Pdf/VU/Luganville.pdf'],
        ['Isabel Is.', -8.000000, 159.662800, 0, ' Atlas/Regional/Pdf/SO/IsabelIs.pdf'],
        ['Rarotonga Wave Buoy', -21.270000, 200.271700, 0, ' Atlas/Regional/Pdf/CK/RarotWB1.pdf'],
        ['Fiji Wave Buoy', -19.306700, 177.956700, 0, ' Atlas/Regional/Pdf/FJ/FijiWB1.pdf'],
        ['Tonga Wave Buoy', -21.237000, 184.730000, 0, ' Atlas/Regional/Pdf/TO/TongaWB2.pdf'],
        ['Eua Wave Buoy', -21.838300, 184.585000, 0, ' Atlas/Regional/Pdf/TO/EuaWB1.pdf'],
        ['Funafuti Wave buoy', -8.525000, 179.215000, 0, ' Atlas/Regional/Pdf/TV/Funafuti.pdf'],
        ['Efate Wave Buoy', -17.875000, 168.550000, 0, ' Atlas/Regional/Pdf/VU/EfateWB1.pdf'],
        ['Pine Is.', -22.714100, 167.434100, 0, ' Atlas/Regional/Pdf/NC/PineIs.pdf'],
        ['Mare Is.', -21.576600, 168.128700, 0, ' Atlas/Regional/Pdf/NC/MareIs.pdf'],
        ['Raivavae', -23.907700, 212.356400, 0, ' Atlas/Regional/Pdf/PF/Raivavae.pdf'],
        ['Rurutu', -22.481100, 208.643200, 0, ' Atlas/Regional/Pdf/PF/Rurutu.pdf'],
        ['Niuas', -15.555500, 184.374700, 0, ' Atlas/Regional/Pdf/TO/Niuas.pdf'],
        ['Rimatara', -22.668600, 207.195600, 0, ' Atlas/Regional/Pdf/PF/Rimatara.pdf']
    ];

    var markers = new L.FeatureGroup();

    function populateMarkers() {
        for (var i = 0; i < points.length; i++) {
            var marker = new L.marker([points[i][1],points[i][2]])
                        .bindPopup("<b>Location: "+points[i][0] + "</b><br>" + "<a href=http://gsd.spc.int/wacop/" + points[i][4].trim() + " target=_blank>See wave climate report</a>");
            markers.addLayer(marker);
        }
        return false;
    }

    if (ocean.app.new == "climate"){
        populateMarkers();
        $('#waveatlas')[0].checked=false;
    }

    $('#waveatlas').change(function() {
        if(this.checked) {
            ocean.mapObj.addLayer(markers);
        } else {
            ocean.mapObj.removeLayer(markers);
        }
    });


    var groupings = {};

    /* load JSON configuration */
    variableModel.getData();
    regionCountryModel.getData(); 
});

    /**
     *
     */ 
    function dateSelection () {
        /* determine the chosen date */
        $('#date').change();
    };
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
    var mindate = $.datepick.determineDate(range.minDate, null, 'yyyymmdd');
    var maxdate = $.datepick.determineDate(range.maxDate, null, 'yyyymmdd');

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

    return { min: new Date(minDate), max: new Date(maxDate) };
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
                return $.datepick.formatDate('M y',
                        new Date(selectedyear, m - range)) + ' &ndash; ' +
                    $.datepick.formatDate('M y',
                        new Date(selectedyear, m));
            }
        } else {
            return function (m) {
                return $.datepick.formatDate('M',
                        new Date(selectedyear, m - range)) + ' &ndash; ' +
                    $.datepick.formatDate('M',
                        new Date(selectedyear, m));
            }
        }
    }

    switch (ocean.period) {
        case 'monthly':
            fmt = function (m) {
                return $.datepick.formatDate('MM',
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
//    if (dataset is null) {
 //       $("#dataset").val($("#dataset option:first").val());
//    }
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
function enableIntersecMarker () {
    map.on('click', setIntersection); 
    if (map.intersecMarker) {
        map.intersecMarker.setOpacity(1.0); 
    }

    /* track changes to the lat/lon and move the feature */
//    $('#latitude, #longitude').change(function () {
//        var lat = $('#latitude').val();
//        var lon = $('#longitude').val();

//        layer.removeAllFeatures();

//        if (lat != '' && lon != '')
//            layer.addFeatures([
//                new OpenLayers.Feature.Vector(
//                    new OpenLayers.Geometry.Point(lon, lat))
//            ]);
//    });

    /* update the map with the initial lat/lon */
//    $('#latitude').change();
}

/**
 * removePointLayer:
 *
 * Removes a point selection layer from the map.
 */
function disableIntersecMarker () {
    map.off('click', setIntersection);
    if (map.intersecMarker) {
        map.intersecMarker.setOpacity(0); 
    }
}

function setIntersection(e) {
    if (!map.intersecMarker) {
        map.intersecMarker = L.marker([90.0, 0], {icon: intersecIcon}).addTo(map);
    }
    map.intersecMarker.setLatLng(e.latlng);
    $('#latitude').val(e.latlng.lat);
    $('#longitude').val(e.latlng.lng);
    
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

function assignAppClass() {
    if (ocean.app) {
        if (ocean.app.old) {
            $('.controlvar').removeClass(ocean.app.old);
        }
        if (ocean.app.new) {
            $('.controlvar').addClass(ocean.app.new);
        }
    }
    else {
        ocean.app = {"new": window.location.hash.split('#')[1]};
    }
    $('.controlvar').addClass(ocean.app.new);
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
        var id = this.id;
        if (field.css('display') != 'none') {
            field.closest('.controlvar').show('fast', function() {
                if (id == 'hour-slider') {
                    slider.reflow();
                }
            });
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

        /*Show feedback id variable is not selected.*/
        if ((typeof (ocean.variable) == 'undefined') || (!ocean.variable)){
            show_feedback("Please select a variable.");
            return;
        }    
        
        function show_error(params, text)
        {
            var url = 'cgi/portal.py?' + $.param(params);
    
            $('#error-dialog-status').html("<b>Error:</b>");
            $('#error-dialog-content').html(text);
            $('#error-dialog-request').prop('href', url);
            $('#error-dialog-report-back').show();
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

                paramscheck = ocean.dataset.beforeSend();
                if (!paramscheck) {
                    ocean.processing = false;
                    $('#loading-dialog').dialog('close');
                }
                return paramscheck;
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

function stepForward() {
    slider.setStep(slider.getStep()[0] + 1);
}

function stepBackward() {
    slider.setStep(slider.getStep()[0] - 1);
}

function show_feedback(text){
     $('#error-dialog-status').html("<b>Missing Input:</b>");
     $('#error-dialog-content').html(text);
     $('#error-dialog-report-back').hide();
     $('#error-dialog').dialog('open');
}  
