var blogApp = angular.module('blogApp', [
	'ngRoute',
	'infinite-scroll',
	'ui.tinymce',
	'sn.addthis',
	'ngFileUpload',
	'angulartics',
	'angulartics.google.analytics',
	'blogAppControllers']);

blogApp.config(['$routeProvider',
	function($routeProvider) {
		$routeProvider
		.when('/posts/:year/:month/:day/:shortUrl', {
			templateUrl: 'partials/post.html',
			controller: 'MainCtrl'
		})
		.when('/posts/tag/:tag', {
			templateUrl: 'partials/home.html',
			controller: 'MainCtrl'
		})
		.when('/add', {
			templateUrl: 'partials/add.html',
			controller: 'AddCtrl'
		})
		.when('/add/:year/:month/:day/:shortUrl', {
			templateUrl: 'partials/add.html',
			controller: 'AddCtrl'
		})
		.when('/image-upload', {
			templateUrl: 'partials/image-upload.html',
			controller: 'UploadCtrl'
		})
		.when('/', {
			templateUrl: 'partials/home.html',
			controller: 'MainCtrl'
		})
		.otherwise({
			redirectTo: '/'
		});
  	}
]);

blogApp.config(['$locationProvider',
	function($locationProvider) {
		// use the HTML5 History API
    	$locationProvider.html5Mode({ enabled: true, requireBase: true });
	}
]);