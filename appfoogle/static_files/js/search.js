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
			console.log("got thread_id");  	
		  	queryMessage(message_id,timestamp,Math.floor(delta),callback,thread_id,isgrouptalk,conversation_id);
		  });
  		return;
	}
	console.log("querying with delta " + delta);  	
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




