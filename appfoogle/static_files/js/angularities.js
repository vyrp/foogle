var foogleApp = angular.module('foogleApp', []);
foogleApp.factory('Data', function(){
    return {
        searchscreen: true,
        dropped: false, 
        query: "",
        alloptions: true,
        posts: true,
        comments: true,
        chat:true
    };
})

function miscCtrl($scope, Data){
    $scope.data = Data;
}

function searchBar($scope, Data){
    $scope.data = Data;

    $scope.searchTypeChange=function(current){
        slaves = document.getElementsByName("slave-checkbox");
        master = document.getElementsByName("master-checkbox")[0];
        if(current=="master-checkbox"){
            $scope.data.posts = $scope.data.alloptions;
            $scope.data.comments = $scope.data.alloptions;
            $scope.data.chat = $scope.data.alloptions;
        }else{
            $scope.data.alloptions = $scope.data.posts && $scope.data.comments && $scope.data.chat;
        }
    }

    $scope.invertDropdown=function(current){
        $scope.data.dropped = !current;
    }


    $scope.search=function(){
        $scope.data.dropped = false;
        if($scope.data.query.length>0){
            var authResponse = FB.getAuthResponse();
            if(authResponse == undefined){
                window.setTimeout(function() {$scope.search()}, 100);
                return;
            }
            access_token=authResponse.accessToken;
            if(access_token==undefined){
                alert("Please, log in our app.");
                return;
            }
            var custom_filter = "";
            if($scope.data.alloptions){
                custom_filter = "cmp";
            }else{
                custom_filter += $scope.data.comments ? "c" : "";
                custom_filter += $scope.data.chat ? "m" : "";
                custom_filter += $scope.data.posts ? "p" : "";
            }

            json = {
                "access_token":access_token,
                "sentence":$scope.data.query,
                "filter": custom_filter
            };

            if($scope.data.from != undefined){
                timestamp = getTimestamp($scope.data.from);
                if(timestamp != NaN){
                    json.from = timestamp;
                }
            }
            
            if($scope.data.to != undefined){
                timestamp = getTimestamp($scope.data.to);
                if(timestamp != NaN){
                    json.to = timestamp;
                }
            }
            
            alert("Pesquisa: " + $scope.data.query + " at filter: " + custom_filter);
            console.log(json);
            $.post(
                "/search",
                JSON.stringify(json),
                function(response) {
                    data=JSON.parse(response).data;
                    console.log(data);
                    for(i in data){
                        data[i].type='m';
                        switch(data[i].type){
                            case 'm':
                              message_id="466050320176931_168";//data.fbid
                              timestamp="1385963939";//data.timestamp
                              delta=10000;
                              queryMessage(message_id,timestamp,delta,function(response){
                                console.log(response);
                              });
                              break;
                              case 'p':
                              post_id="100000099637951_411059209010431";//data.fbid
                              console.log(getPostLink(post_id));
                              queryPost(post_id,function(response){
                                  console.log(response);
                              });
                              break;
                              case 'c':
                              comment_id="411272562322429";//data.fbid
                              queryComment(comment_id,function(response,post_data){
                                  console.log(response);
                                  console.log(post_data);
                                  post_id = post_data[0].post_id;
                                  console.log(getPostLink(post_id));
                              });
                              break;
                          }
                      }
                  });
}
}
}    

