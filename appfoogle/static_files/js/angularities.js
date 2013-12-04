var foogleApp = angular.module('foogleApp', []);
foogleApp.factory('Data', function(){
    return {
searchscreen: true,
resultscreen: false,
dropped: false, 
query: "",
alloptions: true,
posts: true,
comments: true,
chat:true,
results:[]
    };
})

function miscCtrl($scope, Data){
    $scope.data = Data;
}

function resultsCtrl($scope, Data){
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
        if($scope.data.query.length>0 && userLogged){
    
            $scope.data.results = [];
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

            console.log("Pesquisa: " + $scope.data.query + " at filter: " + custom_filter);
            console.log(json);
            $.post(
            "/search",
            JSON.stringify(json),
            function(response) {
                data=JSON.parse(response).data;
                console.log(data);
                for(i in data){
                    var single_result = {};
                    data[i].type='m';
                    switch(data[i].type){
                    case 'm':
                        //message_id="388551281214203_154007";
                        //timestamp=1386107311;

                        message_id="466050320176931_168";//data.fbid
                        timestamp="1385963939";//data.timestamp
                        delta=1000;
                        queryMessage(message_id,timestamp,delta,function(response,conversation_id,isgrouptalk){
                            single_result.response = response;
                            // console.log(response);
                            single_result.conversation_id = conversation_id;
                            // console.log(conversation_id);
                            single_result.isgrouptalk = isgrouptalk;
                            // console.log(isgrouptalk);
                            var mess_link = getMessageLink(conversation_id,isgrouptalk);
                            single_result.mess_link = mess_link;
                            // console.log(mess_link);
                        });

                        break;
                    case 'p':
                        post_id="100000099637951_411059209010431";//data.fbid
                        console.log(getPostLink(post_id));
                        queryPost(post_id,function(response){
                            single_result.response = response;
                            // console.log(response);
                        });
                        break;
                    case 'c':
                        comment_id="411272562322429";//data.fbid
                        queryComment(comment_id,function(response,post_data){
                            single_result.response = response;
                            // console.log(response);
                            single_result.post_data = post_data;
                            // console.log(post_data);
                            post_id = post_data[0].post_id;
                            single_result.post_link = post_link;
                            var post_link = getPostLink(post_id);
                            // console.log(post_link);
                        });
                        break;
                    }
                    $scope.data.results.push(single_result);
                }
                console.log($scope.data.results);
            });
            $scope.data.searchscreen = false;
            $scope.data.resultscreen = true;
        }else if(!userLogged){
            alert("Please login to use the app.");
        }
  }
}