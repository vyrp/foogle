window.fbAsyncInit = function() {
  // init the FB JS SDK
  FB.init({ 
   // appId      : '394904207304456',                        // ID for Deploy
    appId       :  '336910786453085',                        // ID for local
    channelUrl : '//appfoogle.appspot.com/channel.html', // Channel file for x-domain comms
    status     : true,                                 // Check Facebook Login status
    xfbml      : true                                  // Look for social plugins on the page
  });
  
  // Additional initialization code such as adding Event Listeners goes here

  FB.Event.subscribe('auth.authResponseChange', function(response) {
		if (response.status === 'connected') {
			testAPI();
		} else if (response.status === 'not_authorized') {
			FB.login();
		} else {
			FB.login();
		}
	});
};

// Load the SDK asynchronously
(function(d, s, id){
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) {return;}
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/all.js";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
 
function testAPI() {
  console.log('Welcome!  Fetching your information.... ');
  FB.api(
  {
    method: 'fql.query',
    query: 'SELECT body FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0) ORDER BY created_time DESC'
  },
  function(response) {
		createDiccionary(response);
  });
} 
