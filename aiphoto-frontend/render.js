// reference: https://www.freecodecamp.org/news/how-to-build-a-simple-speech-recognition-app-a65860da6108/
// reference: https://developer.mozilla.org/en-US/docs/Web/API/Document/createElement 
// reference: https://stackoverflow.com/questions/52722597/prevent-image-distortion-inside-a-resizing-container-with-css 
var fileExt = null;
var SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
const recognition = new SpeechRecognition();


function searchFromVoice() {
  recognition.start();

  recognition.onresult = (event) => {
    const speechToText = event.results[0][0].transcript;
    console.log(speechToText);

    document.getElementById("searchbar").value = speechToText;
    search();
  }
}

function randomChoice(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

function showImages(res) {
  var newDiv = document.getElementById("images");
  if(typeof(newDiv) != 'undefined' && newDiv != null){
    while (newDiv.firstChild) {
      newDiv.removeChild(newDiv.firstChild);
    }
  }
  console.log(res);
  var img_urls = res.messages[0].array.labels;
  for (var i = 0; i < img_urls.length; i++) {
    console.log(img_urls[i]);
    var newDiv = document.getElementById("images");
    var newImg = document.createElement("img");
    newImg.src = img_urls[i];
    newDiv.appendChild(newImg);

  }
}

function search() {
  var searchTerm = document.getElementById("searchbar").value;
  var apigClient = apigClientFactory.newClient({ apiKey: "q3F3bw7AJW92Z6vxzsia4BKxiU00rRJmhOJWtad0" });

  var params = {
    "q": searchTerm
  };
  
  console.log(searchTerm);
  apigClient.searchGet(params, {}, {})
    .then(function (result) {
      console.log('successfully searched');
      showImages(result.data);
    }).catch(function (result) {
      console.log(result);
    });
}



const realFileBtn = document.getElementById("realfile");
console.log(realFileBtn);

function upload() {
  realFileBtn.click(); 
}

function uploadFile(input) {
  var files = input.files[0];
  var labelFile = document.getElementById("label").value;
  if (labelFile.length == 0) { // set the label to be filename if there's no label input
    fileExt = files.name.split(".").pop().toLowerCase();
    console.log(fileExt)
    console.log(files.name.split(".")[0])
    if (fileExt == 'jpg' || fileExt == 'jpeg' || fileExt == 'png') {
      labelFile = files.name.split(".")[0]
    }
  }
  console.log(files)
  let config = {
    headers:{
      "Content-Type": files.type, 
      "x-api-key": "uDtH3PnyXe9kF82d85Eoh1BRBsMTa0CxiAOOrC8h", 
      "x-amz-meta-customLabels": labelFile
    }
  };
  console.log(config)

  url = 'https://5kdkukz2og.execute-api.us-east-1.amazonaws.com/test2/6998-hw2-b2/' + files.name
  axios.put(url,files,config).then(response=>{
    console.log(response)
    console.log("Upload successfully!");
    window.alert("Upload successfully!");
  })
  
}
