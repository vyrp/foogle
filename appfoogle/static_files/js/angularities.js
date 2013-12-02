var foogleApp = angular.module('foogleApp', []);
foogleApp.factory('Data', function(){
	return {dropped: false, query: ""};
})

function frontendCtrl($scope, Data){
	$scope.data = Data;

	$scope.invertDropdown= function(){

	}
}

function searchBar($scope, Data){
	$scope.data = Data;

	$scope.search=function(){
		alert($scope.data.query)
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
	      		data[i].type='c';
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
		      				 console.log(response);
		      			});
	      			break;
	      			case 'c':
	      				comment_id="411272562322429";//data.fbid
		      			timestamp="1378670958";//data.timestamp
		      			queryComment(comment_id,function(response,post_data){
		      				 console.log(response);
		      				 console.log(post_data);
		      			});
	      			break;
	      		}
	      	}
	      });
	}
}	

