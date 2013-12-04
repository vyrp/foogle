function search($scope){
        
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
                    data[i].type='c';

                    switch(data[i].type){
                    case 'm':
                        //message_id="388551281214203_154007";
                        //timestamp=1386107311;
                        single_result.ismessage = true;
                        single_result.ispost = false;
                        single_result.iscomment = false;

                        message_id="466050320176931_168";//data.fbid
                        timestamp="1385963939";//data.timestamp
                        delta=1000;
                        queryMessage(message_id,timestamp,delta,function(response,conversation_id,isgrouptalk){
                            for (var index = 0; index < response.length; ++index){
                              var tempDate = new Date(response[index].created_time*1000);
                              var tempStr = tempDate.toGMTString();
                              response[index].created_time = tempStr.substring(0,tempStr.length - 4);
                            }
                            single_result.response = response;
                            console.log(response);
                            single_result.conversation_id = conversation_id;
                            // console.log(conversation_id);
                            single_result.isgrouptalk = isgrouptalk;
                            // console.log(isgrouptalk);
                            var mess_link = getMessageLink(conversation_id,isgrouptalk);
                            single_result.mess_link = mess_link;
                            // console.log(mess_link);
                            $scope.data.results.push(single_result);
                        });

                        break;
                    case 'p':
                        single_result.ismessage = false;
                        single_result.ispost = true;
                        single_result.iscomment = false;
                        post_id="100000099637951_411059209010431";//data.fbid
                        var post_link = getPostLink(post_id);
                        single_result.post_link = post_link;
                        // console.log(post_link);
                        queryPost(post_id,function(response){
                            for (var index = 0; index < response.length; ++index){
                              var tempDate = new Date(response[index].created_time*1000);
                              var tempStr = tempDate.toGMTString();
                              response[index].created_time = tempStr.substring(0,tempStr.length - 4);
                            }
                            single_result.response = response;
                            console.log(response);
                            $scope.data.results.push(single_result);
                        });
                        break;
                    case 'c':
                        single_result.ismessage = false;
                        single_result.ispost = false;
                        single_result.iscomment = true;
                        comment_id="411272562322429";//data.fbid
                        queryComment(comment_id,function(response,post_data){
                            single_result.response = response;
                            console.log(response);
                            single_result.post_data = post_data;
                            console.log(post_data);
                            post_id = post_data[0].post_id;
                            single_result.post_link = post_link;
                            var post_link = getPostLink(post_id);
                            // console.log(post_link);
                            $scope.data.results.push(single_result);

                        });
                        break;
                    }
                 //   $scope.data.results.push(single_result);
                }
                console.log($scope.data.results);
                console.log("o.O");
            });
            $scope.data.searchscreen = false;
            $scope.data.resultscreen = true;
        }else if(!userLogged){
            alert("Please login to use the app.");
        }
  }





function getNameAndPhoto(response,uidfunc,callback){
	uidlist = [];
	for(var i=0;i<response.length;i++){
		uidlist.push(uidfunc(response[i]));
	}
	query = "SELECT uid,name, pic_small FROM user WHERE uid IN \(\"" + uidlist.join('", "') + "\"\)"
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(users) {
	  	for(var i=0;i<response.length;i++){
			for(var j = 0; j<users.length ;j++){
				if(uidfunc(response[i]) == users[j].uid){
					response[i].pic = users[j].pic_small;
					response[i].name = users[j].name;
					break;
				}	
			}
		}

	  	callback(response);
		return;
	  	
	  });
	return;

}




function queryMessage(message_id,timestamp,delta,callback, thread_id, isgrouptalk, conversation_id){
	timestamp=parseInt(timestamp);
	delta=parseInt(delta);
	if(delta==0)return;
	if(thread_id == undefined){

		query = "SELECT recipients,thread_id,viewer_id FROM thread WHERE thread_id IN \(" + 'SELECT thread_id FROM message WHERE message_id="' + message_id + '"\)'
  		FB.api(
		  {
		    method: 'fql.query',
		    query: query
		  },
		  function(response) {
		  	recipients = response[0].recipients;
		  	isgrouptalk = recipients.length>2;
		  	thread_id = response[0].thread_id;	
		  	if(isgrouptalk){
		  		conversation_id = thread_id;
		  	}
		  	else{
		  		conversation_id = response[0].viewer_id == recipients[0]?recipients[1]:recipients[0];
		  	}
			// console.log("got thread_id");  	
		  	queryMessage(message_id,timestamp,Math.floor(delta),callback,thread_id,isgrouptalk,conversation_id);
		  });
  		return;
	}
	// console.log("querying with delta " + delta);  	
	uplimit=(timestamp+delta);
	lowlimit=(timestamp-delta);
	query='SELECT body,message_id,author_id,created_time FROM message WHERE thread_id = "' + thread_id + '"  AND created_time>=' + lowlimit + ' AND created_time<=' + uplimit + ' ORDER BY created_time DESC';
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	 
	  	if(JSON.stringify(response).indexOf(message_id)!=-1){

	  		getNameAndPhoto(response,function(x){return x.author_id},function(newresponse){
	  			callback(newresponse,conversation_id,isgrouptalk);
	  		});
	  	}
	  	else{
	  		queryMessage(message_id,timestamp,Math.floor(delta/2),callback,thread_id,isgrouptalk,conversation_id);
	  	}
	  });
}



function queryPost(post_id,callback){
	query='SELECT post_id,message,actor_id,like_info,share_info,created_time FROM stream WHERE post_id="' + post_id + '"';	 
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	getNameAndPhoto(response,function(x){return x.actor_id},function(newresponse){

	  		callback(newresponse);
	  	});
	  	
	  });
}

function queryComment(comment_id,callback){
	query='SELECT likes,text,post_id,fromid,id,time FROM comment WHERE id="' + comment_id + '"';	 
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	post_id=response[0].post_id;
	  	queryPost(post_id,function(post_data){
	  		getNameAndPhoto(response,function(x){return x.fromid},function(newresponse){
	  			callback(newresponse,post_data);
	  		});
	  		
	  	});

	  	
	  });
}

function getPostLink(post_id){
	return "https://www.facebook.com/" + post_id.split("_").join("/posts/");
}

function getMessageLink(conversation_id,isgrouptalk){
	if(!isgrouptalk){
		return "https://www.facebook.com/messages/" + conversation_id;	
	}
	return "https://www.facebook.com/messages/conversation-id." + conversation_id;
}




