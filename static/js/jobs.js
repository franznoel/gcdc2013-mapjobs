var jobs = angular.module('jobs',['ngRoute','phoneControllers']);

jobs.controller('')



/*jobs.config(['$routeProvider',
  function($routeProvider) {
    $routeProvider
      .when('/jobs/create',{templateUrl:'partials/jobs-create-form.html',controller:'JobCreateCtrl'})
      .when('/job/:jobId/update',{templateUrl:'partials/jobs-update-form.html',controller:'jobUpdateCtrl'})
      .otherwise({redirectTo:'/job'})
  }
]);

jobs.factory('Jobs',['$resources',
  function($resource) {
    return $resource('job/:jobId.json',{},{
      query: {method:'GET',params:{jobId:'jobs'},isArray:true}
    });
  }
]);
*/



