var name = ''
var encoded = null
var fileExt = null
var apigClient = apigClientFactory.newClient()


// Encode picture to base 64_________SEE IF I NEED TO ENCODE
function ViewFile(input) {
  var reader = new FileReader()
  file = input.files[0]
  fileExt = input.files[0].name.split(".").pop()

  reader.onload = function (e) {
    var src = e.target.result
    var newImage = document.createElement("img")
    newImage.src = src
    encoded = newImage.outerHTML
  }
  reader.readAsDataURL(input.files[0])
}


function UploadFile() {
  var customLabels = document.getElementById('custom-labels').value //apple, orange
  console.log(customLabels)
  var filePath = document.getElementById('file_path').value //C:\fakepath\me.png
  document.getElementById('file_path').value = ""
  if ((filePath == "") || (!['png', 'jpg', 'jpeg'].includes(fileExt))) {
    alert("Please upload a valid PNG/JPG file")
  } else {
    var params = {
      bucket: 'photophotobucket',
      key: filePath.split("\\").slice(-1)[0],
      'x-amz-meta-customLabels': customLabels
    };
    var body = btoa(file)
    var additionalParams = {
      headers: {
        'x-api-key': 'MxJvWb9Rlf3gkMM4aJkRXa4YLnRAY0MU52BuFexS',
        'Content-Type': file.type
      },
      queryParams: {}
    };
    return apigClient.uploadBucketKeyPut(params, body, additionalParams)
      .then(function (result) {
        console.log("DEBUG: not error result")
        console.log(result)
        alert("Successfully uploaded the image!")
      })
      .catch(function (error) {
        console.log("DEBUG: error result")
        console.log(error)
      })
  }
}




function TextSearch() {
  var searchTerm = document.getElementById("searcher").value.trim().toLowerCase()
  console.log("DEBUG searchTerm:", searchTerm) //string of what I typed in
  if (searchTerm == "") {
    alert("Please enter valid text");
  } else {
    $('#answer2').html("You are searching for: " + searchTerm).css("color", "green")
    document.getElementById('searcher').value = searchTerm // putting the trim lowercase in the value
    SendMessageBot(searchTerm)
  }
}

function VoiceSearch() {
  var searchTerm = document.getElementById("transcript").value.trim().toLowerCase()
  console.log("DEBUG searchTerm:", searchTerm) //string of what I typed in
  if (searchTerm == "") {
    alert("Please enter valid text");
  } else {
    $('#answer2').html("You are searching for: " + searchTerm).css("color", "green")
    document.getElementById('transcript').value = searchTerm // putting the trim lowercase in the value
    SendMessageBot(searchTerm)
  }
}

function SendMessageBot(searchTerm) {
  document.getElementById('output-box').innerHTML = "" //need to see what to do with this // this is where the output pops up
  var searchResults = []
  var params = {
    'q': searchTerm
  }
  var body = {}
  var additionalParams = {
    headers: {
      'x-api-key': 'MxJvWb9Rlf3gkMM4aJkRXa4YLnRAY0MU52BuFexS'
    }
  }

  return apigClient.searchGet(params, body, additionalParams)
    .then(function (result) {
      var responsedata = result.data.results.keywords.join(', ')
      $('#answer5').html("The main keywords are: " + responsedata).css("color", "blue")

      result.data.results.ids.forEach((element) => {
        searchResults.push(element)
      })
      searchResults.forEach((element) => {
        var imageHTML = "<img src=\"" + element + "\" width=\"50%\" height=\"50%\" style=\"border-radius: 10px\">"
        console.log(imageHTML)
        document.getElementById('output-box').innerHTML += imageHTML
      })
      if (searchResults.length == 0) {
        $('#answer6').html("No image to RETURN!").css("color", "red")
      }
    })
    .catch(function (error) {
      console.log("DEBUG: error result")
      console.log(error)
      alert("Something went Wrong!")
    })
}