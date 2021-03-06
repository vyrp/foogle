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
loading:true,
results:[]
    };
})

var i=1;
var foi=false;
var respostas = 0;
var max = 0
var set;
var rmax=0;

function updateNewSearch($scope,result,rate){
    if(result!=undefined){
        set.push(result);
    }
    console.log(respostas);
    
    

    respostas++;
    if(respostas==max || respostas%1==0){
        
        console.log("length antigo" + set.length)
        
        console.log(set);
        
        console.log("ai vai")
        console.log(set);
        console.log("length " + set.length)
        for(var i=0;i<set.length;i++){
            if(rate>rmax){
                rmax=rate;
                aux=$scope.data.results[0];
                $scope.data.results[0]=set[i];
                $scope.data.results.push(aux);
            
            }else
            {
                $scope.data.results.push(set[i]);
            }
            
            
            
        }
    
        $scope.$digest();
        set=[]
        console.log("digeriu")
      }
    if(!foi)window.setTimeout(function(){
         $( "#datepicker21" ).datepicker(
        {
          onSelect: function(dateText, inst){
            $("#datepicker22").datepicker("option", "minDate", $.datepicker.parseDate("dd/mm/yy", dateText));
          }
        });
        $( "#datepicker22" ).datepicker();

        $( "#datepicker22" ).datepicker('setDate', $.datepicker.parseDate("dd/mm/yy", $("#datepicker12").val()));
        $( "#datepicker21" ).datepicker('setDate', $.datepicker.parseDate("dd/mm/yy", $("#datepicker11").val()));

    },100);
    foi=true;
    
}

function miscCtrl($scope, Data){
    $scope.data = Data;
    $scope.count = 0;

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

    $scope.search=function(){
        rmax=0;
        $scope.data.dropped = false;
        if($scope.data.query.length>0 && userLogged){
            $scope.data.loading = true;
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
                set = [];
                data=JSON.parse(response).data;
                max=data.length;
                console.log(data);
                for(i in data){
                    $scope.data.loading=true;
                    var single_result = {};

                    //data[i].type='p';
                    try{(function(i,single_result){
                        switch(data[i].type){
                        case 'm':
                            //message_id="388551281214203_154007";
                            //timestamp=1386107311;
                            single_result.ismessage = true;
                            single_result.ispost = false;
                            single_result.iscomment = false;

                            //message_id="466050320176931_168";//data.fbid
                            //timestamp="1385963939";//data.timestamp
                            message_id = data[i].fbid;
                            timestamp = data[i].timestamp;
                            
                            
                            
                            delta=1000;
                            queryMessage(message_id,timestamp,delta,function(response,conversation_id,isgrouptalk,user){
                                console.log("entrou em mensagens ")
                                console.log(response)
                                for (var index = 0; index < response.length; ++index){
                                  var tempDate = new Date(response[index].created_time*1000);
                                  var tempStr = tempDate.toUTCString();
                                  response[index].created_time = tempStr.substring(0,tempStr.length - 4);
                                }
                                single_result.response = response;
                                // console.log(response);
                                single_result.conversation_id = conversation_id;
                                // console.log(conversation_id);
                                single_result.isgrouptalk = isgrouptalk;
                                // console.log(isgrouptalk);
                                var mess_link = getMessageLink(conversation_id,isgrouptalk);
                                single_result.mess_link = mess_link;
                                // console.log(mess_link);
                                //set.push(single_result);
                                //$scope.data.results.push(single_result);
                                $scope.data.loading = false;
                                updateNewSearch($scope,single_result,data[i].rate)
                            });

                            break;
                        case 'p':
                            single_result.ismessage = false;
                            single_result.ispost = true;
                            single_result.iscomment = false;
                            //post_id="100000099637951_411059209010431";//data.fbid
                            post_id = data[i].fbid;
                            var post_link = getPostLink(post_id);
                            single_result.post_link = post_link;
                            // console.log(post_link);
                            queryPost(post_id,function(response){
                                for (var index = 0; index < response.length; ++index){
                                  var tempDate = new Date(response[index].created_time*1000);
                                  var tempStr = tempDate.toUTCString();
                                  response[index].created_time = tempStr.substring(0,tempStr.length - 4);
                                }
                                single_result.response = response;
                                // console.log(response);
                                //set.push(single_result);
                                //$scope.data.results.push(single_result);
                                $scope.data.loading = false;
                                updateNewSearch($scope,single_result,data[i].rate)

                            });
                            break;
                        case 'c':
                            single_result.ismessage = false;
                            single_result.ispost = false;
                            single_result.iscomment = true;
                            //comment_id="411272562322429";//data.fbid
                            
                            comment_id = data[i].fbid;
                            
                            queryComment(comment_id,function(response,post_data){
                                for (var index = 0; index < response.length; ++index){
                                  var tempDate = new Date(response[index].time*1000);
                                  var tempStr = tempDate.toUTCString();
                                  response[index].time = tempStr.substring(0,tempStr.length - 4);
                                }
                                single_result.response = response;
                                // console.log(response);
                                for (var index = 0; index < post_data.length; ++index){
                                  var tempDate = new Date(post_data[index].created_time*1000);
                                  var tempStr = tempDate.toUTCString();
                                  post_data[index].created_time = tempStr.substring(0,tempStr.length - 4);
                                }
                                single_result.post_data = post_data;
                                // console.log(post_data);
                                try{
                                    post_id = post_data[0].post_id;
                                  }
                                  catch(er){
                                    updateNewSearch($scope,undefined)
                                    return;
                                  }
                                var post_link = getPostLink(post_id);
                                single_result.post_link = post_link;
                                // console.log(post_link);
                                //set.push(single_result);
                                //$scope.data.results.push(single_result);
                                $scope.data.loading = false;
                                updateNewSearch($scope,single_result,data[i].rate)
                            });
                            break;
                        }
                    })(i,single_result);}
                    catch(e){
                        respostas++;
                    }
                 //   $scope.data.results.push(single_result);
                }
                // console.log($scope.data.results);
                console.log("o.O");
            });
            $scope.data.searchscreen = false;
            $scope.data.resultscreen = true;
        }else if(!userLogged){
            alert("Please login to use the app.");
        }
  }
}

function resultsCtrl($scope, Data){
    $scope.data = Data;
    $scope.count = 1;
}

function searchCtrl($scope, Data){
    
    $scope.data = Data;    
    $scope.count = 42;
    $scope.invertDropdown=function(current){
        $scope.data.dropped = !current;
    }


    
}
