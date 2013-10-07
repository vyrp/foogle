function verify(array, json){
  for(var i=0; i<array.length; i++){
    console.log(i + " <<" + json[array[i]] + ">>");
  }
}

function transform(json){
  dic = {};
  for(var i=0; i<json.length; i++){
    dic[json[i].message_id] = json[i].body;
  }
  return dic;
}

function size(dictionary){
  var sum = 0;
  for(var elem in dictionary){
    sum++;
  }
  return sum;
}

function max(dictionary){
  var m = 0;
  var mElem = "xxx";
  for(var elem in dictionary){
    if(dictionary[elem].length > m){
      m = dictionary[elem].length;
      mElem = elem;
    }
  }
  return [m, mElem];
}

function normalize(word){
  return word.toLowerCase()
             .replace(/[бвагд]/, 'a')
             .replace(/[йкил]/, 'e')
             .replace(/[номп]/, 'i')
             .replace(/[уфтхц]/, 'o')
             .replace(/[ъыщь]/, 'u')
             .replace(/[эя]/, 'y')
             .replace(/з/, 'c')
             .replace(/с/, 'n')
             .replace(/^[^a-zA-Z0-9]+/, '')
             .replace(/[^a-zA-Z0-9]+$/, '');
}

function createDiccionary(json){
  console.log("Number of messages: " + size(json));
  var dic = {};
  var total = 0;
  for(var i=0; i<json.length; i++){
    var words = json[i].body.split(/\s/);
    var id = json[i].message_id;
    for(var j=0; j<words.length; j++){
      var word = normalize(words[j]);
      if(word === ""){
        continue;
      }
      total++;
      if(dic[word] === undefined){
        dic[word] = [id];
      } else {
        dic[word] = dic[word].concat(id);
      }
    }
  }
  console.log("Number of total words: " + total);
  console.log("Number of different words: " + size(dic));
  var M = max(dic);
  console.log("Most common word: " + M[1] + ", with " + M[0] + " entries.");
  console.log(dic);
  //return dic;
}