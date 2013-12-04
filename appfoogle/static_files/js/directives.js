foogleApp.directive("searchbar", function(){
  return {
    restrict: "E",
    templateUrl: "/searchbar.html",
    link: function(scope, element,attrs){
      element.children().addClass(attrs.cssclasszero);
      element.children().next().removeClass(attrs.cssclasszero);
      element.children().next().addClass(attrs.cssclassone);
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