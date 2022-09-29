define("pref_app", ["pref_storage"], function(pref_storage) {
    var keyToIdMap = {
        "show-western-links": "#cb-show-western",
        "show-byzantine-links": "#cb-show-byzantine",
        "show-audio-links": "#cb-show-audio",
        "show-pdf-links": "#cb-show-pdf",
        "show-textmusic-links": "#cb-show-textmusic",
        "show-en-links": "#cb-show-en",
        "show-gr-links": "#cb-show-gr",
        "show-gren-links": "#cb-show-gren"
    }
    var prefs = {};

    Object.keys(keyToIdMap).map((key) => {
        var prefValue = pref_storage.getKeyValue(key, true);
        $(keyToIdMap[key]).prop("checked", prefValue);
        prefs[key] = prefValue;
    });

    console.log(prefs);

    $("#pref-save-btn").click(function() {
        console.log("Saving preferences...");
        Object.keys(keyToIdMap).map((key) => {
            pref_storage.setKeyValue(key, $(keyToIdMap[key]).prop("checked"));
        });
        $("#pref-messages").html("Preferences saved!<br>Click Return to go back to your previous page.");
    });

    $("#pref-return-btn").click(function() {
    	window.history.back()
    });

    // Service listing for date
    if (prefs["show-pdf-links"] === false) {
        $("a.index-file-link").each((i, obj) => {
            if ($(obj).html() == "Print") {
                $(obj).parent().parent().css("display", "none");
            }
        })
    }

    if (prefs["show-textmusic-links"] === false) {
        $("a.index-file-link").each((i, obj) => {
            if ($(obj).html() == "View") {
                $(obj).parent().parent().css("display", "none");
            }
        })
    }

    if (prefs["show-en-links"] === false) {
        $("span.index-language").each((i, obj) => {
            if ($(obj).html() == "EN") {
                $(obj).parent().parent().css("display", "none");
            }
        })
    }

    if (prefs["show-gren-links"] === false) {
        $("span.index-language").each((i, obj) => {
            if ($(obj).html() == "GR-EN") {
                $(obj).parent().parent().css("display", "none");
            }
        })
    }

    if (prefs["show-gr-links"] === false) {
        $("span.index-language").each((i, obj) => {
            if ($(obj).html() == "GR") {
                $(obj).parent().parent().css("display", "none");
            }
        })
    }

    // Media links
    if (prefs["show-byzantine-links"] === false) {
        $("span.media-icon > i.fa-byznote").each((i, obj) => {
            $(obj).css("display", "none");
        })
    }

    if (prefs["show-western-links"] === false) {
        $("i.glyphicon-music").each((i, obj) => {
            $(obj).css("display", "none");
        })
    }

    if (prefs["show-audio-links"] === false) {
        $("i.glyphicon-volume-up").each((i, obj) => {
            $(obj).css("display", "none");
        })
    }

});
