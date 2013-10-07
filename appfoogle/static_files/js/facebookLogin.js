window.fbAsyncInit = function() {
  // init the FB JS SDK
  FB.init({
    appId      : '394904207304456',                        // App ID from the app dashboard
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
    query: 'SELECT body FROM message WHERE thread_id=388551281214203 ORDER BY created_time DESC LIMIT 100 OFFSET 139000'/*IN (SELECT thread_id FROM thread WHERE folder_id=1 LIMIT 1000) ORDER BY created_time DESC LIMIT 2000 OFFSET 1000'*/
  },
  function(response) {
    console.log(response);
		createDiccionary(response);
  });
} 
