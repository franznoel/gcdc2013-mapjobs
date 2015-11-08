var JobMaps = angular.module('JobMaps', ['MenuCtrl','google-maps']); 
  JobMaps.config(['$routeProvider',
    function($routeProvider) {
      $routeProvider
        .when('/jobs/', {templateUrl: 'templates/job.html',controller: 'JobListCtrl'})
        .when('/job/:jobId', {templateUrl: 'templates/job.html', controller: 'JobDetailCtrl'})
        .when('/resume/', {templateUrl: 'templates/resume.html',controller: 'ResumeListCtrl'})
        .when('/resume/:resumeId', {templateUrl: 'templates/resume.html', controller: 'ResumeDetailCtrl'})
        .when('/profile/', {templateUrl: 'templates/profile.html',controller: 'ProfileListCtrl'})
        .when('/profile/:profileId', {templateUrl: 'templates/profile.html', controller: 'ProfileDetailCtrl'})
        .otherwise({redirectTo: '/',templateUrl: 'templates/default.html', controller: 'DefaultCtrl'});
    }
  ]);
  JobMaps.config(['$interpolateProvider',
    function($interpolateProvider) {
      $interpolateProvider.startSymbol('{[{');
      $interpolateProvider.endSymbol('}]}');
    }
  ]);

// Menu
var MenuCtrl = angular.module('MenuCtrl',[]);
  MenuCtrl.controller('MenuCtrl', function($scope,$location) {
    $scope.menus = [
      {'name': 'Jobs','link': 'jobs','active':''},
      {'name': 'Resume','link': 'resume','active':''},
      {'name': 'Profile','link': 'profile','active':''},
    ];
    $scope.isActive = function(route) {
      return route === $location.path();
    };
    $scope.log = function(route) {
      $log.log(route);
    }
    $scope.setActive = function(name) {
      ($window.mockWindow || $window).alert(name);
      ($window.mockWindow || $window).alert($scope.menus);;
      /*
      var menus = $scope.menus;
      for (var i=0;i<menus.length;i++) {
        if (menus[i].name==name) {
          menus[i].active = 'active';
        } else {
          menus[i].active = '';
        }
      }
      $scope.menus = menus;
      */
    }
  });
  
  MenuCtrl.directive('changeSize', function () {
    return {
      restrict: 'A',
      link: function($scope, $element, $attributes) {
        var onFocusSize = $attributes['changeSize'] || $element.attr('size');
        var onBlurSize = $element.attr('size');
        $element.focus(function() { $element.attr('size',onFocusSize); });
        $element.blur(function() { $element.attr('size',onBlurSize); });
      }
    }
  });
  
  /*
  angular.extend($scope, {
    center: {
      latitude: 0, // initial map center latitude
      longitude: 0, // initial map center longitude
    },
    markers: [], // an array of markers,
    zoom: 8, // the zoom level
  });
  */


function MapListCtrl() {
  
}

function JobListCtrl() {
}

function JobDetailCtrl() {
}

function ResumeListCtrl() {
}

function ResumeDetailCtrl() {
}

function ProfileListCtrl() {
}

function ProfileDetailCtrl() {
}

function DefaultCtrl() {
}

