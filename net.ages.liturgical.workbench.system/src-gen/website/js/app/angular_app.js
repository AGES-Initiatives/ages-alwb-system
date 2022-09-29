define("alwb", ["require", "angular", "angular_app", "pref_storage"], function(require, angular)
{
    var alwb = angular.module("alwb", []);

    angular.element(document).ready(function()
        { angular.bootstrap(document,[]); }
    );

    alwb.controller('StaticCtrl', function StaticCtrl($scope) {
        $scope.countries = {
            'usa': {
                'San Francisco': ['SOMA', 'Richmond', 'Sunset'],
                'Los Angeles': ['Burbank', 'Hollywood']
            },
            'canada': {
                'People dont live here': ['igloo', 'cave']
            }
        };
    });
});
