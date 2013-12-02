function queryMessage(message_id,timestamp,delta,callback){
	timestamp=parseInt(timestamp);
	delta=parseInt(delta);
	if(delta==0)return;
	uplimit=(timestamp+delta);
	lowlimit=(timestamp-delta);
	query='SELECT body,message_id,author_id FROM message WHERE thread_id IN \(SELECT thread_id FROM message WHERE message_id="' + message_id + '"\)  AND created_time>=' + lowlimit + ' AND created_time<=' + uplimit + ' ORDER BY created_time DESC';
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	 
	  	if(JSON.stringify(response).indexOf(message_id)!=-1){
	  		callback(response);
	  	}
	  	else{
	  		queryMessage(message_id,timestamp,Math.floor(delta/2),callback);
	  	}
	  });
}



function queryPost(post_id,callback){
	query='SELECT message,actor_id,like_info,share_info FROM stream WHERE post_id="' + post_id + '"';	 
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	callback(response);
	  });
}

function queryComment(comment_id,callback){
	query='SELECT message,actor_id,like_info,share_info FROM stream WHERE post_id="' + comment_id + '"';	 
	FB.api(
	  {
	    method: 'fql.query',
	    query: query
	  },
	  function(response) {
	  	callback(response);
	  });
}



