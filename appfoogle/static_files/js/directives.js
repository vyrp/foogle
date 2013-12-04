foogleApp.directive("searchbar", function(){
  return {
    restrict: "E",
    templateUrl: "/searchbar.html",
    link: function(scope, element,attrs){
      element.children(0).addClass(attrs.cssclass);
    }
  }
});