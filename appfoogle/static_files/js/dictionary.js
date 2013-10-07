function normalize(word){
  
}

function createDiccionary(json){
  dic = {};
  for(var i=0; i<json.length; i++){
    var words = json[i].body.split(' ');
    for(var j=0; j<words.length; j++){
      word = normalize(words[j]);
    }
  }
}