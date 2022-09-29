define(function() {
    var agesStorage = window.localStorage;
    var test = 'test';
    function localStorageTest() {
        try {
            localStorage.setItem(test, test);
            localStorage.removeItem(test);
            return true;
        } catch(e) {
            console.warn("LocalStorage unavailable. Preferenes will not work.")
            return false;
        }
    }
    
    if (localStorageTest() === true)
        return {
            setKeyValue: function(key, value) {
                // console.log(`Storing ${key} = ${value}`);
                agesStorage.setItem(key, value);
            },

            getKeyValue: function(key, default_value) {
                // console.log(`Getting value for ${key}`);
                if (agesStorage.hasOwnProperty(key)) {
                    // JSON.parse to handle booleans
                    return JSON.parse(agesStorage.getItem(key));
                } else {
                    return default_value;
                }
            }
        }
    else
        return false;
});
