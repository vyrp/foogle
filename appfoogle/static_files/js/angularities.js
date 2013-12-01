var foogleApp = angular.module('foogleApp', []);

function mainCtrl($scope){
	
}


function searchBar($scope){
	$scope.search=function(){
		$.post(
	      "/search",
	      JSON.stringify({
			"uid":1,
			"sentence":$scope.data.query,
			"filter":"cmp"
		   }),
	      function(response) {
	      	data=JSON.parse(response).data;
	      	/// 
	      	for(i in data){
	      		data[i].type='p';
	      		switch(data[i].type){
	      			case 'm':
		      			message_id="388551281214203_133771";//data.fbid
		      			timestamp="1378684085";//data.timestamp
		      			delta=300;
		      			queryMessage(message_id,timestamp,delta,function(response){
		      				 
		      			});
	      			break;
	      			case 'p':
	      				post_id="100001603548199_589109644485815";//data.fbid
		      			timestamp="1378670958";//data.timestamp
		      			queryPost(post_id,function(response){
		      				 
		      			});
	      			break;
	      			case 'c':
	      			break;
	      		}
	      	}
	      });
	}
}	

