var blogAppControllers = angular.module('blogAppControllers', []);

blogAppControllers.controller('MainCtrl',
    function ($scope, $http, $location, $routeParams, $rootScope, $sce) {
        $scope.error = false;
        $scope.start = 0;
        $scope.step = 5;
        var singlePost = false;

        var jsonDest = 'api/posts/list/' + $scope.start + '/' + $scope.step;
        if ($routeParams.shortUrl) {
            singlePost = true;
            jsonDest = ('api/posts/id/' +
                $routeParams.year + '/' +
                $routeParams.month + '/' +
                $routeParams.day + '/' +
                $routeParams.shortUrl);
        }
        else if ($routeParams.tag) {
            jsonDest = 'api/posts/tag/' + $routeParams.tag
        }
        $scope.loading = true;
        $http.get(jsonDest).then(function(response) {
            var data = response.data;
            if (data['status'] != 'ok') {
                $scope.loading = false;
                $scope.error_description = data['payload'];
                $scope.error = true;
                return;
            }
            $scope.posts = data['payload'][0];
            if (singlePost) {
                $rootScope.pageTitle = $scope.posts[0].title;
                $scope.is_user_auth = data['auth']
            } else {
                $rootScope.pageTitle = 'Francesco Pongetti, Engineer';
            }
            $scope.more = data['payload'][1];
            $scope.loading = false;
        });

        $scope.trustAsHtml = $sce.trustAsHtml;

        $scope.loadMore = function() {
            $scope.start += $scope.step;
            var jsonDest = 'api/posts/list/' + $scope.start + '/' + $scope.step;
            $http.get(jsonDest).success(function(data) {
                if (data['status'] != 'ok') {
                    return;
                }
                $scope.posts = $scope.posts.concat(data['payload'][0]);
                $scope.more = data['payload'][1];
            });
        }
    }
);


blogAppControllers.controller('AddCtrl',
    function ($scope, $http, $routeParams) {
        $scope.edit = false;
        $scope.loading = true;
        $scope.firstStep = true;
        $scope.done = false;
        $scope.tinymceOptions = {
            theme: 'modern',
            height: 250,
            plugins: [
                'advlist autolink lists link image charmap print preview hr anchor pagebreak',
                'searchreplace wordcount visualblocks visualchars code fullscreen',
                'insertdatetime media nonbreaking save table contextmenu directionality',
                'emoticons paste textcolor colorpicker textpattern imagetools'
            ],
            toolbar1: 'insertfile undo redo | styleselect | bold italic | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image',
            toolbar2: 'print preview media | forecolor backcolor emoticons',
            image_advtab: true,
            force_p_newlines : false,
            forced_root_block : '',
        };

        $http.get('api/tags/list').success(function(data) {
            if (data['status'] != 'ok') {
                return;
            }
            $scope.available_tags = data['payload']
        });

        // Declares a new object to avoid problem with AngularJs scopes in ng-repeat.
        $scope.post = {};
        $scope.form = {};

        if ($routeParams.shortUrl) {
            $scope.edit = true;
            jsonDest = ('api/posts/id/' +
                $routeParams.year + '/' +
                $routeParams.month + '/' +
                $routeParams.day + '/' +
                $routeParams.shortUrl);

            $http.get(jsonDest).then(function(response) {
                var data = response.data;
                if (data['status'] != 'ok') {
                    return;
                }
                $scope.post = data['payload'][0][0];
                $scope.form.title = $scope.post.title;
                $scope.form.content = $scope.post.content;
                $scope.form.hidden = $scope.post.hidden;
                $scope.form.tags = $scope.post.tags.join();
                $scope.form.short_url = $scope.post.shortUrl;
                $scope.loading = false;
            });
        } else {
            $scope.form.title = '';
            $scope.form.content = '';
            $scope.form.hidden = 0;
            $scope.form.tags = '';
            $scope.form.short_url = '';
            $scope.loading = false;
        }

        $scope.shortUrl = function() {
            if (!$scope.edit) {
                $scope.form.short_url = $scope.form.title.replace(/([^a-zA-Z0-9])/g, '-');
            }
        };
        $scope.tagClick = function(tag) {
            if ($scope.form.tags == '') {
                $scope.form.tags = tag;
            } else {
                $scope.form.tags = $scope.form.tags + ', ' + tag;
            }
        };
        $scope.addClick = function() {
            $scope.loading = true;
            var formData = {
                'title': $scope.form.title,
                'content':  $scope.form.content,
                'hidden': $scope.form.hidden,
                'tags': $scope.form.tags,
                'short_url': $scope.form.short_url,
                'edit': $scope.edit,
                'dateCompressed': $scope.post.dateCompressed,
            };
            formData = angular.toJson(formData);
            $http({
                method: 'post',
                url: 'api/posts/add',
                data: formData,
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .success(function(data) {
                $scope.done = true;
                $scope.firstStep = false;
                $scope.result = data;
                $scope.loading = false;
            });
        };
    }
);

blogAppControllers.controller('UploadCtrl',
    function ($scope, $rootScope, Upload, $timeout) {
        $rootScope.hideSidebar = true;
        $scope.uploadFiles = function(files, errFiles) {
            $scope.files = files;
            $scope.errFiles = errFiles;
            angular.forEach(files, function(file) {
                file.upload = Upload.upload({
                    url: 'api/image/upload',
                    data: {file: file}
                });

                file.upload.then(function (response) {
                    $timeout(function () {
                        file.result = response.data;
                    });
                }, function (response) {
                    if (response.status > 0)
                        $scope.errorMsg = response.status + ': ' + response.data;
                }, function (evt) {
                    file.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
                });
            });
        }
    }
);
