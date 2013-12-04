foogleApp.directive("searchbar", function(){
  return {
    restrict: "E",
    templateUrl: "/searchbar.html",
    link: function(scope, element,attrs){
      element.children(0).addClass(attrs.cssclass);
    }
  }
});

foogleApp.directive("messageresult", function(){
  return {
    restrict: "E",
    templateUrl: "/templatemessage.html"
  }
});

foogleApp.directive("postresult", function(){
  return {
    restrict: "E",
    templateUrl: "/templatepost.html"
  }
});

foogleApp.directive("commentresult", function(){
  return {
    restrict: "E",
    templateUrl: "/templatecomment.html"
  }
});