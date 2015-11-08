var JobMapsApp = angular.module('JobMapsApp', []);
 
JobMapsApp.controller('JobListCtrl', ['$scope', '$http',
  function PhoneListCtrl($scope, $http) {
    $http.get('jobs').success(function(data) {
      $scope.jobs = data;
    });
    $scope.orderProp = 'dateCreated';
  }
]);
 
JobMapsApp.controller('JobDetailCtrl', ['$scope', '$routeParams',
  function($scope, $routeParams) {
    $scope.phoneId = $routeParams.phoneId;
  }
]);