window.fbAsyncInit = function() {
  // init the FB JS SDK
  FB.init({ 
    appId      : '394904207304456',                        // ID for Deploy
    //appId       :  '336910786453085',                        // ID for local
    channelUrl : '//appfoogle.appspot.com/channel.html', // Channel file for x-domain comms
    status     : true,                                 // Check Facebook Login status
    xfbml      : true                                  // Look for social plugins on the page
  });
  
  // Additional initialization code such as adding Event Listeners goes here
  

  FB.Event.subscribe('auth.authResponseChange', function(response) {
  // Here we specify what we do with the response anytime this event occurs. 
  if (response.status === 'connected') {
    // The response object is returned with a status field that lets the app know the current
    // login status of the person. In this case, we're handling the situation where they 
    // have logged in to the app.
    console.log('connected');
    testAPI();
  } else if (response.status === 'not_authorized') {
    // In this case, the person is logged into Facebook, but not into the app, so we call
    // FB.login() to prompt them to do so. 
    // In real-life usage, you wouldn't want to immediately prompt someone to login 
    // like this, for two reasons:
    // (1) JavaScript created popup windows are blocked by most browsers unless they 
    // result from direct interaction from people using the app (such as a mouse click)
    // (2) it is a bad experience to be continually prompted to login upon page load.
    console.log('not_authorized');
    FB.login();
  } else {
    // In this case, the person is not logged into Facebook, so we call the login() 
    // function to prompt them to do so. Note that at this stage there is no indication
    // of whether they are logged into the app. If they aren't then they'll see the Login
    // dialog right after they log in to Facebook. 
    // The same caveats as above apply to the FB.login() call here.
    console.log('not logged');
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
    query: 'SELECT body, message_id FROM message WHERE thread_id IN (SELECT thread_id FROM thread WHERE folder_id=0) ORDER BY created_time DESC'
  },
  function(response) {
    // createDiccionary(response);
  });
} 
