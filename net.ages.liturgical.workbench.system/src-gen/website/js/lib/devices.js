var isMobile = {
    Android: function() {
        return (navigator.userAgent.match(/Android/i) != null);
    },
    BlackBerry: function() {
        return (navigator.userAgent.match(/BlackBerry/i) != null);
    },
    iOS: function() {
        return (navigator.userAgent.match(/iPhone|iPad|iPod/i) != null);
    },
    iPhone: function() {
        return (navigator.userAgent.match(/iPhone/i) != null);
    },
    iPad: function() {
        return (navigator.userAgent.match(/iPad/i) != null);
    },
    iPod: function() {
        return (navigator.userAgent.match(/iPod/i) != null);
    },
    Opera: function() {
        return (navigator.userAgent.match(/Opera Mini/i) != null);
    },
    Windows: function() {
        return (navigator.userAgent.match(/IEMobile/i) != null);
    },
    any: function() {
        return (isMobile.Android() || isMobile.BlackBerry() || isMobile.iOS() || isMobile.Opera() || isMobile.Windows());
    }
};

if (isMobile.any()) {
	document.location = "servicesindex.html"
} else {
	document.location = "dcs.html"
}
