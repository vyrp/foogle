var userLogged = false;

window.fbAsyncInit = function() {
    FB.init({ 
        //appId      : '394904207304456',                        // ID for Deploy
        appId      :  '336910786453085',                         // ID for local
        status     : true,                                       // Check Facebook Login status
        xfbml      : true                                        // Look for social plugins on the page
        //channelUrl : '//appfoogle.appspot.com/channel.html',   // Channel file for x-domain comms
    });

    FB.Event.subscribe('auth.authResponseChange', function(response) {
    
        if (response.status === 'connected')
        {
            console.log('connected');
            userLogged = true;
            
            var authResponse = FB.getAuthResponse();
            $.post('populate', {'access_token': authResponse.accessToken}, function(response){
                console.log(response.status);
            }, "json");
        }
        else if (response.status === 'not_authorized')
        {
            console.log('not authorized');
            userLogged = false;
        }
        else
        {
            console.log('not logged');
            userLogged = false;
        }
        
    });
};

// Load the SDK asynchronously
// (function(d, s, id){
    // var js, fjs = d.getElementsByTagName(s)[0];
    // if (d.getElementById(id)) {return;}
    // js = d.createElement(s); js.id = id;
    // js.src = "//connect.facebook.net/en_US/all.js";
    // fjs.parentNode.insertBefore(js, fjs);
// }(document, 'script', 'facebook-jssdk'));

(function() {
    var e = document.createElement('script');
    e.type = 'text/javascript';
    e.src = document.location.protocol + '//connect.facebook.net/en_US/all.js';
    e.async = true;
    document.getElementById('fb-root').appendChild(e);
}());